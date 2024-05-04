# Secret injection using Vault Agent and argocd-vault-plugin
![image](https://github.com/naren4b/nks/assets/3488520/2c71e8b7-5502-46db-8428-7e9ac0aa7d59)
- **Using Vault Agent** Injecting secrets into Kubernetes pods via Vault Agent containers
- **Argocd-vault-plugin** This plugin is aimed at helping to solve the issue of secret management with GitOps and Argo CD. We wanted to find a simple way to utilize Vault without having to rely on an operator or custom resource definition. This plugin can be used not just for secrets but also for deployments, configMaps or any other Kubernetes resource.

# Using Vault Agent:  Injecting secrets into Kubernetes pods via Vault Agent containers
- 
![image](https://github.com/naren4b/nks/assets/3488520/9353da4b-a21d-467d-831a-f0a9ebd612c2)


### Install Vault 
```
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm install vault hashicorp/vault --set "server.dev.enabled=true"
```
### Configure Vault 
```bash
kubectl exec -it vault-0 -- /bin/sh
```
#### Inside the pod 
```bash
# Enable kv-v2 secrets at the path internal.
vault secrets enable -path=internal kv-v2

#Create a secret at path internal/database/config with a username and password.
vault kv put internal/database/config username="naren" password="mypassword"

# Check the values
vault kv get internal/database/config

```
#### Set up kubernetes authentication*
Vault provides a Kubernetes authentication method that enables clients to authenticate with a Kubernetes Service Account Token. This token is provided to each pod when it is created.

```bash
# Enable the Kubernetes authentication method.
vault auth enable kubernetes

# Configure the Kubernetes authentication method to use the location of the Kubernetes API. (when running inside the cluster)
vault write auth/kubernetes/config \
      kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

# Write out the policy named internal-app that enables the read capability for secrets at path internal/data/database/config.
vault policy write internal-app - <<EOF
path "internal/data/database/config" {
   capabilities = ["read"]
}
EOF

# Create a Kubernetes authentication role named internal-app.
vault write auth/kubernetes/role/internal-app \
      bound_service_account_names=internal-app \
      bound_service_account_namespaces=default \
      policies=internal-app \
      ttl=24h

# Create a Kubernetes authentication role named argocd.
vault write auth/kubernetes/role/argocd \
      bound_service_account_names=argocd \
      bound_service_account_namespaces=argocd \
      policies=internal-app \
      ttl=24h
exit
```
### Set up in Kubernetes Create service account
```
kubectl create sa internal-app
cat<<EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
   name: orgchart
   labels:
      app: orgchart
spec:
   selector:
      matchLabels:
       app: orgchart
   replicas: 1
   template:
      metadata:
       annotations:
         vault.hashicorp.com/agent-inject: 'true'
         vault.hashicorp.com/role: 'internal-app'
         vault.hashicorp.com/agent-inject-secret-database-config.txt: 'internal/data/database/config'
       labels:
         app: orgchart
      spec:
       serviceAccountName: internal-app
       containers:
         - name: orgchart
           image: jweissig/app:0.0.1
EOF
kubectl apply -f deployment.yaml
```

# Check the Secret 
```
kubectl exec \
      $(kubectl get pod -l app=orgchart -o jsonpath="{.items[0].metadata.name}") \
      --container orgchart -- cat /vault/secrets/database-config.txt
```
# Argocd-vault-plugin 
 This plugin is aimed at helping to solve the issue of secret management with GitOps and Argo CD. We wanted to find a simple way to utilize Vault without having to rely on an operator or custom resource definition. This plugin can be used not just for secrets but also for deployments, configMaps or any other Kubernetes resource.
![image](https://github.com/naren4b/nks/assets/3488520/f3852901-4bbc-466d-828f-54f0b942b0af)

```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl edit deployments.apps -n argocd argocd-server  // argument --insecure 
nohup kubectl  port-forward -n argocd svc/argocd-server 8080:443 --address 0.0.0.0 & 

curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

argocd_password=$(kubectl get secrets -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
argocd login localhost:8080  --insecure --username=admin --password=$argocd_password 
kubectl create secret generic -n argocd argocd-vault-plugin-credentials \
	--from-literal=AVP_TYPE=vault \
	--from-literal=VAULT_ADDR=http://vault-internal.default.svc.cluster.local:8200 \
	--from-literal=AVP_AUTH_TYPE=k8s \
	--from-literal=AVP_K8S_ROLE=argocd
wget https://raw.githubusercontent.com/argoproj-labs/argocd-vault-plugin/main/manifests/cmp-configmap/argocd-repo-server-deploy.yaml
kubectl patch deployment argocd-repo-server  -n argocd --patch-file argocd-repo-server-deploy.yaml
wget https://raw.githubusercontent.com/argoproj-labs/argocd-vault-plugin/main/manifests/cmp-configmap/argocd-cm.yaml
kubectl patch cm argocd-cm  -n argocd --patch-file argocd-cm.yaml


```



# 1. Create argocd-vault-plugin-credentials 
```
kubectl exec -it vault-0 -- /bin/sh
export VAULT_ADDR=http://127.0.0.1:8200
vault login root 
vault token create // copy the token 
exit

```
# Create the Access for argocd 
```
# curl -v vault-internal.default.svc.cluster.local:8200
k create secret generic argocd-vault-plugin-credentials \
                 --from-literal=AVP_AUTH_TYPE=token\
                 --from-literal=VAULT_ADDR=http://vault-internal.default.svc.cluster.local:8200\ 
                 --from-literal=AVP_TYPE=vault\
                 --from-literal=VAULT_TOKEN=<token> \
                 --dry-run=client -o yaml>/tmp/secret.yaml

```
```
cat<<EOF> /tmp/cmp-plugin.yaml

```


# Install Argocd helm chart
```
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -n argocd -f /tmp/argocd-values.yaml
kubectl get pods -n argocd
# note that the reposerver should show 2/2 pods as we added initContainers.
# we can access UI and get password for the ArgoCD using the following command
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
kubectl port-forward svc/argocd-server -n argocd 8080:443 &
```

# Inside the Vault
```
# enable key-value engine
vault secrets enable kv-v2
# add the password to path kv-v2/argocd
vault kv put kv-v2/argocd password="argocd"
# add a policy to read the previously created secret
vault policy write argocd - <<EOF
path "kv-v2/data/argocd" {
  capabilities = ["read"]
}
EOF
```

# Secret Yaml file 
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
  annotations:
    avp.kubernetes.io/path: "kv-v2/data/argocd"
type: Opaque
stringData:
  TOKEN: <password>
```

^ Vault Authentication Methods
**Token Authentication:**
_Overview_: Token authentication is the simplest and most commonly used method. When Vault is initialized or unsealed, it generates a root token by default. This root token has full access to Vault and should be securely stored and used only for administrative tasks.
_Usage_: Besides the root token, Vault can generate and manage other tokens with limited access and lifetimes. Tokens can be used to authenticate users, applications, or services to access secrets or perform actions within Vault.
_Authentication Process_: Users provide their token to Vault when accessing resources or performing operations. Vault validates the token against its internal token store and grants access based on the token's policies and capabilities.
_Use Cases_: Token authentication is suitable for various scenarios, including initial setup, administrative tasks, and user or application authentication.

**Kubernetes Authentication:**
_Overview_: Kubernetes authentication enables applications running in Kubernetes clusters to authenticate with Vault seamlessly. It uses Kubernetes Service Account Tokens for authentication.
_Configuration_: Vault is configured to trust Kubernetes' token-based authentication system. Kubernetes Pods can authenticate with Vault by presenting their Service Account Token.
_Dynamic Secrets_: Vault can dynamically generate short-lived credentials (e.g., database credentials) for applications based on Kubernetes authentication. This enhances security by minimizing the exposure of long-lived credentials.
_Use Cases_: Kubernetes authentication is valuable in containerized environments where applications run in Kubernetes Pods. It streamlines access management and enhances security by integrating with Kubernetes' native authentication mechanisms.

