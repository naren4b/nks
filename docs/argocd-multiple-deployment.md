```bash
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

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
argocd repo add https://argoproj.github.io/argo-helm --type helm --name argo

context=$(kubectl config get-contexts -o name)
argocd cluster add $context | echo 'y'


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
