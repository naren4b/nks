#!/bin/bash

##############################################################
# Usage: bash addk8suser.sh <name> <cluster-role> <duration> #
# example: bash addk8suser.sh npanda cluster-admin 86400000  #
##############################################################



username="${1:-my-user}"
group="${2:-view}"
expirationSeconds="${3:-86400}"
role="${2:-edit}"
mkdir ${username}
cd ${username}

echo "INPUT : bash addk8suser.sh  $username $role $expirationSeconds"

openssl genrsa -out ${username}.key 2048
openssl req -new -key ${username}.key -out ${username}.csr -subj "/CN=${username}/O=${group}"
openssl req -in ${username}.csr -noout -text

echo "INFO: CERTIFICATES created..."

cat <<EOF >${username}.yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: ${username}
spec:
  request: $(cat ${username}.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: $expirationSeconds
  usages:
  - client auth
EOF

cat ${username}.yaml

echo "INFO: CSR file created..."

if kubectl auth can-i create clusterrolebinding; then
    echo "Connected to Kubernetes cluster using kubeconfig: $KUBECONFIG"
else
    echo "Not connected to a Kubernetes cluster using kubeconfig: $KUBECONFIG"
    exit 1
fi

if [ ! -e ${username}.yaml ]; then
    echo "CertificateSigningRequest for ${username}.yaml file does not exist."
fi


kubectl apply -f ${username}.yaml
kubectl certificate approve ${username}
kubectl get csr ${username}  -o jsonpath='{.status.certificate}'| base64 -d > ${username}.crt

echo "INFO: CSR approved...."

kubectl create clusterrolebinding ${username}-${role} --user=${username} --clusterrole=${role}

echo list pod -- $(kubectl auth can-i list pod --as ${username})
echo create pod -- $(kubectl auth can-i create pod --as ${username})
echo delete pod -- $(kubectl auth can-i delete pod --as ${username})

ls -lrt

cluster_name=$(cat  $KUBECONFIG | yq -r .clusters[0].name)
cluster_server=$(cat $KUBECONFIG  | yq -r .clusters[0].cluster.server)
cluster_ca=$(cat $KUBECONFIG | yq -r '.clusters[0].cluster."certificate-authority-data"')

cat <<EOF >${username}-kubeconfig
apiVersion: v1
kind: Config
clusters:
- name: $cluster_name
  cluster:
    server: $cluster_server
    certificate-authority-data: $cluster_ca
users:
- name: $username
  user:
    client-certificate-data: $(kubectl get csr ${username}  -o jsonpath='{.status.certificate}')
    client-key-data: $(cat ${username}.key | base64 | tr -d '\n')
contexts:
- context:
    cluster: $cluster_name
    namespace: default
    user: $username
  name: ${username}@${cluster_name}
current-context: ${username}@${cluster_name}
EOF
