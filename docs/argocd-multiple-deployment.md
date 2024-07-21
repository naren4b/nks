# Controlling Multiple individual Kubernetes Cluster through Multiple ArgoCD Fleet(Scale and Automation)
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)

# Setup Central Argocd 

#### 1. Install Root ArgoCD via Helm install
ref: [Install Argocd to standalon kubernetes cluster](https://gist.github.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e)
```bash
curl -oS https://gist.githubusercontent.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e/raw/a7e41fac2cf5170186fff2a759c2e08fc94cf3dd/install-argocd.sh
bash install-argocd.sh
```
#### 2. Add git repo credentials - declaratively(Optional) 
ref: [Repository credentials, for using the same credentials in multiple repositories.](https://gist.github.com/naren4b/fae65efb90998cb46a3c9ebed16df880)
```
curl -oS https://gist.githubusercontent.com/naren4b/fae65efb90998cb46a3c9ebed16df880/raw/443682b34a4a5bc6a212cca93cd41e32873f2eb2/create-https-repo-creds-secret.sh
vi create-https-repo-creds-secret.sh
bash create-https-repo-creds-secret.sh
```
#### 3. Add cluster credentials - declaratively(Otional)
ref: [Register A Cluster ](https://gist.github.com/naren4b/4af945b244f60d801ca77227cdeda861)
```bash
curl -Os https://gist.githubusercontent.com/naren4b/4af945b244f60d801ca77227cdeda861/raw/a0b28af2e06caaa7806953afdcb171278fe714e7/create-cluster-secret.sh 
bash create-cluster-secret.sh 
```
##### 4. Create Argocd Application Deploy 

```bash
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




