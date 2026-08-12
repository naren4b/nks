# Bootstrap AWS IAM and an S3 Backend for Terraform

This guide creates the first AWS identity used to run Terraform and a private Amazon S3 bucket used to store Terraform state.

> [!IMPORTANT]
> Use an IAM user only as a bootstrap option for a personal learning account or an environment that cannot use temporary credentials. For production, prefer AWS IAM Identity Center, OIDC federation, IAM Roles Anywhere, or an IAM role. Never create access keys for the AWS root user.

## Target setup

| Component | Example |
| --- | --- |
| IAM user | `terraform-bootstrap` |
| Console access | Disabled |
| AWS CLI profile | `terraform` |
| Region | `ap-south-1` |
| S3 bucket | `naren-terraform-state-<account-id>-ap-south-1` |
| State object | `learning/dev/terraform.tfstate` |
| Encryption | SSE-S3 (`AES256`) |
| Versioning | Enabled |
| Public access | Fully blocked |
| State locking | S3 native lock file |

## 1. Secure the root user

Before creating the IAM user:

1. Sign in to AWS as the root user.
2. Enable MFA for the root user.
3. Verify the account email address and phone number.
4. Do not create root-user access keys.
5. Use the root user only for tasks that specifically require it.

## 2. Create the bootstrap IAM user

In the AWS Management Console:

1. Open **IAM**.
2. Go to **Users** and select **Create user**.
3. Enter `terraform-bootstrap`.
4. Do not enable AWS Management Console access.
5. Add the tag `Purpose = TerraformBootstrap`.

### Initial permissions

For a temporary personal sandbox setup, attach the AWS-managed `AdministratorAccess` policy. Remove it after the initial environment is working and replace it with policies restricted to:

- The S3 state bucket and state path.
- The AWS services managed by the Terraform configuration.
- `sts:AssumeRole` if Terraform assumes a separate execution role.

Do not use `AdministratorAccess` for a production Terraform identity.

## 3. Create the access key

1. Open **IAM > Users > terraform-bootstrap**.
2. Select **Security credentials**.
3. Under **Access keys**, select **Create access key**.
4. Choose **Command Line Interface**.
5. Save the access key ID and secret access key in a secure password manager.

The secret access key is displayed only once. Never place credentials in:

- Terraform `.tf` or `.tfvars` files.
- Source-code repositories.
- README files.
- Container images.
- Unencrypted shell scripts.

## 4. Configure and verify the AWS CLI

Configure a named profile:

```bash
aws configure --profile terraform
```

Enter the access key, secret key, region `ap-south-1`, and output format `json`.

Verify the identity:

```bash
aws sts get-caller-identity --profile terraform
```

The ARN should end with:

```text
user/terraform-bootstrap
```

Use the profile in the current terminal:

```bash
export AWS_PROFILE=terraform
export AWS_REGION=ap-south-1
```

## 5. Create the S3 state bucket

Get the AWS account ID and construct a globally unique bucket name:

```bash
TF_ACCOUNT_ID="$(aws sts get-caller-identity --profile terraform --query Account --output text)"
TF_STATE_REGION="ap-south-1"
TF_STATE_BUCKET="naren-terraform-state-${TF_ACCOUNT_ID}-${TF_STATE_REGION}"

echo "$TF_STATE_BUCKET"
```

Create the bucket:

```bash
aws s3api create-bucket \
  --bucket "$TF_STATE_BUCKET" \
  --region "$TF_STATE_REGION" \
  --create-bucket-configuration "LocationConstraint=$TF_STATE_REGION" \
  --profile terraform
```

> [!NOTE]
> For `us-east-1`, omit `--create-bucket-configuration`. The command above is correct for `ap-south-1`.

### Block all public access

```bash
aws s3api put-public-access-block \
  --bucket "$TF_STATE_BUCKET" \
  --public-access-block-configuration \
  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true' \
  --profile terraform
```

### Enable versioning

Versioning helps recover a previous state after accidental deletion, replacement, or corruption.

```bash
aws s3api put-bucket-versioning \
  --bucket "$TF_STATE_BUCKET" \
  --versioning-configuration Status=Enabled \
  --profile terraform
```

### Configure default encryption

```bash
aws s3api put-bucket-encryption \
  --bucket "$TF_STATE_BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' \
  --profile terraform
```

SSE-S3 is sufficient for this learning setup. Use a customer-managed AWS KMS key when organizational requirements demand control over key policies, rotation, and audit boundaries.

## 6. Deny non-TLS access

Create `state-bucket-policy.json`. Replace both bucket-name placeholders with the actual bucket name.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::naren-terraform-state-ACCOUNT_ID-ap-south-1",
        "arn:aws:s3:::naren-terraform-state-ACCOUNT_ID-ap-south-1/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy \
  --bucket "$TF_STATE_BUCKET" \
  --policy file://state-bucket-policy.json \
  --profile terraform
```

## 7. Configure the Terraform backend

Create `backend.tf` in the Terraform project. Backend blocks do not support normal Terraform variables, so replace the bucket name with the real value.

```hcl
terraform {
  required_version = ">= 1.10.0"

  backend "s3" {
    bucket       = "naren-terraform-state-ACCOUNT_ID-ap-south-1"
    key          = "learning/dev/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

`use_lockfile = true` enables S3-native state locking. DynamoDB-based locking is deprecated for new Terraform S3 backend configurations.

Initialize the backend:

```bash
AWS_PROFILE=terraform terraform init
```

If Terraform already has local state, confirm the prompt to migrate that state into S3.

Validate the configuration:

```bash
AWS_PROFILE=terraform terraform validate
AWS_PROFILE=terraform terraform plan
```

Do not run Terraform with `-lock=false` during normal operations.

## 8. Least-privilege access to the state backend

After bootstrapping, replace broad permissions with a restricted policy. Update the bucket name if necessary.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListTerraformStatePrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::naren-terraform-state-ACCOUNT_ID-ap-south-1",
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "learning/dev/*"
          ]
        }
      }
    },
    {
      "Sid": "ReadWriteTerraformState",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::naren-terraform-state-ACCOUNT_ID-ap-south-1/learning/dev/terraform.tfstate"
    },
    {
      "Sid": "ManageTerraformStateLock",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::naren-terraform-state-ACCOUNT_ID-ap-south-1/learning/dev/terraform.tfstate.tflock"
    }
  ]
}
```

This policy grants access only to the remote backend. Add separate permissions for the infrastructure Terraform needs to create, update, and delete.

## 9. Verify the bucket controls

```bash
aws s3api get-public-access-block \
  --bucket "$TF_STATE_BUCKET" \
  --profile terraform

aws s3api get-bucket-versioning \
  --bucket "$TF_STATE_BUCKET" \
  --profile terraform

aws s3api get-bucket-encryption \
  --bucket "$TF_STATE_BUCKET" \
  --profile terraform

aws s3api get-bucket-policy \
  --bucket "$TF_STATE_BUCKET" \
  --profile terraform
```

After the first successful Terraform operation, the bucket should contain:

```text
learning/dev/terraform.tfstate
```

During a state-changing operation, Terraform may temporarily create:

```text
learning/dev/terraform.tfstate.tflock
```

## Operational recommendations

- Keep the backend bucket outside the lifecycle of the workload stack using it.
- Do not run `terraform destroy` against the backend bucket as part of an application stack.
- Use a separate state key for each environment, such as `learning/dev`, `learning/test`, and `learning/prod`.
- Never manually edit or upload a Terraform state file.
- Do not commit `.terraform/`, crash logs, local state, plan files, or credentials.
- Review and remove unused access keys.
- Enable CloudTrail and billing alerts.
- Move CI/CD to OIDC federation or an IAM role instead of static access keys.
- Move human access to IAM Identity Center or another temporary-credential mechanism.

## Suggested `.gitignore`

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
crash.*.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json
.terraformrc
terraform.rc
*.pem
*.key
.env
```

## References

- [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS root-user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html)
- [AWS access-key guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
- [Amazon S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [Amazon S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3)
- [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking)
