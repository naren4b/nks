# Naren Cloud Architecture Lab

Practical AWS, Kubernetes, and platform engineering guides by **Narendranath Panda**.

I document how I approach cloud architecture through DevOps and SRE: repeatable infrastructure, secure delivery, observability, recovery, and cost-aware design. This repository is the source for **[blog.npanda.online](https://blog.npanda.online/)**.

## Start Here

- [Architecture portfolio](docs/index.md): the engineering progression and principles behind the work.
- [AWS architecture hub](docs/aws-architecture.md): design decisions and AWS Well-Architected considerations.
- [About me](docs/about.md): professional focus and public links.

## Engineering Focus

This repository covers:

- Kubernetes, Amazon EKS, and edge computing
- GitOps, Argo CD, and CI/CD
- Observability, reliability, and disaster recovery
- DevSecOps, secrets, and software supply-chain security
- Terraform, OpenTofu, and Terragrunt
- AI-assisted infrastructure operations and automation

## Featured Guides

- **AWS and infrastructure:** [EKS Auto Mode with S3](docs/eks-auto-s3.md) and [IaC pipelines with Terraform, OpenTofu, and Terragrunt](docs/tg-tf-gl.md).
- **Platform engineering:** [Multi-cluster deployment through Argo CD](docs/argocd-multiple-deployment.md).
- **Security:** [Kubernetes traffic with mTLS](docs/secure-local-ingress.md), [software supply-chain security](docs/cosign-syft-grype-kevyrno.md), and [image signing and attestation](docs/image-signing-attestation.md).
- **Reliability and observability:** [VictoriaLogs](docs/victorialogs-demo.md), [VictoriaMetrics backup and restore](docs/vmbackup_and_vmrestore.md), and [GitHub Copilot metrics](docs/gcp-metrics-exporter.md).
- **AI tooling:** [Harbor MCP: talk to your container registry](docs/harbor-mcp.md).

The published navigation in [mkdocs.yml](mkdocs.yml) is the complete article catalog. These links highlight selected work.

## Using the Guides

The repository contains architecture notes, implementation guides, and learning labs. Read each guide's prerequisites and validation steps before running commands; coverage and tested environments vary by article. Treat large-scale designs as architecture studies unless the guide includes deployment evidence.

## Preview and Validate

Use Python 3.12 to match CI. From the repository root:

```sh
python -m venv .venv
# Linux / WSL:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs serve
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1` instead.

Before opening a PR:

```sh
python -m mkdocs build --strict
git diff --check
```

GitHub Actions validates PRs and publishes the site after a merge to `main`.

## Publish an Article

Follow the [article publishing guide](PUBLISHING.md) for local setup, the article template, navigation updates, validation, and deployment. Repository-wide contribution rules are in [AGENTS.md](AGENTS.md).
