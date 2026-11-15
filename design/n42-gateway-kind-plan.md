# NKS and N42 Gateway plan

Date: 2026-11-15

## Goal

Provide the simplest robust local developer platform based on kind, default
local-path storage, and the Kubernetes Gateway API implemented by N42 Gateway.
This does not install an API gateway product.

## Decisions

- Keep kind as the generic local Kubernetes layer.
- Keep the StorageClass supplied by kind. Validate a PVC separately before
  applications depend on it.
- Install the N42 Gateway controller once as shared cluster infrastructure.
- Start on stable N42 Gateway v0.16.3 and Gateway API Standard CRDs v1.7.0.
  Use only basic HTTPRoute behavior because this N42 Gateway line has partial
  Gateway API support. Review v0.17 again after it leaves alpha.
- Map host 127.0.0.1:8080 to kind control-plane port 80. Bind the controller
  to that node only with a DaemonSet, hostPort, node selector, and control-plane
  toleration.
- Keep controller Helm values generic in NKS. Each application owns its
  Namespace, Deployment, Service, and HTTPRoute.
- Keep Argo CD generic installation and RBAC separate. Preserve the user's
  updated docs/argocd-rbac.md.

## Open/Closed ownership rule

The shared Gateway controller is installed and configured once. New application
routes extend the setup through Gateway API resources. An application should
not need to edit the shared controller values or replace the controller release.
The initial lab keeps the Gateway and sample route in one namespace to avoid
introducing cross-namespace policy in the first pass.

## Delivery

1. Align the kind guide's version table and commands with the observed Docker,
   kind, kubectl, and Kubernetes versions. Remove the stale Kubernetes 1.37
   instructions that caused the kubeadm API mismatch.
2. Add a dated N42 Gateway on kind implementation guide with pinned versions,
   host port design, sample HTTPRoute, validation, limitations, and cleanup.
3. Archive only superseded ingress-specific articles outside the published
   MkDocs tree. Keep the old published URLs as short archive notices.
4. Add the new article to MkDocs navigation and the repository README feature
   list. Leave the updated Argo CD RBAC article untouched.
5. Run a strict MkDocs build and diff checks before opening a review PR.

## Scope for learn-gitlab

The GitLab repository should contain only GitLab-specific resources:
GitLab chart values, Argo CD Application or App-of-Apps definitions, and
GitLab-specific Gateway routes. Do not duplicate the shared kind or N42
Gateway installation.

## Deferred

- HTTPS, cert-manager, and local CA workflow.
- Cross-namespace route attachment and policy.
- Metrics, dashboards, production HA, and external DNS.
- GitLab deployment details.
