# Setting up ArgoCD in k8s cluster with local User & RBAC 
![argocd-rbac](https://user-images.githubusercontent.com/3488520/204094103-33ed7434-efe4-489b-afc5-c4971ef37d90.jpg)




### Install the argocd
```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Install the Argocd CLI
```
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```
### Access the argocd 
```
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
argocd login localhost:8080  --insecure
argocd account update-password 
```
### Set up default policy,role
```
kubectl patch -n argocd cm argocd-cm --patch='{"data":{"policy.default": "role:readonly" }}'
kubectl patch -n argocd cm argocd-rbac-cm --patch='{"data":{"policy.default": "role:readonly" }}'

```

### Create a local user 
```
username=naren
newpassword=newpassword
curentpassword=curentpassword

kubectl patch -n argocd cm argocd-cm --patch='{"data":{"accounts.${username}": "apikey,login" }}'
argocd account list 
argocd account update-password  --current-password=${curentpassword} --new-password=${newpassword} --account=${username}

```
![image](https://user-images.githubusercontent.com/3488520/204011839-a2d042b0-0f8e-4864-803a-97753443432d.png)
![image](https://user-images.githubusercontent.com/3488520/204012094-354261a1-bf4a-4bf9-be46-30a17c41b06e.png)

ws: https://killercoda.com/kubernetes/scenario/a-playground

