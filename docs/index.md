# From Site Reliability Engineering to AWS Solutions Architecture

Welcome to my cloud architecture portfolio. I am **Narendranath Panda**, a Cloud and Platform Architect with 19+ years of infrastructure experience. This portal documents my progression from operating reliable systems as an SRE to designing secure, scalable, and cost-aware solutions on AWS.

[Explore My Journey](career-journey.md){ .md-button .md-button--primary }
[Browse AWS Architecture](aws-architecture.md){ .md-button }
[About Me](about.md){ .md-button }

## My Engineering Progression

### 1. SRE Foundations

I started with the operational disciplines that make systems dependable: monitoring, logging, capacity management, backup and recovery, incident prevention, and measurable reliability.

**Evidence:** [VictoriaLogs](victorialogs-demo.md) · [Thanos](unlimited-monitoring-data-by-thanos.md) · [Business Continuity](bcp.md) · [Backup and Restore](vmbackup_and_vmrestore.md)

### 2. Cloud-Native & Kubernetes Engineering

I expanded those reliability practices into container platforms—managing Kubernetes resources, cluster access, ingress, autoscaling, certificates, secrets, and workload security.

**Evidence:** [Kubernetes Resource Management](k8s-resource-management.md) · [Cluster Access](kubernetes-adduser.md) · [mTLS](secure-local-ingress.md) · [Image Security](cosign-syft-grype-kevyrno.md)

### 3. Platform Engineering & GitOps

I moved from operating individual clusters to creating repeatable platforms with Argo CD, CI/CD, reusable infrastructure modules, policy-driven delivery, and multi-cluster automation.

**Evidence:** [Multi-Cluster Argo CD](argocd-multiple-deployment.md) · [IaC Pipelines](tg-tf-gl.md) · [Terragrunt](tg-concepts.md) · [Harbor IaC](tg-tf-gl-hbr.md)

### 4. AWS Solutions Architecture

My current focus applies the same operational depth to AWS architecture: identity, networking, compute, storage, resilience, security, observability, automation, and cost optimization. The goal is to connect design decisions to business outcomes and the AWS Well-Architected pillars.

**Evidence:** [AWS IAM and Terraform Backend](aws-terraform-iam.md) · [EKS Auto Mode with S3](eks-auto-s3.md) · [Karpenter on EKS](install-karpenter.md)

## Architecture Principles

- Design for failure, recovery, and measurable service objectives.
- Automate infrastructure and delivery through version-controlled workflows.
- Apply least privilege, layered security, and auditable access.
- Balance reliability, performance, sustainability, and cost.
- Document trade-offs, validation steps, and production considerations.

## Explore the Portfolio

Use the navigation to follow the progression in order, or start with the dedicated [AWS Architecture](aws-architecture.md) hub. Each guide captures practical implementation work and the architecture reasoning behind it.
