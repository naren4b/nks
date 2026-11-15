# Archived ingress guides

These original articles were moved here on 2026-11-15 because their installation
examples rely on retired or obsolete ingress-controller paths, old Kubernetes
images, or unmaintained configuration.

The archived files are kept for historical reference and are not published by
the MkDocs site. The existing article URLs now show a short notice.

- [Emissary ingress on kind](emissary-ingress.md)
- [Local mTLS ingress](secure-local-ingress.md)
- [NKS cert-manager PKI guide](k8s-nks-pki-cert-manager.md)

The new basic local Gateway setup is documented in
[docs/n42-gateway-kind.md](../../docs/n42-gateway-kind.md). It uses the
Kubernetes Gateway API with N42 Gateway. It does not replace the archived
mTLS or certificate-authority instructions; add those only in a separate
follow-up after choosing a supported TLS design.
