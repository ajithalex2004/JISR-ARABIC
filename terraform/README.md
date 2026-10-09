# JISR Arabic (فهيم) — Cloud Infrastructure as Code (Terraform)
## Enterprise Multi-AZ Architecture in AWS UAE (`me-central-1`)
### Capacity: 10,000+ Students | 1,000 Concurrent Users (CCU)

This directory contains the production-grade Infrastructure as Code (IaC) configuration for deploying JISR Arabic on Amazon Web Services (AWS) in the UAE region (`me-central-1`), strictly complying with **UAE Personal Data Protection Law (PDPL Federal Decree-Law No. 45/2021)** and the **UAE Ministry of Education (MoE)** digital curriculum guidelines.

---

## 1. Architectural Topology Overview

```text
[ Client Tier: React Web & Flutter Mobile ]
                     │
                     ▼ HTTPS (TLS 1.3)
      [ Cloudflare / CloudFront CDN & WAF ]
          │                           │
          │ (Audio / Static Assets)   │ (Dynamic API Traffic)
          ▼                           ▼
[ S3 Assets: me-central-1 ]     [ Application Load Balancer (ALB) ]
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼ (Private Compute Subnets)               ▼
       [ FastAPI Replica 1 ]                     [ FastAPI Replica 2..6 ]
       (ECS Fargate Auto-Scaled)                 (ECS Fargate Auto-Scaled)
                 │                                         │
        ┌────────┴───────────────────┬─────────────────────┴────────┐
        ▼                            ▼                              ▼
 [ Amazon RDS Proxy ]    [ ElastiCache Redis 7 ]           [ Standalone Worker ]
 (PgBouncer Pooling)     (Multi-AZ Replication)            (backend.tasks.worker)
        │
        ▼ (Port 5432)
 [ Amazon Aurora PostgreSQL 16 ]
 (Multi-AZ Cluster + 35-Day PITR)
```

---

## 2. Infrastructure Modules

| Module | Location | Managed AWS Resources |
| :--- | :--- | :--- |
| **`vpc`** | [`modules/vpc/`](./modules/vpc) | Multi-AZ VPC, 3 Public Subnets, 3 Private Compute Subnets, 3 Isolated DB Subnets, 2 NAT Gateways, Internet Gateway, Security Groups. |
| **`secrets`** | [`modules/secrets/`](./modules/secrets) | AWS Secrets Manager secrets, Random 32-char DB password, Random 64-char JWT secret key. |
| **`storage`** | [`modules/storage/`](./modules/storage) | Private S3 assets bucket (`jisr-prod-assets-ae`), Versioning, SSE-S3 Encryption, CloudFront Origin Access Control (OAC), CloudFront CDN Distribution. |
| **`database`** | [`modules/database/`](./modules/database) | Amazon Aurora PostgreSQL 16 (Multi-AZ 1 Writer + 1 Reader), 35-day continuous PITR WAL archiving, Amazon RDS Proxy connection pooler (PgBouncer mode). |
| **`redis`** | [`modules/redis/`](./modules/redis) | Amazon ElastiCache for Redis 7 (Multi-AZ with automatic failover), Redis Parameter Group with `volatile-lru` eviction policy. |
| **`ecs`** | [`modules/ecs/`](./modules/ecs) | Amazon ECR repositories (`jisr/api`, `jisr/worker`), ECS Fargate Cluster, Application Load Balancer (ALB), Target Group with `/api/health` probes, Auto-Scaling Policies (CPU > 70% & RequestCount > 300). |

---

## 3. Prerequisites

1. **AWS CLI v2** installed and configured with administrator credentials:
   ```bash
   aws configure
   # Ensure AWS Region is set to me-central-1 (UAE)
   ```
2. **Terraform CLI** (v1.5.0 or later):
   ```bash
   terraform -version
   ```
3. **Docker Engine**:
   Required to build and push container images to Amazon ECR.

---

## 4. Step-by-Step Deployment Guide

### Step 1: Initialize Configuration
Copy the production variables example:
```bash
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars` with your target domain (`jisr.ae`) and subdomains.

### Step 2: Initialize Terraform
```bash
terraform init
```

### Step 3: Generate Execution Plan
```bash
terraform plan -out=tfplan
```
Review the proposed plan to verify all resources, subnets, and security groups.

### Step 4: Apply Infrastructure
```bash
terraform apply tfplan
```
Once complete, Terraform outputs the **ALB DNS Name**, **CloudFront CDN Domain**, **RDS Proxy Endpoint**, and **ECR URLs**.

---

## 5. Post-Provisioning Deployment Workflow

### Step 5: Build and Push Docker Images to ECR
Authenticate Docker with your newly provisioned ECR registry:
```bash
# Get ECR login token
aws ecr get-login-password --region me-central-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com

# Build and push API image
docker build -t <YOUR_ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com/jisr-arabic/api:latest -f Dockerfile .
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com/jisr-arabic/api:latest

# Build and push Worker image
docker build -t <YOUR_ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com/jisr-arabic/worker:latest -f Dockerfile .
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com/jisr-arabic/worker:latest
```

### Step 6: Populate Live Secrets
Update AWS Secrets Manager with live production credentials:
```bash
aws secretsmanager put-secret-value \
    --secret-id "jisr-arabic/production/app-secrets" \
    --secret-string '{
        "FAHIM_SECRET_KEY": "YOUR_GENERATED_SECRET",
        "FAHIM_PAYMENT_WEBHOOK_SECRET": "whsec_LIVE_STRIPE_WEBHOOK_SECRET",
        "STRIPE_SECRET_KEY": "sk_live_LIVE_STRIPE_SECRET",
        "STRIPE_PUBLISHABLE_KEY": "pk_live_LIVE_STRIPE_KEY",
        "GEMINI_API_KEY": "AIzaSy_YOUR_LIVE_GEMINI_KEY",
        "FAHIM_SMTP_HOST": "email-smtp.me-central-1.amazonaws.com",
        "FAHIM_SMTP_PORT": "587",
        "FAHIM_SMTP_USER": "YOUR_SES_SMTP_USER",
        "FAHIM_SMTP_PASS": "YOUR_SES_SMTP_PASSWORD",
        "FAHIM_SMTP_FROM": "noreply@jisr.ae"
    }'
```

### Step 7: Apply Migrations & Pre-Warm Audio Assets
1. Execute database migrations using an ECS one-off task or local migration runner connected to the RDS Proxy:
   ```bash
   python -m backend.migrations upgrade
   ```
2. Execute the audio pre-warming engine to generate and upload the 1,787 curriculum phrases directly to the production S3 bucket:
   ```bash
   python -m backend.scripts.prewarm_audio --grades 1 2 3 4 5 6 7 8 9 10 11 12 --terms 1 2 3 --concurrency 8
   ```

### Step 8: Configure DNS CNAME Records
In your DNS provider (Route 53 or Cloudflare):
- CNAME `api.jisr.ae` -> `<ALB_DNS_NAME>`
- CNAME `cdn.jisr.ae` -> `<CLOUDFRONT_DOMAIN_NAME>`

---

## 6. Disaster Recovery & Point-In-Time Recovery (PITR)

Aurora PostgreSQL continuously streams write-ahead logs to S3. To restore the database to any specific second within the 35-day retention window:
```bash
aws rds restore-db-cluster-to-point-in-time \
    --source-db-cluster-identifier jisr-arabic-production-aurora \
    --target-db-cluster-identifier jisr-arabic-restored-cluster \
    --restore-to-time 2026-10-09T02:15:00Z \
    --db-subnet-group-name jisr-arabic-production-db-subnet-group
```
Once the restored cluster is ready, update the RDS Proxy target group or redeploy ECS services to restore operation.
