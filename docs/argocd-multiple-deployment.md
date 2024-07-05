# Handling Multiple ArgoCD Manage 1000 of individual Kubernetes Cluster
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)


## At the Control Plan (Admin Bay)
### Install argocd cli
```bash
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```
### Install Argocd to standalon kubernetes cluster
```bash
helm repo add argo https://argoproj.github.io/argo-helm
cat<<EOF >argocd-values.yaml 
configs:
  params:
    server.insecure: true
EOF
helm upgrade --install root argo/argo-cd -n argocd -f argocd-values.yaml  --create-namespace 
kubectl wait --for=condition=Ready -n argocd pod -l  app.kubernetes.io/name=argocd-server
nohup kubectl port-forward service/root-argocd-server -n argocd 8080:443 --address 0.0.0.0  &
password=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
argocd login localhost:8080 --username admin --password $password  | echo 'y'
```

# How to git Repo to ArgoCD
```bash
argocd repo add https://argoproj.github.io/argo-helm --type helm --name argo
```
# How to add Clusters to ArgoCD
```bash
context=$(kubectl config get-contexts -o name)
argocd cluster add $context | echo 'y'
```
# Regional Argocd Application Template 
```bash
zone=us
cat<<EOF > ${zone}-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${zone}-zone-argocd
  namespace: argocd 
spec:
  project: default 
  source:
    chart: argo-cd
    repoURL: https://argoproj.github.io/argo-helm
    targetRevision: 7.3.4 
    helm:
      releaseName: ${zone}-zone-argocd
  destination:
    server: "https://kubernetes.default.svc"
    namespace: ${zone}
EOF
kubectl create ns $zone
kubectl apply -f ${zone}-application.yaml
```
