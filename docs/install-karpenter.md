https://repost.aws/knowledge-center/eks-install-karpenter

# Step 1. Setup Environment 
```
export KARPENTER_VERSION=v0.29.2 #todo change


export AWS_PARTITION="aws" 
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export TEMPOUT=$(mktemp)


export CLUSTER_NAME=your-cluster-name
export CLUSTER_ENDPOINT="$(aws eks describe-cluster --name ${CLUSTER_NAME} --query "cluster.endpoint" --output text)"

# Check 
echo KARPENTER_VERSION:$KARPENTER_VERSION

echo AWS_DEFAULT_REGION:$AWS_DEFAULT_REGION
echo AWS_ACCOUNT_ID:$AWS_ACCOUNT_ID
echo AWS_PARTITION:$AWS_PARTITION
echo TEMPOUT:$TEMPOUT

echo CLUSTER_NAME:$CLUSTER_NAME 
echo CLUSTER_ENDPOINT:$CLUSTER_ENDPOINT

```
# Step 2. Create IAM roles for Karpenter and the Karpenter controller 
ref: https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html


### 2.1. KarpenterInstanceNodeRole 
```
AmazonEKSWorkerNodePolicy
AmazonEKS_CNI_Policy
AmazonEC2ContainerRegistryReadOnly
AmazonSSMManagedInstanceCore
```

### 2.2 KarpenterControllerRole
#### 2.2.1 policy file 
```
echo '{
    "Statement": [
        {
            "Action": [
                "ssm:GetParameter",
                "iam:PassRole",
                "ec2:DescribeImages",
                "ec2:RunInstances",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeLaunchTemplates",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeInstanceTypeOfferings",
                "ec2:DescribeAvailabilityZones",
                "ec2:DeleteLaunchTemplate",
                "ec2:CreateTags",
                "ec2:CreateLaunchTemplate",
                "ec2:CreateFleet",
                "ec2:DescribeSpotPriceHistory",
                "pricing:GetProducts"
            ],
            "Effect": "Allow",
            "Resource": "*",
            "Sid": "Karpenter"
        },
        {
            "Action": "ec2:TerminateInstances",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/Name": "*karpenter*"
                }
            },
            "Effect": "Allow",
            "Resource": "*",
            "Sid": "ConditionalEC2Termination"
        }
    ],
    "Version": "2012-10-17"
}' > controller-policy.json
```
#### 2.2.  Apply the policy
```
aws iam create-policy --policy-name KarpenterControllerPolicy-${CLUSTER_NAME} --policy-document file://controller-policy.json
```

### 2.3. Create an IAM OIDC identity provider for your cluster using this eksctl command
ref: https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html
```
```
### 2.4.  Create the IAM role for Karpenter Controller using the eksctl command. Associate the Kubernetes Service Account and the IAM role using IRSA.
```
eksctl create iamserviceaccount \
  --cluster "${CLUSTER_NAME}" --name karpenter --namespace karpenter \
  --role-name "KarpenterControllerRole-${CLUSTER_NAME}" \
  --attach-policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/KarpenterControllerPolicy-${CLUSTER_NAME}" \
  --role-only \
  --approve
```


# Step 3. Add tags to subnets and security groups

### 3.1. Add tags to node group subnets so that Karpenter knows the subnets to use.
```
# Check 
for NODEGROUP in $(aws eks list-nodegroups --cluster-name ${CLUSTER_NAME} \
    --query 'nodegroups' --output text); do echo aws ec2 create-tags \
        --tags "Key=karpenter.sh/discovery,Value=${CLUSTER_NAME}" \
        --resources $(aws eks describe-nodegroup --cluster-name ${CLUSTER_NAME} \
        --nodegroup-name $NODEGROUP --query 'nodegroup.subnets' --output text )
done

# Check 
for NODEGROUP in $(aws eks list-nodegroups --cluster-name ${CLUSTER_NAME} \
    --query 'nodegroups' --output text); do aws ec2 create-tags \
        --tags "Key=karpenter.sh/discovery,Value=${CLUSTER_NAME}" \
        --resources $(aws eks describe-nodegroup --cluster-name ${CLUSTER_NAME} \
        --nodegroup-name $NODEGROUP --query 'nodegroup.subnets' --output text )
done

```

### 3.2. Add tags to security groups.
The following commands add tags only to the security groups of the first node group. 
If you have multiple node groups or multiple security groups, you must decide the security group that Karpenter will use

```
NODEGROUP=$(aws eks list-nodegroups --cluster-name ${CLUSTER_NAME} --query 'nodegroups[0]' --output text)
 
LAUNCH_TEMPLATE=$(aws eks describe-nodegroup --cluster-name ${CLUSTER_NAME} \
    --nodegroup-name ${NODEGROUP} --query 'nodegroup.launchTemplate.{id:id,version:version}' \
    --output text | tr -s "\t" ",")
 
# If your EKS setup is configured to use only Cluster security group, then please execute -
 
SECURITY_GROUPS=$(aws eks describe-cluster --name ${CLUSTER_NAME} --query cluster.resourcesVpcConfig.clusterSecurityGroupId | tr -d '"')
 
# If your setup uses the security groups in the Launch template of a managed node group, then :
 
SECURITY_GROUPS=$(aws ec2 describe-launch-template-versions \
    --launch-template-id ${LAUNCH_TEMPLATE%,*} --versions ${LAUNCH_TEMPLATE#*,} \
    --query 'LaunchTemplateVersions[0].LaunchTemplateData.[NetworkInterfaces[0].Groups||SecurityGroupIds]' \
    --output text)
 
aws ec2 create-tags \
    --tags "Key=karpenter.sh/discovery,Value=${CLUSTER_NAME}" \
    --resources ${SECURITY_GROUPS}
```

# Step 4. Update aws-auth ConfigMap
### 4.1. Update the aws-auth ConfigMap in the cluster to allow the nodes that use the KarpenterInstanceNodeRole IAM role to join the cluster. Run the following command:
```
kubectl edit configmap aws-auth -n kube-system
```

### 4.2. Add a section to mapRoles that looks similar to this example:    
Note: Replace the ${AWS_ACCOUNT_ID} variable with your account, but don't replace {{EC2PrivateDNSName}}.
```
- groups:
  - system:bootstrappers
  - system:nodes
  rolearn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/KarpenterInstanceNodeRole
  username: system:node:{{EC2PrivateDNSName}}
```

# Step 5. Install Karpenter , Set nodeAffinity
```
helm template karpenter oci://public.ecr.aws/karpenter/karpenter --version ${KARPENTER_VERSION} --namespace karpenter \
    --set settings.aws.defaultInstanceProfile=KarpenterInstanceProfile \
    --set settings.aws.clusterEndpoint="${CLUSTER_ENDPOINT}" \
    --set settings.aws.clusterName=${CLUSTER_NAME} \
    --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="arn:aws:iam::${AWS_ACCOUNT_ID}:role/KarpenterControllerRole-${CLUSTER_NAME}" > karpenter.yaml


affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: karpenter.sh/provisioner-name
          operator: DoesNotExist
      - matchExpressions:
        - key: eks.amazonaws.com/nodegroup
          operator: In
          values:
          - ${NODEGROUP}


kubectl create namespace karpenter
kubectl create -f https://raw.githubusercontent.com/aws/karpenter/${KARPENTER_VERSION}/pkg/apis/crds/karpenter.sh_provisioners.yaml
kubectl create -f https://raw.githubusercontent.com/aws/karpenter/${KARPENTER_VERSION}/pkg/apis/crds/karpenter.k8s.aws_awsnodetemplates.yaml
kubectl apply -f karpenter.yaml
		  
```

# Step 6.  Create sample Provisioner & AWSNodeTemplate
```
cat <<EOF | kubectl apply -f -
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: default
spec:
  requirements:
    - key: karpenter.k8s.aws/instance-category
      operator: In
      values: [c, m, r]
    - key: karpenter.k8s.aws/instance-generation
      operator: Gt
      values: ["2"]
  providerRef:
    name: default
  ttlSecondsAfterEmpty: 30
---
apiVersion: karpenter.k8s.aws/v1alpha1
kind: AWSNodeTemplate
metadata:
  name: default
spec:
  subnetSelector:
    karpenter.sh/discovery: "${CLUSTER_NAME}"
  securityGroupSelector:
    karpenter.sh/discovery: "${CLUSTER_NAME}"
EOF
```


# Step 7. Keep reserved nodes for the critial services 
```
aws eks update-nodegroup-config --cluster-name ${CLUSTER_NAME} \
    --nodegroup-name ${NODEGROUP} \
    --scaling-config "minSize=2,maxSize=2,desiredSize=2"
```

# Step 8. Check the karpenter logs 
```

kubectl logs -f -n karpenter -c controller -l app.kubernetes.io/name=karpenter

```
