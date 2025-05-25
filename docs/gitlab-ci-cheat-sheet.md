# GitLab CI/CD Cheat Sheet for New Joiners

Welcome to your quick-reference guide to GitLab CI/CD! This cheat sheet is designed to help you understand the most important GitLab CI/CD concepts, directives, and real-world examples in one place. Ideal for beginners and new team members.

---

## 🧩 1. Stages

**Purpose**: Define phases of the pipeline.

**Directive**:

```yaml
stages:
  - build
  - test
  - deploy
```

**Example**:
In an e-commerce app, you may build Docker images, test payment services, and deploy to staging or production.

---

## 🔨 2. Jobs

**Purpose**: Define the tasks in each stage.

**Directive**:

```yaml
build_app:
  stage: build
  script:
    - npm install
    - npm run build
```

**Example**:
A job to compile frontend code before packaging it into a Docker image.

---

## 🚀 3. Pipeline Triggering

**Purpose**: Automatically trigger on events.

**Default**: Triggered on push, merge request, etc.

**Example**:
When a developer pushes code to the `main` branch, a pipeline runs automatically.

---

## 🏃 4. Runners

**Purpose**: Execute jobs on GitLab Runner (shared or custom).

**Directive**:

```yaml
tags: [custom-runner]
```

**Example**:
A self-managed runner deployed in a secure cloud environment for sensitive data.

---

## 🔐 5. Environment Variables

**Purpose**: Configure settings dynamically.

**Directive**:

```yaml
variables:
  NODE_ENV: production
```

**Example**:
Use `NODE_ENV=production` to differentiate between test and prod builds.

---

## 🛡️ 6. Secret Masking

**Purpose**: Protect sensitive values.

**Setup**: Configure in GitLab UI → CI/CD → Variables → Masked.

**Example**:
Mask AWS access keys during deployment.

---

## ⚙️ 7. `before_script`

**Purpose**: Run setup steps before job.

**Directive**:

```yaml
before_script:
  - npm install
```

**Example**:
Install dependencies before running tests.

---

## 🧪 8. Testing & Reports

**Purpose**: Execute and collect test results.

**Directive**:

```yaml
artifacts:
  reports:
    junit: test-results.xml
```

**Example**:
Publish unit test results from Jest or Mocha.

---

## 📈 9. Code Coverage

**Purpose**: Show coverage % in GitLab UI.

**Directive**:

```yaml
coverage: '/TOTAL\s+\d+\s+\d+\s+(\d+%)/'
```

**Example**:
Display how much of the backend logic is covered by unit tests.

---

## 🧰 10. Services (e.g., DBs)

**Purpose**: Attach DB or services to jobs.

**Directive**:

```yaml
services:
  - postgres:latest
```

**Example**:
Run integration tests using a temporary PostgreSQL DB.

---

## 📦 11. Caching

**Purpose**: Speed up jobs by reusing data.

**Directive**:

```yaml
cache:
  paths:
    - node_modules/
```

**Example**:
Avoid re-downloading packages for every pipeline.

---

## 🐳 12. Docker Build & Push

**Purpose**: Build & deploy container images.

**Directive**:

```yaml
script:
  - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME .
  - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
```

**Example**:
Push microservice container to GitLab Container Registry.

---

## 🌍 13. Environments

**Purpose**: Identify deployment target.

**Directive**:

```yaml
environment:
  name: staging
```

**Example**:
Use different K8s namespaces for staging vs production.

---

## ✋ 14. Manual Deployments

**Purpose**: Require approval before continuing.

**Directive**:

```yaml
when: manual
```

**Example**:
Promote to production only after QA signs off.

---

## ☸️ 15. Kubernetes Deployments

**Purpose**: Automate app deployment to K8s.

**Example Job**:

```yaml
script:
  - kubectl apply -f k8s/deployment.yaml
```

**Example**:
Deploy a Helm chart or manifest to a cluster from pipeline.

---

## 🎢 16. Parallel Execution

**Purpose**: Speed up tasks using multiple workers.

**Directive**:

```yaml
parallel:
  matrix:
    - NODE_VERSION: [14, 16]
```

**Example**:
Test a NodeJS app against multiple versions of Node.

---

## 🔗 17. Job Dependencies

**Purpose**: Define job sequence across stages.

**Directive**:

```yaml
needs: [build_app]
```

**Example**:
Only test the app if the build was successful.

---

## ⏱️ 18. Timeouts

**Purpose**: Stop jobs that take too long.

**Directive**:

```yaml
timeout: 10 minutes
```

**Example**:
Prevent infinite loops in e2e test scripts.

---

## 🧠 19. Rules

**Purpose**: Run jobs based on conditions.

**Directive**:

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
```

**Example**:
Only deploy if the commit is to `main` branch.

---

## 🧩 20. Reusable Job Templates

**Purpose**: Avoid duplication.

**Directive**:

```yaml
extends: .base_job
```

**Example**:
Reuse the same deploy steps for staging, QA, and prod.

---

## 🔍 21. Security Testing

**Purpose**: Add SAST, DAST, Secret Scanning.

**Directive**:

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
```

**Example**:
Scan for common code vulnerabilities in every MR.

---

## 📣 22. Notifications

**Purpose**: Alert on job status.

**Example**:
Send Slack message using webhook after deployment.

---

## 🕐 23. Scheduled Pipelines

**Purpose**: Trigger pipeline at intervals.

**Setup**: GitLab UI → CI/CD → Schedules

**Example**:
Run database backup every night at 2 AM.

---

## ✅ 24. Auto DevOps

**Purpose**: Use GitLab's pre-configured pipeline.

**Setup**: GitLab UI → Enable Auto DevOps

**Example**:
Auto-detect language and deploy app with zero config.

---

# 🛰️ GitLab CI/CD Cheat Sheet – Solar System NodeJS Project

## 1. 📜 `workflow` – Controlling Pipeline Execution

```yaml
workflow:
  name: Solar System NodeJS Pipeline
  rules:
    - if: $CI_COMMIT_BRANCH == 'main' || $CI_COMMIT_BRANCH =~ /^feature/
      when: always
    - if: $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME =~ /^feature/ && $CI_PIPELINE_SOURCE == 'merge_request_event'
      when: always
```

👨‍💻 **Scenario:**  
- Developer creates `feature/add-auth` → pipeline runs.  
- Push to `main` → pipeline runs.  
- Push to `hotfix/urgent-fix` → pipeline **skipped**.

---

## 2. 🧱 `stages` – Defining Pipeline Steps

```yaml
stages:
  - test
  - reporting
  - containerization
  - dev-deploy
  - stage-deploy
```

### Stages:
1. `test`: Run unit tests  
2. `reporting`: Generate reports  
3. `containerization`: Build Docker image  
4. `dev-deploy`: Deploy to development  
5. `stage-deploy`: Manual deploy to staging  

---

## 3. 📦 `include` – Reusing Configurations

```yaml
include:
  - local: 'template/aws-reports.yml'
```

📁 Use shared templates for Slack alerts, scanning, etc.

---

## 4. ⚙️ `variables` – Setting Environment Variables

```yaml
variables:
  DOCKER_USERNAME: siddharth67
  IMAGE_VERSION: $CI_PIPELINE_ID
  K8S_IMAGE: $DOCKER_USERNAME/solar-system:$IMAGE_VERSION
  MONGO_URI: 'mongodb+srv://supercluster...'
  MONGO_USERNAME: superuser
  MONGO_PASSWORD: $M_DB_PASSWORD
```

🔐 Store secrets in GitLab → Settings → CI/CD → Variables.

---

## 5. 🧰 `.prepare_nodejs_environment` – Common Job Template

```yaml
.prepare_nodejs_environment:
  image: node:17-alpine3.14
  services:
    - name: siddharth67/mongo-db:non-prod
      alias: mongo
  before_script:
    - npm install
```

🎯 Use `extends:` to inherit this setup in jobs.

---

## 6. ✅ `unit_testing` – Running Tests and Collecting Results

```yaml
unit_testing:
  stage: test
  extends: .prepare_nodejs_environment
  script:
    - npm test
  artifacts:
    reports:
      junit: test-results.xml
```

🧪 View test results in GitLab UI.

---

## 7. 📊 `reporting` – Custom Reporting or Alerts

```yaml
reporting:
  stage: reporting
  tags:
    - docker
    - linux
    - aws
```

📤 Push metrics or test results to S3, notify teams, etc.

---

## 8. 🔐 Containerization Stages (Commented)

Jobs like:
- `docker_build`: Builds and saves `.tar`
- `docker_test`: Loads and tests image
- `docker_push`: Pushes to Docker Hub

💡 Automate end-to-end container workflow.

---

## 9. ☁️ Kubernetes Deployment (Dev and Stage)

```yaml
environment:
  name: development
  url: https://$INGRESS_URL
```

### `k8s_dev_deploy`: Auto deploys  
### `k8s_stage_deploy`: Manual trigger

```bash
kubectl -n $NAMESPACE create secret generic mongo-db-creds --from-literal=MONGO_URI=$MONGO_URI --from-literal=MONGO_USERNAME=$MONGO_USERNAME --from-literal=MONGO_PASSWORD=$MONGO_PASSWORD
```

🔐 Store DB secrets securely.

---

## 10. 🧪 Integration Testing in Kubernetes

```bash
curl -s -k https://$INGRESS_URL/live | jq -r .status | grep -i live
```

📡 Check health post-deployment.

---

## ✅ Summary for New Joiners

| Section           | Purpose            | What You Do                     |
|------------------|--------------------|----------------------------------|
| `workflow`        | Control triggers   | Define branch/MR rules          |
| `stages`          | Define pipeline    | Order job execution             |
| `include`         | Reuse logic        | DRY for templates               |
| `variables`       | Set configs        | Use GitLab CI/CD Variables      |
| `extends`         | Share setup        | Common environment for jobs     |
| `artifacts`       | Save outputs       | Store test/report files         |
| `docker_*`        | Container lifecycle| Build, test, push images        |
| `k8s_*`           | Deployment         | Auto/manual K8s deployment      |
| `integration_test`| Health check       | Verify deployment works         |


