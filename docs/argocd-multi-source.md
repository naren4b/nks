![misc-Copy of Multiple ArgoCD Source](https://github.com/naren4b/nks/assets/3488520/6e8cd133-7b90-4fbb-a76c-9d6ddf359a44)

# Multiple Sources for an ArgoCD Application

ref: Argo CD has the ability to specify multiple sources for a single Application. Argo CD compiles all the sources and reconciles the combined resources. 
(argocd-multi-sources)[https://argo-cd.readthedocs.io/en/stable/user-guide/multiple_sources/]



# Install ArgoCD
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl patch deployments.apps -n argocd  argocd-server  \
--type=json \
-p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--insecure"}]'

```

# Install argocd CLI
```bash
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```

# ArgoCD CLI login 
```bash
kubectl get secrets -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo 
kubectl port-forward service/argocd-server -n argocd 8080:443 &
argocd login localhost:8080  --insecure
```

# Add Git repo
```bash
USERNAME=npanda
TOKEN=hello

# Add Template Repo
REPO_URL=https://github.com/naren4b/demo-app.git
argocd repo add ${REPO_URL} --username ${USERNAME} --password ${TOKEN}

# ADD Value Repo
REPO_URL=https://github.com/naren4b/argocd-multi-source-demo.git
argocd repo add ${REPO_URL} --username ${USERNAME} --password ${TOKEN}
```

![Repos-added](https://github.com/naren4b/argocd-multi-source-demo/blob/main/res/image.png)

# Deploy the App 
```bash
git clone https://github.com/naren4b/argocd-multi-source-demo.git
kubectl  apply -f dev-demo-argo-application.yaml -f staging-demo-argo-application.yaml
```

# Check the manifest file & match with the values given 
```
kubectl get cm -n demo-dev demo -o jsonpath="{.data.env}" && echo 
kubectl get cm -n demo-staging demo -o jsonpath="{.data.env}" && echo 
```
![argo-apps](https://github.com/naren4b/argocd-multi-source-demo/blob/main/res/image-1.png)


# To check the templating is OK before applying

```bash
cat <<EOF >my-app.yaml
project: default
destination:
  server: 'https://kubernetes.default.svc'
  namespace: demo-dev
sources:
  - repoURL: 'https://github.com/naren4b/demo-app.git'
    path: helm-chart
    targetRevision: main
    helm:
      valueFiles:
        - $values/env/dev-values.yaml
  - repoURL: 'https://github.com/naren4b/argocd-multi-source-demo.git'
    targetRevision: main
    ref: values

EOF
```

# Test the ArgoCD Application

```bash
wget https://raw.githubusercontent.com/naren4b/argocd-multi-source-demo/main/decodeArgoApp.py
python decodeArgoApp.py --app my-app --dry-run=true # for full execution --dry-run=false
```
