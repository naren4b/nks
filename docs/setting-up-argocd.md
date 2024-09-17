# Setup Argocd with extra cluster and git integrated 
## Create `Main` Cluster
Setup the Data 
```bash
export ORG_CONTROL_PLANE_K8S=main
clusterName=$ORG_CONTROL_PLANE_K8S
kind delete cluster --name=${clusterName}
apiServerPort=6443
```
Prepare the cluster-config
```
cat << EOF > ${clusterName}-cluster-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${clusterName}
networking:
 apiServerAddress: "0.0.0.0"
 apiServerPort: $apiServerPort
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 443
    hostPort: 443
    listenAddress: "0.0.0.0"
  - containerPort: 80
    hostPort: 80
    listenAddress: "0.0.0.0"
EOF
kind create cluster --config ${clusterName}-cluster-config.yaml --kubeconfig ./kubeconfig
cat kubeconfig | sed "s|https://:${apiServerPort}|https://0.0.0.0:${apiServerPort}|g"  > ./config
kind get kubeconfig --name=${clusterName} | sed "s|https://:${apiServerPort}|https://${clusterName}-control-plane:6443|g"  > ${clusterName}-config
```
#### Install Ingress Controller `haproxy`
```bash
helm repo add haproxy-ingress https://haproxy-ingress.github.io/charts
helm upgrade --install ingress haproxy-ingress/haproxy-ingress -n ingress-controller --create-namespace --set controller.hostNetwork=true --set controller.ingressClassResource.enabled=true

export DOMAIN=10.157.53.176.nip.io
export INGRESS_CLASS=haproxy
```
#### Install ArgoCD and Argocd Ingress 
```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
cat<<EOF >argocd-values.yaml
configs:
  params:
    server.insecure: true
EOF
helm upgrade --install root argo/argo-cd -n argocd -f argocd-values.yaml  --create-namespace
kubectl wait --for=condition=Ready -n argocd pod -l  app.kubernetes.io/name=argocd-server
#kubectl create ingress argocd --rule="argocd.${DOMAIN}/=root-argocd-server:8080" -n argocd 
ARGOCDURL=argocd.${DOMAIN} 
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
  name: argocd
  namespace: argocd
spec:
  ingressClassName: haproxy
  rules:
  - host: $ARGOCDURL
    http:
      paths:
      - backend:
          service:
            name: root-argocd-server
            port:
              number: 443
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - $ARGOCDURL
EOF
```
#### Add git repo 
Prepare the values
```bash
export MY_GIT_NAME={name}
export MY_GIT_USER={user}
export MY_GIT_TOKEN={token}
export MY_GIT_URL={url}
```
Apply the Secret
```bash
cat<<EOF | kubectl create -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${MY_GIT_NAME}-https-creds
  namespace: argocd
  labels:
   argocd.argoproj.io/secret-type: repo-creds
stringData:
  type: git
  url: ${MY_GIT_URL}
  username: ${MY_GIT_USER}
  password: ${MY_GIT_TOKEN}
EOF
```
Check the Repo https://argocd.127.0.0.1.nip.io/settings/repos
![image](https://github.com/user-attachments/assets/4111947f-4911-4c9f-b537-082441d5692b)

## Create `Edge` Cluster
Setup the data 
```bash
clusterName=edge-1 #Change me
kind delete cluster --name=${clusterName}
apiServerPort=6444 # change me
```
Create the cluster 
```
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
#### Create The Service Account `argocd`
```bash
# Connect to EDGE cluster
#!/bin/bash
echo "Create the Service Account"
kubectl create sa argocd-manager -n kube-system
cat<<EOF | kubectl create -f - 
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: argocd-manager
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: "argocd-manager"
EOF
```
#### Create Cluster Role Binding `argocd-cluster-admin` 
```bash
# Note Cluster Admin is a full permission (we can check alternative https://github.com/argoproj/argo-cd/issues/5389)
echo "Create the rolebinding"
kubectl create clusterrolebinding --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager argocd-manager-role
```
Collect the information
```
caData=$(kubectl config view --raw -o jsonpath="{.clusters[0].cluster.certificate-authority-data}")
token=$(kubectl create token argocd-manager -n kube-system --duration=9999h)
server=$(kubectl config view --raw -o jsonpath="{.clusters[0].cluster.server}")
name=$(kubectl config view --raw -o jsonpath="{.clusters[0].name}")
```
# Connect extra cluster and deploy application
```bash
kubectx main
```
#### Add the EDGE cluster 
```bash
cat<<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${name}-cluster-secret
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: ${name}
  server: ${server}
  config: |
    {
      "bearerToken": "${token}",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "${caData}"
      }
    }
EOF
```
Check https://argocd.127.0.0.1.nip.io/settings/clusters
![image](https://github.com/user-attachments/assets/2be62844-3d66-4214-9329-f518ec1e6087)

#### Deploy the Demo Argocd Application 
```bash
SERVER=$1 #"https://edge-1-control-plane:6443"
```
Deploy the application
```bash
cat<<EOF | kubectl apply  -n argocd -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: 'demo-app'
spec:
  destination:
    server: $SERVER
    namespace: default
  source:
    path: sample-app
    repoURL: https://github.com/naren4b/demo-app.git
    targetRevision: HEAD  
  project: default
  syncPolicy:
    automated: {}
EOF
```
![image](https://github.com/user-attachments/assets/0b765e66-f3e8-4a04-a848-6910283b8753)
