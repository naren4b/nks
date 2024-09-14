# Installing multiple kind cluster in a single host 


#### Install the org-control-plane kind cluster 
```bash
export ORG_CONTROL_PLANE_K8S=org

clusterName=$ORG_CONTROL_PLANE_K8S
kind delete cluster --name=${clusterName}

apiServerPort=6443
cat << EOF > ${clusterName}-cluster-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${clusterName}
networking:
 apiServerAddress: "0.0.0.0"
 apiServerPort: $apiServerPort
nodes:
- role: control-plane
EOF

kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./config 
kind get kubeconfig --name=${clusterName} | sed "s|https://0.0.0.0|https://${clusterName}-control-plane|g"  | sed "s/${apiServerPort}/6443/g"  > ${clusterName}-config
```
#### Setup a test Docker Image 
```
cat<<EOF > Dockerfile
FROM alpine
RUN apk add curl

ENTRYPOINT ["/bin/sh","-c","sleep infinity"]
EOF
docker build -t alpine-sleeper:1 .
```
#### Load the image to KIND Node 
```
kind load docker-image alpine-sleeper:1 --name=${clusterName}
````

#### Deploy a test pod 
```
k run test --image=alpine-sleeper:1
```
#### Setup the test pod 
```bash
cat<<EOF > setup.sh
mkdir ~/.kube
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.28.3/2023-11-14/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/
alias k=kubectl
EOF
k cp setup.sh test:/
k exec test sh setup.sh
```

# Copy the kubeconfig
```bash
clusterName=$ORG_CONTROL_PLANE_K8S
k cp ${clusterName}-config test:/
k exec test -- kubectl cluster-info --kubeconfig=${clusterName}-config 
```
# Setup the EDGE k8s clusters
```bash
clusterName=edge-1 #Change me
kind delete cluster --name=${clusterName}
apiServerPort=6444 # change me
cat << EOF > ${clusterName}-cluster-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${clusterName}
networking:
 apiServerAddress: "0.0.0.0"
 apiServerPort: $apiServerPort
nodes:
- role: control-plane
EOF

kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./config 
kind get kubeconfig --name=${clusterName} | sed "s|https://0.0.0.0|https://${clusterName}-control-plane|g" |  sed "s/${apiServerPort}/6443/g"  > ${clusterName}-config
```

# Copy the kubeconfig 
```
kubectl config use-context kind-$ORG_CONTROL_PLANE_K8S
clusterName=edge-1
k  cp ${clusterName}-config test:/
k exec test -- kubectl cluster-info --kubeconfig=${clusterName}-config 
```
