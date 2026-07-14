# Naren Cloud Architecture Lab

Practical architecture notes, implementation guides, and hands-on labs for cloud and platform engineers.

This repository covers:

- Kubernetes, Amazon EKS, and edge computing
- GitOps, Argo CD, and CI/CD
- Observability, reliability, and disaster recovery
- DevSecOps, secrets, and software supply-chain security
- Terraform, OpenTofu, and Terragrunt
- AI-assisted infrastructure operations and automation

## Documentation

Read the complete, searchable documentation at **[blog.npanda.online](https://blog.npanda.online/)**.

## Featured Guides

- [Orchestrating Thousands of Kubernetes Clusters through Argo CD](docs/argocd-multiple-deployment.md)
- [Building IaC Pipelines with Terraform, OpenTofu, and Terragrunt](docs/tg-tf-gl.md)
- [Securing Kubernetes Traffic with mTLS](docs/secure-local-ingress.md)
- [Enhancing Software Supply-Chain Security](docs/cosign-syft-grype-kevyrno.md)
- [Exploring VictoriaLogs](docs/victorialogs-demo.md)
- [Harbor MCP: Talk to Your Container Registry](docs/harbor-mcp.md)

## Local Preview

```sh
python -m venv .venv
python -m pip install -r requirements.txt
mkdocs serve
```

Open `http://127.0.0.1:8000`. Before submitting changes, run `mkdocs build --strict`.

## Contributing

Articles live in `docs/`. Use lowercase kebab-case filenames, add new pages to the categorized navigation in `mkdocs.yml`, and verify all commands and links. See [AGENTS.md](AGENTS.md) for the repository guidelines.
