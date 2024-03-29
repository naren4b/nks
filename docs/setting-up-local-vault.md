```
kubectl create namespace vault
kubectl --namespace='vault' get all

helm repo add hashicorp https://helm.releases.hashicorp.com
helm search repo hashicorp/vault
helm install vault hashicorp/vault --namespace vault --dry-run
helm install vault hashicorp/vault --namespace vault --version 0.5.0
helm install vault hashicorp/vault \
 --namespace vault \
 --set "server.ha.enabled=true" \
 --set "server.ha.replicas=5" \
 --dry-run
```

# Override
```
cat << EOF > ./override-values.yml
server:
ha:
enabled: true
replicas: 5
EOF
helm install vault hashicorp/vault \
 --namespace vault \
 -f override-values.yml \
 --dry-run
```
```
cat << EOF > ./override-values.yml

# Vault Helm Chart Value Overrides

global:
enabled: true
tlsDisable: false

injector:
enabled: true

# Use the Vault K8s Image https://github.com/hashicorp/vault-k8s/

image:
repository: "hashicorp/vault-k8s"
tag: "latest"

resources:
requests:
memory: 256Mi
cpu: 250m
limits:
memory: 256Mi
cpu: 250m

server:

# Use the Enterprise Image

image:
repository: "hashicorp/vault-enterprise"
tag: "1.5.0_ent"

# These Resource Limits are in line with node requirements in the

# Vault Reference Architecture for a Small Cluster

resources:
requests:
memory: 8Gi
cpu: 2000m
limits:
memory: 16Gi
cpu: 2000m

# For HA configuration and because we need to manually init the vault,

# we need to define custom readiness/liveness Probe settings

readinessProbe:
enabled: true
path: "/v1/sys/health?standbyok=true&sealedcode=204&uninitcode=204"
livenessProbe:
enabled: true
path: "/v1/sys/health?standbyok=true"
initialDelaySeconds: 60

# extraEnvironmentVars is a list of extra environment variables to set with the stateful set. These could be

# used to include variables required for auto-unseal.

extraEnvironmentVars:
VAULT_CACERT: /vault/userconfig/tls-ca/ca.crt

# extraVolumes is a list of extra volumes to mount. These will be exposed

# to Vault in the path `/vault/userconfig/<name>/`.

extraVolumes: - type: secret
name: tls-server - type: secret
name: tls-ca - type: secret
name: kms-creds

# This configures the Vault Statefulset to create a PVC for audit logs.

# See https://www.vaultproject.io/docs/audit/index.html to know more

auditStorage:
enabled: true

standalone:
enabled: false

# Run Vault in "HA" mode.

ha:
enabled: true
replicas: 5
raft:
enabled: true
setNodeId: true

      config: |
        ui = true
        listener "tcp" {
          address = "[::]:8200"
          cluster_address = "[::]:8201"
          tls_cert_file = "/vault/userconfig/tls-server/fullchain.pem"
          tls_key_file = "/vault/userconfig/tls-server/server.key"
          tls_client_ca_file = "/vault/userconfig/tls-server/client-auth-ca.pem"
        }

        storage "raft" {
          path = "/vault/data"
            retry_join {
            leader_api_addr = "https://vault-0.vault-internal:8200"
            leader_ca_cert_file = "/vault/userconfig/tls-ca/ca.crt"
            leader_client_cert_file = "/vault/userconfig/tls-server/server.crt"
            leader_client_key_file = "/vault/userconfig/tls-server/server.key"
          }
          retry_join {
            leader_api_addr = "https://vault-1.vault-internal:8200"
            leader_ca_cert_file = "/vault/userconfig/tls-ca/ca.crt"
            leader_client_cert_file = "/vault/userconfig/tls-server/server.crt"
            leader_client_key_file = "/vault/userconfig/tls-server/server.key"
          }
          retry_join {
            leader_api_addr = "https://vault-2.vault-internal:8200"
            leader_ca_cert_file = "/vault/userconfig/tls-ca/ca.crt"
            leader_client_cert_file = "/vault/userconfig/tls-server/server.crt"
            leader_client_key_file = "/vault/userconfig/tls-server/server.key"
          }
          retry_join {
              leader_api_addr = "https://vault-3.vault-internal:8200"
              leader_ca_cert_file = "/vault/userconfig/tls-ca/ca.crt"
              leader_client_cert_file = "/vault/userconfig/tls-server/server.crt"
              leader_client_key_file = "/vault/userconfig/tls-server/server.key"
          }
          retry_join {
              leader_api_addr = "https://vault-4.vault-internal:8200"
              leader_ca_cert_file = "/vault/userconfig/tls-ca/ca.crt"
              leader_client_cert_file = "/vault/userconfig/tls-server/server.crt"
              leader_client_key_file = "/vault/userconfig/tls-server/server.key"
          }

        }

        service_registration "kubernetes" {}

# Vault UI

ui:
enabled: true
serviceType: "LoadBalancer"
serviceNodePort: null
externalPort: 8200

# For Added Security, edit the below

#loadBalancerSourceRanges:

# - < Your IP RANGE Ex. 10.0.0.0/16 >

# - < YOUR SINGLE IP Ex. 1.78.23.3/32 >
EOF
```
```
kubectl --namespace='vault' create secret tls vault-ca-crt --cert ./tls-ca.cert --key ./tls-ca.key
kubectl create secret generic consul-token --from-file=./consul_token
kubectl --namespace='vault' create secret tls tls-secret --cert=path/to/tls.cert --key=path/to/tls.key
```
