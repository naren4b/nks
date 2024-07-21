# Controlling Multiple individual Kubernetes Cluster through Multiple ArgoCD Fleet(Scale and Automation)
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)

# A: For Each SCM(git) Repo 
==============
1. Create access Token for the User(RO) 
2. Create Repo Secret (this will be refered Central Argocd/Step-2, Zone ArgoCD/Step-2)
3. [My-App Helm Chart Repo ](https://github.com/naren4b/argo-cd/tree/main/demo-applications/myapp)
    - My Application Menifests 
4. Central Argocd Helm Chart Repo
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
ref: [Install Argocd to standalon kubernetes cluster](https://gist.github.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e)
```bash
curl -oS https://gist.githubusercontent.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e/raw/a7e41fac2cf5170186fff2a759c2e08fc94cf3dd/install-argocd.sh
bash install-argocd.sh
```
#### 2. Create Cluster Secret or Configure in the Value file of
Check [Appendix](https://github.com/naren4b/nks/edit/main/docs/argocd-multiple-deployment.md#appendix) for Manual creation 
#### 3. Create and Apply git repo secret (ref: A.1 & A.2)
Check [Appendix](https://github.com/naren4b/nks/edit/main/docs/argocd-multiple-deployment.md#appendix) for Manual creation 
##### 4. Create Argocd Application Deploy A.5 Helm 
```
cat<<EOF | kubectl create -f -
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
ref: [Repository credentials, for using the same credentials in multiple repositories.](https://gist.github.com/naren4b/fae65efb90998cb46a3c9ebed16df880)
```
curl -oS https://gist.githubusercontent.com/naren4b/fae65efb90998cb46a3c9ebed16df880/raw/443682b34a4a5bc6a212cca93cd41e32873f2eb2/create-https-repo-creds-secret.sh
vi create-https-repo-creds-secret.sh
bash create-https-repo-creds-secret.sh
```

#### 2. Declaratively Adding a cluster
ref: [Register A Cluster ](https://gist.github.com/naren4b/4af945b244f60d801ca77227cdeda861)
```bash
curl -Os https://gist.githubusercontent.com/naren4b/4af945b244f60d801ca77227cdeda861/raw/a0b28af2e06caaa7806953afdcb171278fe714e7/create-cluster-secret.sh 
bash create-cluster-secret.sh 
```



