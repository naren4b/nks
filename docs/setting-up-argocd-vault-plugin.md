# Securing Kubernetes Secrets with Argocd-vault-plugin
![image](https://github.com/naren4b/nks/assets/3488520/2c71e8b7-5502-46db-8428-7e9ac0aa7d59)

Managing secrets securely within Kubernetes clusters can be challenging, especially when following GitOps practices with tools like Argo CD. In this guide, we'll explore how to leverage the Argocd-vault-plugin to streamline secret management within Kubernetes clusters using Vault.

## Introduction to Argocd-vault-plugin
The Argocd-vault-plugin is designed to address the complexities of secret management in GitOps workflows with Argo CD. By integrating with Vault, it offers a simple yet robust solution for managing secrets, configurations, and deployments within Kubernetes clusters.

![image](https://github.com/user-attachments/assets/f283b79a-a70b-44f2-bcd0-2d0e5cea60b7)

The setup 

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
```bash
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
```

```bash
# edit the deployment for insecure installation in local
kubectl patch deployments.apps -n argocd  argocd-server  \
--type=json \
-p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--insecure"}]'
nohup kubectl  port-forward -n argocd svc/argocd-server 8080:443 --address 0.0.0.0 & 

argocd_password=$(kubectl get secrets -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo $argocd_password
argocd login localhost:8080  --insecure --username=admin --password=$argocd_password
```

```bash
argocd repo add https://github.com/naren4b/demo-app.git

argocd app create demo \
     --repo https://github.com/naren4b/demo-app.git \
     --path helm-chart \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default \
     --sync-policy  automated
```
## Integrate the argocd-vault plugin as configmap
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
wget https://raw.githubusercontent.com/naren4b/demo-app/main/others/argocd-repo-server-patch.yaml
kubectl patch deployment argocd-repo-server -n argocd --patch-file argocd-repo-server-patch.yaml
kubectl get pod -n argocd -w
# edit and update the `serviceAccount` Name in the `argocd-repo-server` deployment to use `argocd-server`
# Restart all the pods
kubectl get pod -n argocd | awk '{print $1}' | xargs kubectl delete pod -n argocd
# add the argocd-vault-plugin-helm
kubectl apply -f https://raw.githubusercontent.com/naren4b/demo-app/main/others/demo-argocd-application.yaml
```
![image](https://github.com/naren4b/nks/assets/3488520/c79e1304-1b2e-4bf6-be83-48b789c8d06b)


![image](https://github.com/naren4b/nks/assets/3488520/97ca08db-c12b-4829-ae06-253499e7e342)

![image](https://github.com/naren4b/nks/assets/3488520/b1bb357d-5be7-4b29-9137-04fccf264149)


## Check the secret value
```bash
kubectl get secret mysecret -o jsonpath="{.data.password}" | base64 -d 
```
![image](https://github.com/naren4b/nks/assets/3488520/efa5506c-14e3-4b60-bded-a55f3cd5e285)



**ref**:
- https://killercoda.com/killer-shell-ckad/scenario/playground
- https://youtu.be/7L6nSuKbC2c?si=q_v-F9Qpv3x5pNQm
- https://argocd-vault-plugin.readthedocs.io/en/stable/ 
- https://medium.com/@raosharadhi11/argocd-with-vault-using-argocd-vault-plugin-dccbc302f0c2
