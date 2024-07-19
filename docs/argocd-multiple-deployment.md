# Controlling Multiple individual Kubernetes Cluster through ArgoCD Fleet(Scale and Automation)
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)

# A: For Each SCM(git) Repo 
==============
1. Create robot/service account user at SCM
2. Create access Token for the User 
3. Create Repo Secret (this will be refered Central Argocd/Step-2, Zone ArgoCD/Step-2)
4. [My-App Helm Chart Repo ](https://github.com/naren4b/argo-cd/tree/main/demo-applications/myapp)
    - My Application Menifests 
5. Central Argocd Helm Chart Repo
     - zone-cluster-secrets.yaml     
     - zone-argocd-applicationset.yaml
5. Zone Argocd Helm Chart Repo
      - cluster-secrets.yaml
      - my-app-repo-secrets.yaml
      - my-app-argocd-applicationset.yaml   

# B: In Each Cluster Setup
================
1. Create Service Account 
2. Cluster Role
3. Cluster Role Binding
4. Collect Cluster Secrets (this will be refered Central Argocd/Step-1, Zone ArgoCD/Step-1)

# C: Central Argocd 
================
#### 1. Install Root ArgoCD via Helm install
##### Install argocd cli
```bash
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```
##### Install Argocd to standalon kubernetes cluster
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
#### 2. Create Cluster Secret or Configure in the Value file of
Check [Appendix](https://github.com/naren4b/nks/edit/main/docs/argocd-multiple-deployment.md#appendix) for Manual creation 
#### 3. Create and Apply git repo secret (ref: A.1 & A.2)
Check [Appendix](https://github.com/naren4b/nks/edit/main/docs/argocd-multiple-deployment.md#appendix) for Manual creation 
##### 4. Create Argocd Application Deploy A.5 Helm 
```
cat<<EOF >seed-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: seed-application
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/naren4b/argo-cd.git
    targetRevision: HEAD
    path: charts/central-argocd
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
EOF
kubectl apply -f seed-application.yaml
```
# appendix 
## At the Control Plan (Admin Bay)
#### Automation 
```
git clone https://github.com/naren4b/argo-cd.git
cd argo-cd/zone-argocd-deploy-repo
vi values.yaml 
helm install zone-argocds .
```
#### Configure Cluster, Repo , Applications 
```
git clone https://github.com/naren4b/argo-cd.git
cd argo-cd/zone-argocd-configuration-repo
vi values.yaml
git commit -m "Configure other clusters"
git push orgin main 
```


## Manual Setup 
# How to add a git Repo to ArgoCD through argocd CLI
```bash
argocd repo add https://argoproj.github.io/argo-helm --type helm --name argo
```
# How to add a Clusters to ArgoCD through CLI
```bash
context=$(kubectl config get-contexts -o name)
argocd cluster add $context | echo 'y'
```

# Install Regional Argocd Application Template 
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
#### 1. Declaratively adding a git repo 

```bash
gitUrl=https://github.com/naren4b/demo-app.git
gitRepoName=demo-app
gitUserName=naren4b
gitUserToken=${MY_GIT_TOKEN}

cat<<EOF > git-repo-demo-app.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ${gitRepoName}
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: ${gitUrl}
  username: ${gitUserName}
  password: ${gitUserToken}
EOF
kubectl create -f git-repo-demo-app.yaml
```
#### 2. Declaratively Adding a cluster
ref: https://argo-cd.readthedocs.io/en/stable/getting_started/#5-register-a-cluster-to-deploy-apps-to-optional
Connect to the cluster 
```
cat<<EOF > argocd-agent-sa-with-token.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: null
  name: argocd-agent
  namespace: kube-system
---
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: argocd-agent
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: argocd-agent
EOF

kubectl create -f argocd-agent-sa-with-token.yaml

caData=$(kubectl config view --raw -o jsonpath="{.clusters[0].cluster.certificate-authority-data}")
token=$(kubectl get secret argocd-agent -n kube-system -o json | jq -r .data.token)
server=$(kubectl config view --raw -o jsonpath="{.clusters[0].cluster.server}")
name=$(kubectl config view --raw -o jsonpath="{.clusters[0].name}")

cat<<EOF > my-zone-cluster-values.yaml  
clusters:
  ${name}: 
    name: ${name}
    server: ${server}
    caData: ${caData}
    token: ${token}
    insecure: false
	
EOF
# upload it here https://github.com/naren4b/argo-cd/charts/central-argocd/values.yaml
cat<<EOF >my-cluster-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mycluster-secret
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
kubectl apply -f my-cluster-secret.yaml
```
