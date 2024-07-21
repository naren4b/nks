# Controlling Multiple individual Kubernetes Cluster through Multiple ArgoCD Fleet(Scale and Automation)
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)

# Setup Central Argocd 

#### 1. Install Root ArgoCD via Helm install
ref: [Install Argocd to standalon kubernetes cluster](https://gist.github.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e)
```bash
curl -sO https://gist.githubusercontent.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e/raw/3a35d8d083203d7203f58c286398b6cd3a656b7d/install-argocd.sh
bash install-argocd.sh
```
#### 2. Add git repo credentials - declaratively(Optional) 
ref: [Repository credentials, for using the same credentials in multiple repositories.](https://gist.github.com/naren4b/fae65efb90998cb46a3c9ebed16df880)
```
# export MY_GIT_TOKEN={token}
curl -sO https://gist.githubusercontent.com/naren4b/fae65efb90998cb46a3c9ebed16df880/raw/443682b34a4a5bc6a212cca93cd41e32873f2eb2/create-https-repo-creds-secret.sh
# vi create-https-repo-creds-secret.sh
bash create-https-repo-creds-secret.sh
```
#### 3. Add cluster credentials - declaratively(Otional)
ref: [Register A Cluster ](https://gist.github.com/naren4b/4af945b244f60d801ca77227cdeda861)
```bash
curl -sO https://gist.githubusercontent.com/naren4b/4af945b244f60d801ca77227cdeda861/raw/c83902c8b9644f225764d2b4890ef9b8d917470d/create-cluster-secret.sh
bash create-cluster-secret.sh 
```
##### 4. Create Argocd Application Deploy 

```bash
cat<<EOF | kubectl apply -f -
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
  syncPolicy:
    automated:
      allowEmpty: true
      selfHeal: true
EOF
```

#### To Check  zone Argocd
```
kubectl -n in-cluster-zone-argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
nohup kubectl port-forward -n in-cluster-zone-argocd svc/in-cluster-zone-argocd-server 5000:80 --address 0.0.0.0 &
```



