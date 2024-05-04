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
# Argocd-vault-plugin This plugin is aimed at helping to solve the issue of secret management with GitOps and Argo CD. We wanted to find a simple way to utilize Vault without having to rely on an operator or custom resource definition. This plugin can be used not just for secrets but also for deployments, configMaps or any other Kubernetes resource.
![image](https://github.com/naren4b/nks/assets/3488520/f3852901-4bbc-466d-828f-54f0b942b0af)

# Inside the vault
```
export VAULT_ADDR=http://127.0.0.1:8200
vault login root 
vault token create
```
# Create the Access for argocd 
```
k create secret generic vault-configuration --from-literal=AVP_AUTH_TYPE=token --from-literal=VAULT_ADDR=http://127.0.0.1:8200 --from-literal=AVP_TYPE=vault --from-literal=VAULT_TOKEN=hvs.HtIpb
qbXh2bPkQ5Bm7OUuoR0  --dry-run=client -o yaml

```
```
cat<<EOF> /tmp/cmp-plugin.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cmp-plugin
  namespace: argocd
data:
  avp-helm.yaml: |
    ---
    apiVersion: argoproj.io/v1alpha1
    kind: ConfigManagementPlugin
    metadata:
      name: argocd-vault-plugin-helm
    spec:
      allowConcurrency: true
      discover:
        find:
          command:
            - sh
            - "-c"
            - "find . -name 'Chart.yaml' && find . -name 'values.yaml'"
      generate:
        command:
          - bash
          - "-c"
          - |
            helm template $ARGOCD_APP_NAME -n $ARGOCD_APP_NAMESPACE -f <(echo "$ARGOCD_ENV_HELM_VALUES") . |
            argocd-vault-plugin generate -s vault-configuration -
      lockRepo: false
  avp.yaml: |
    apiVersion: argoproj.io/v1alpha1
    kind: ConfigManagementPlugin
    metadata:
      name: argocd-vault-plugin
    spec:
      allowConcurrency: true
      discover:
        find:
          command:
            - sh
            - "-c"
            - "find . -name '*.yaml' | xargs -I {} grep \"<path\\|avp\\.kubernetes\\.io\" {} | grep ."
      generate:
        command:
          - argocd-vault-plugin
          - generate
          - "."
          - "-s"
          - "vault-configuration"
      lockRepo: false
---
EOF
```
# Install argocd 
```
kubectl create ns argocd
kubectl apply -f secret.yaml -n argocd
kubectl apply -f cmp-plugin.yaml -n argocd
```
# Install the argocd helm chart
```
cat<<EOF > /tmp/argocd-values.yaml
repoServer:
  rbac:
    - verbs:
        - get
        - list
        - watch
      apiGroups:
        - ''
      resources:
        - secrets
        - configmaps
  initContainers:
    - name: download-tools
      image: registry.access.redhat.com/ubi8
      env:
        - name: AVP_VERSION
          value: 1.11.0
      command: [sh, -c]
      args:
        - >-
          curl -L https://github.com/argoproj-labs/argocd-vault-plugin/releases/download/v$(AVP_VERSION)/argocd-vault-plugin_$(AVP_VERSION)_linux_amd64 -o argocd-vault-plugin &&
          chmod +x argocd-vault-plugin &&
          mv argocd-vault-plugin /custom-tools/
      volumeMounts:
        - mountPath: /custom-tools
          name: custom-tools

  extraContainers:
    # argocd-vault-plugin with plain YAML
    - name: avp
      command: [/var/run/argocd/argocd-cmp-server]
      image: quay.io/argoproj/argocd:v2.4.0
      securityContext:
        runAsNonRoot: true
        runAsUser: 999
      volumeMounts:
        - mountPath: /var/run/argocd
          name: var-files
        - mountPath: /home/argocd/cmp-server/plugins
          name: plugins
        - mountPath: /tmp
          name: tmp

        # Register plugins into sidecar
        - mountPath: /home/argocd/cmp-server/config/plugin.yaml
          subPath: avp.yaml
          name: cmp-plugin

        # Important: Mount tools into $PATH
        - name: custom-tools
          subPath: argocd-vault-plugin
          mountPath: /usr/local/bin/argocd-vault-plugin
    
    - name: avp-helm
      command: [/var/run/argocd/argocd-cmp-server]
      image: quay.io/argoproj/argocd:v2.5.3
      securityContext:
        runAsNonRoot: true
        runAsUser: 999
      volumeMounts:
        - mountPath: /var/run/argocd
          name: var-files
        - mountPath: /home/argocd/cmp-server/plugins
          name: plugins
        - mountPath: /tmp
          name: tmp
        - mountPath: /home/argocd/cmp-server/config/plugin.yaml
          subPath: avp-helm.yaml
          name: cmp-plugin
        - name: custom-tools
          subPath: argocd-vault-plugin
          mountPath: /usr/local/bin/argocd-vault-plugin
      
  volumes:
    - configMap:
        name: cmp-plugin
      name: cmp-plugin
    - name: custom-tools
      emptyDir: {}
EOF
```
# Install Argocd helm chart
```
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -n argocd -f /tmp/argocd-values.yaml
kubectl get pods -n argocd
# note that the reposerver should show 2/2 pods as we added initContainers.
# we can access UI and get password for the ArgoCD using the following command
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
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
Overview: Token authentication is the simplest and most commonly used method. When Vault is initialized or unsealed, it generates a root token by default. This root token has full access to Vault and should be securely stored and used only for administrative tasks.
Usage: Besides the root token, Vault can generate and manage other tokens with limited access and lifetimes. Tokens can be used to authenticate users, applications, or services to access secrets or perform actions within Vault.
Authentication Process: Users provide their token to Vault when accessing resources or performing operations. Vault validates the token against its internal token store and grants access based on the token's policies and capabilities.
Use Cases: Token authentication is suitable for various scenarios, including initial setup, administrative tasks, and user or application authentication.

