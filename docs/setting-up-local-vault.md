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
#### Set up kubernetes authentication
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





