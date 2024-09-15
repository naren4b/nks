# 🦭Step-by-Step Guide to Setting Up Multiple Kind Clusters on a Single Host🦭

![multi-docker-kind-k8s-cluster drawio](https://github.com/user-attachments/assets/81cfcc7d-94be-47ef-afc1-138393131079)
#### Guide to Creating Kubernetes Clusters Using Kind and Podman
#### Setup the host
kind version: v0.24.0
kubernetes Version: v1.31.0

Install KIND
```
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
Pre Load the image
```
podman  pull docker.io/kindest/node:v1.31.0@sha256:53df588e04085fd41ae12de0c3fe4c72f7013bba32a20e7325357a1ac94ba865
```
- ref: https://github.com/kubernetes-sigs/kind/tags
- ref: https://kind.sigs.k8s.io/docs/user/quick-start/

#### Install the org-control-plane kind cluster 
```bash
export KIND_EXPERIMENTAL_PROVIDER=podman
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

kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./kubeconfig
cat kubeconfig | sed "s|https://:${apiServerPort}|https://0.0.0.0:${apiServerPort}|g"  > ./config
kind get kubeconfig --name=${clusterName} | sed "s|https://:${apiServerPort}|https://${clusterName}-control-plane:6443|g"  > ${clusterName}-config

```
![image](https://github.com/user-attachments/assets/8e34ff8b-34b1-4d07-9cf5-9adcafa89dab)


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

kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./kubeconfig
cat kubeconfig | sed "s|https://:${apiServerPort}|https://0.0.0.0:${apiServerPort}|g"  > ./config
kind get kubeconfig --name=${clusterName} | sed "s|https://:${apiServerPort}|https://${clusterName}-control-plane:6443|g"  > ${clusterName}-config

```

# Copy the kubeconfig 
```
kubectl config use-context kind-$ORG_CONTROL_PLANE_K8S
kubectl run test --image=docker.io/alpine -- sleep infinte
clusterName=edge-1
kubectl  cp ${clusterName}-config test:/config
kubectl exec -it test sh
apk add curl
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.28.3/2023-11-14/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv kubectl /usr/local/bin
kubectl cluster-info --kubeconfig=config
 
```
![image](https://github.com/user-attachments/assets/1502199c-f0aa-4ae1-809d-85d1464c9b78)

