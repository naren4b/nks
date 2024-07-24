# Orchestrating Hundreds of Kubernetes Clusters through Multiple ArgoCD Fleet(Scale and Automation)
![100_argocds-aws-region-az](https://github.com/naren4b/nks/assets/3488520/9b3a9443-c172-4c91-b926-2feb38896108)
High-level architecture of Root ArgoCD, Zone ArgoCDs, and Kubernetes clusters

- Root ArgoCD: Central orchestration point
- Zone ArgoCDs: Manage clusters within specific zones
- Kubernetes clusters: Deployment targets

# Why ArgoCD
#### Declarative GitOps Approach:
ArgoCD follows the GitOps paradigm, which means the desired state of the applications and infrastructure is stored in Git repositories. This provides a single source of truth and allows for version-controlled deployments.
#### Automated Synchronization:
ArgoCD continuously monitors the desired state in Git and the actual state in the Kubernetes clusters, automatically synchronizing any deviations.

#### Enhanced Security:
With ArgoCD, you can manage cluster and repository credentials securely. It also supports integration with various authentication mechanisms.

#### Scalability:
ArgoCD is designed to scale, capable of managing deployments across multiple clusters and handling a large number of applications efficiently.

#### User-Friendly Interface:
ArgoCD provides a comprehensive web-based user interface that offers real-time insights into the status of applications, making it easier to manage deployments.

#### Auditing and Compliance:
Every change to the desired state is tracked in the Git repository, providing an audit trail for compliance and troubleshooting.
#### Flexibility:
ArgoCD supports various deployment strategies, such as blue-green deployments, canary releases, and more. It can also manage Helm charts, Kustomize applications, and plain Kubernetes manifests.

#### Self-Healing:
ArgoCD can automatically roll back changes if a deployment fails, ensuring system stability and minimizing downtime.

#### Integration with CI Tools:
ArgoCD integrates seamlessly with popular CI tools, allowing for a smooth CI/CD pipeline. It can trigger deployments based on changes in the repository or external events.
#### Community and Ecosystem:
As an open-source tool, ArgoCD benefits from a large and active community, ensuring continuous improvements, support, and a rich ecosystem of plugins and integrations.

# Setting Up Root ArgoCD
#### 1. Install Root ArgoCD via Helm install
ref: [Install Argocd to standalon kubernetes cluster](https://gist.github.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e)
```bash
curl -sO https://gist.githubusercontent.com/naren4b/ac834254f2d348d7b5e91ebc32fcba6e/raw/3a35d8d083203d7203f58c286398b6cd3a656b7d/install-argocd.sh
bash install-argocd.sh
```
#### 2. Add git repo credentials - declaratively(Optional) 

Steps:
- Export Git token
- Run the script to create credentials
- Reference: [Repository credentials Script, for using the same credentials in multiple repositories.](https://gist.github.com/naren4b/fae65efb90998cb46a3c9ebed16df880)
Example:  
```
# export MY_GIT_TOKEN={token}
curl -sO https://gist.githubusercontent.com/naren4b/fae65efb90998cb46a3c9ebed16df880/raw/443682b34a4a5bc6a212cca93cd41e32873f2eb2/create-https-repo-creds-secret.sh
# vi create-https-repo-creds-secret.sh
bash create-https-repo-creds-secret.sh
```
#### 3. Add cluster credentials - declaratively(Otional)
Steps:
- Download and run the script to create cluster secrets
- Reference: [Register A Cluster ](https://gist.github.com/naren4b/4af945b244f60d801ca77227cdeda861)
```bash
curl -sO https://gist.githubusercontent.com/naren4b/4af945b244f60d801ca77227cdeda861/raw/c83902c8b9644f225764d2b4890ef9b8d917470d/create-cluster-secret.sh
bash create-cluster-secret.sh 
```
##### 4. Create Argocd Application Deploy 
Create s seeding ArgoCD Application to trigger everything 

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
# Setting Up Zone ArgoCD
Zone ArgoCD value file details at your Private value file repo 
Key Points:
- Cluster Settings 
- Git repository settings
- Example [Configuration zone argocd Values](https://raw.githubusercontent.com/naren4b/argo-cd/main/charts/zone-argocd/values.yaml)

# To Check  zone Argocd
```
kubectl -n in-cluster-zone-argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
nohup kubectl port-forward -n in-cluster-zone-argocd svc/in-cluster-zone-argocd-server 5000:80 --address 0.0.0.0 &
```

# Conclusion
#### Summary:
- Benefits of using ArgoCD for managing CD
- Scalability across multiple clusters
- Automation and self-healing capabilities
#### Next Steps:
- Implementation roadmap
- Future improvements and enhancements



