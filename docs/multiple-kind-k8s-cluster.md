# Installing multiple kind cluster in a single host 
![multi-docker-kind-k8s-cluster drawio](https://github.com/user-attachments/assets/81cfcc7d-94be-47ef-afc1-138393131079)


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

kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./config 
kind get kubeconfig --name=${clusterName} | sed "s|https://0.0.0.0|https://${clusterName}-control-plane|g"  | sed "s/${apiServerPort}/6443/g"  > ${clusterName}-config
```
![image](https://github.com/user-attachments/assets/8e34ff8b-34b1-4d07-9cf5-9adcafa89dab)

# Deploy Test pod 
```
kubectl apply -f https://gist.githubusercontent.com/naren4b/76e8a281b259d8de5d8a5bfa830e3840/raw/f8f203c63f476c831bceb9b74939cccece42e82a/swiss-knife.yaml
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
kubectl  cp ${clusterName}-config swiss-knife:/
kubectl exec swiss-knife -- kubectl cluster-info --kubeconfig=${clusterName}-config 
```
