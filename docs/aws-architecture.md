# AWS Solutions Architecture

This section brings together my AWS-focused implementation guides and the architecture principles behind them. It will grow from foundational account security and infrastructure delivery into complete workload architectures aligned with the AWS Well-Architected Framework.

## Current AWS Guides

### Identity & Infrastructure Foundations

- [Bootstrap AWS IAM and an S3 Backend for Terraform](aws-terraform-iam.md) — secure initial access, remote state, encryption, versioning, and public-access controls.
- [Terraform, OpenTofu, and Terragrunt Delivery](tg-tf-gl.md) — reusable infrastructure modules, remote state, validation, and CI/CD patterns applicable to AWS environments.

### Containers & Compute

- [Set Up Karpenter on Amazon EKS](install-karpenter.md) — dynamic node provisioning and workload-aware compute capacity.
- [Amazon EKS Auto Mode with S3](eks-auto-s3.md) — secure workload access to object storage and cost-conscious managed Kubernetes operations.

### Reliability & Operations

- [Business Continuity: RPO, RTO, and MTD](bcp.md) — requirements that drive AWS backup, replication, and recovery architecture.
- [Kubernetes Resource Management](k8s-resource-management.md) — capacity practices that inform EKS performance and cost decisions.
- [Observability and Reliability](setup-monitoring-stack.md) — operational patterns to carry into Amazon CloudWatch and managed observability services.

## AWS Well-Architected Lens

New AWS articles should explain their decisions against these pillars:

| Pillar | Questions addressed |
| --- | --- |
| Operational Excellence | How is the workload deployed, observed, operated, and improved? |
| Security | How are identity, data, networks, and detection protected? |
| Reliability | How does the design tolerate failure and recover? |
| Performance Efficiency | Why were these services and scaling models selected? |
| Cost Optimization | How are usage, pricing models, and waste controlled? |
| Sustainability | How does the design minimize unnecessary resource consumption? |

## Architecture Roadmap

Planned coverage includes:

- Multi-account governance with AWS Organizations and Control Tower
- VPC, Transit Gateway, Route 53, and hybrid connectivity patterns
- EC2, Lambda, ECS, and EKS workload-selection guidance
- S3, EBS, EFS, RDS, DynamoDB, and database-selection trade-offs
- IAM Identity Center, KMS, WAF, GuardDuty, Security Hub, and centralized logging
- Multi-AZ, multi-region, backup, and disaster-recovery architectures
- Migration assessment, landing zones, modernization, and FinOps

These roadmap items are future work; the links above represent currently published, hands-on evidence.
