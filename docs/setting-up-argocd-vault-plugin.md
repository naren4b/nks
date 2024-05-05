# Secret injection using argocd-vault-plugin inside kubernetes cluster 

![image](https://github.com/naren4b/nks/assets/3488520/2c71e8b7-5502-46db-8428-7e9ac0aa7d59)

**Argocd-vault-plugin**:
 This plugin is aimed at helping to solve the issue of secret management with GitOps and Argo CD. We wanted to find a simple way to utilize Vault without having to rely on an operator or custom resource definition. This plugin can be used not just for secrets but also for deployments, configMaps or any other Kubernetes resource.

![image](https://github.com/naren4b/nks/assets/3488520/f3852901-4bbc-466d-828f-54f0b942b0af)

# Install Vault 
```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm install vault hashicorp/vault --set "server.dev.enabled=true"
```
# Configure the Vault
```bash
kubectl exec -it vault-0 sh
```
## Setup the Key-Value in the kubernetes
```bash
vault secrets enable -path=mysecret kv-v2
vault kv put mysecret/database/config username="nks-user" password="nks-secret-password"

# Write out the policy named mysecret that enables the read capability for secrets at path mysecret/data/database/config.
vault policy write mysecret - <<EOF
path "mysecret/data/database/config" {
   capabilities = ["read"]
}
EOF

```
### Enable kubernetes authentication 
```
# Enable the Kubernetes authentication method.
vault auth enable kubernetes

# Configure the Kubernetes authentication method to use the location of the Kubernetes API. (when running inside the cluster)
vault write auth/kubernetes/config \
      kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"


# Create a Kubernetes authentication role named internal-app.
vault write auth/kubernetes/role/argocd-server \
      bound_service_account_names=argocd-server \
      bound_service_account_namespaces=argocd \
      policies=mysecret \
      ttl=24h
exit
```

# Basic Argocd Installation Setupp 
```bash
# Install argocd client
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

# Create the namespace and Install argocd 
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pod -n argocd -w
# edit the deployment for insecure installation in local
#kubectl edit deployments.apps -n argocd argocd-server 
nohup kubectl  port-forward -n argocd svc/argocd-server 8080:443 --address 0.0.0.0 & 

argocd_password=$(kubectl get secrets -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo $argocd_password
argocd login localhost:8080  --insecure --username=admin --password=$argocd_password

argocd repo add https://github.com/naren4b/demo-app.git

argocd app create demo \
     --repo https://github.com/naren4b/demo-app.git \
     --path helm-chart \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default \
     --sync-policy  automated
```
## Integrate the argocd-vault plugin 
Create the plugin behavior 
```
kubectl create -f https://raw.githubusercontent.com/naren4b/demo-app/main/others/cmp-plugin.yaml -n argocd
```
## Inject the vault authentication for the argocd to consume 
```bash
kubectl create secret generic -n argocd argocd-vault-plugin-credentials \
	--from-literal=AVP_TYPE=vault \
	--from-literal=VAULT_ADDR=http://vault-internal.default.svc.cluster.local:8200 \
	--from-literal=AVP_AUTH_TYPE=k8s \
	--from-literal=AVP_K8S_ROLE=argocd-server 
```
## Patch the argocd-repo-server 
```bash
wget https://raw.githubusercontent.com/naren4b/demo-app/main/others/cmp-plugin.yaml
kubectl create -f cmp-plugin.yaml

wget https://raw.githubusercontent.com/naren4b/demo-app/main/others/argocd-repo-server-patch.yaml

kubectl patch deployment argocd-repo-server -n argocd --patch-file argocd-repo-server-patch.yaml
 
```

## Check the secret value
```bash
kubectl get secret mysecret -o jsonpath="{.data.password}" | base64 -d 
```

