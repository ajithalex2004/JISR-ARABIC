# JISR Arabic (فهيم) — CI/CD Pipeline Runbook
**Target Infrastructure:** AWS UAE (`me-central-1`), GitHub Actions, Google Play Store, Apple App Store  
**Target Scale:** 10,000+ Active Students | 1,000 Concurrent Users (CCU)  
**Security Standard:** Strict HTTPS (`https://api.jisr.ae`), Zero-Cleartext, Automated Migrations, Zero-Downtime Rolling Updates

---

## 1. Pipeline Overview & Topology

The JISR Arabic CI/CD automation pipeline is architected into three specialized, hardened workflows within `.github/workflows/`:

```
                             [ Developer Commit / PR ]
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │  .github/workflows/ci.yml               │
                    │  -------------------------------------  │
                    │  1. Backend (Python 3.13, 72 Tests)     │
                    │  2. Frontend (Node 20, Vite Build)      │
                    │  3. Mobile (Flutter Analyze & Tests)    │
                    │  4. Terraform (Format & Validation)     │
                    │  5. Docker (Multi-stage image test)     │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
         [ Push to 'main' ]                         [ Tag 'v*.*.*' ]
                    │                                         │
                    ▼                                         ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│ .github/workflows/deploy.yml          │ │ .github/workflows/release_mobile.yml  │
│ ------------------------------------- │ │ ------------------------------------- │
│ 1. Build & Push ECR Images            │ │ 1. Sign & Build Android App Bundle    │
│ 2. Run Database Migrations            │ │    (.aab) & Release APK (.apk)        │
│ 3. Rolling Update ECS Fargate Tasks   │ │ 2. Build iOS Archive (.ipa)           │
│ 4. Sync Web Frontend to S3 & CloudFront││ 3. Deploy to Google Play / TestFlight │
│ 5. Automated Health Smoke Verification│ │ 4. Publish Tagged GitHub Release      │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 2. Workflows Reference

### 2.1 Continuous Integration (`ci.yml`)
* **Trigger:** Pushes and pull requests to `main`, `master`, and `staging`.
* **Execution Matrix:**
  1. **`backend-ci`:** Installs dependencies from [`backend/requirements.txt`](file:///c:/JISR%20ARABIC/backend/requirements.txt), validates Python bytecode syntax (`compileall`), verifies migration engine status, runs offline SaaS configuration audit, and executes all **72 enterprise regression unit tests** across all 10 test suites in under 30 seconds.
  2. **`frontend-ci`:** Runs TypeScript type checks (`npx tsc --noEmit`) and compiles the production React 19 / Vite bundle to `dist/`.
  3. **`mobile-ci`:** Sets up Java 17 and Flutter stable, resolves dependencies, executes `flutter analyze` enforcing **zero warnings**, and executes all **15 mobile tests** (including endpoint pinning and layout tests).
  4. **`terraform-ci`:** Verifies Terraform formatting (`terraform fmt -check`) and validates syntax across all modules in [`terraform/`](file:///c:/JISR%20ARABIC/terraform).
  5. **`docker-ci`:** Tests container compilation for both [`Dockerfile`](file:///c:/JISR%20ARABIC/Dockerfile) (Backend/Workers) and [`Dockerfile.frontend`](file:///c:/JISR%20ARABIC/Dockerfile.frontend) (Nginx/React SPA).

### 2.2 Continuous Deployment (`deploy.yml`)
* **Trigger:** Push to `main` or manual trigger via **Run workflow** (`workflow_dispatch`).
* **Execution Flow:**
  1. **Build & Push:** Compiles multi-stage production Docker images tagged with git short SHA and `latest`, then pushes to Amazon ECR in `me-central-1`.
  2. **Database Migrations:** Applies pending PostgreSQL schema migrations (`python -m backend.migrations run`) before updating services to prevent runtime schema mismatches.
  3. **ECS Rolling Update:** Issues zero-downtime updates to AWS ECS Fargate services (`jisr-backend-service` and `jisr-worker-service`) and waits for task stability.
  4. **Static Frontend CDN:** Syncs compiled Vite bundle to S3 and triggers an invalidation (`/*`) on CloudFront.
  5. **Live Verification:** Automatically queries `https://api.jisr.ae/api/health` and posts a summary to GitHub.

### 2.3 Mobile Store Release (`release_mobile.yml`)
* **Trigger:** Tag push matching `v*` (e.g. `v2.4.0`) or manual execution via `workflow_dispatch`.
* **Deliverables:**
  - Google Play App Bundle: `app-release.aab` (signed with release keystore, obfuscated, debug symbols split).
  - Standalone APK: `app-release.apk` (for QA testing, sideloading, or enterprise MDM).
  - iOS IPA: `JISR-iOS-Release.ipa` (unsigned or signed payload ready for App Store Connect).
  - Automated GitHub Release with changelog notes and downloadable binary assets.

---

## 3. Required GitHub Secrets Configuration

To connect the pipeline to your cloud provider and app store accounts, configure the following secrets under **Settings > Secrets and variables > Actions**:

### 3.1 AWS & Cloud Infrastructure Secrets
| Secret Name | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `AWS_ACCESS_KEY_ID` | IAM User / Deployment Role access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM User / Deployment Role secret | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS Data Residency Region | `me-central-1` (UAE) |
| `DATABASE_URL` | Production PostgreSQL connection string | `postgresql://jisr_admin:pass@jisr-db-proxy...:5432/jisr_production` |
| `ECS_CLUSTER_NAME` | Target Amazon ECS cluster | `jisr-production-cluster` |
| `ECS_SERVICE_NAME` | ECS FastAPI service name | `jisr-backend-service` |
| `ECS_WORKER_SERVICE_NAME` | ECS Task Queue worker service name | `jisr-worker-service` |
| `FRONTEND_S3_BUCKET` | S3 bucket hosting React SPA | `jisr-web-client-prod` |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront Distribution for CDN invalidation | `E1A2B3C4D5E6F7` |

### 3.2 Mobile Release & Signing Secrets
| Secret Name | Description | Example / Instructions |
| :--- | :--- | :--- |
| `ANDROID_KEYSTORE_BASE64` | Base64-encoded release `.jks` file | `cat upload-keystore.jks \| base64 -w 0` |
| `ANDROID_KEY_ALIAS` | Key alias in upload keystore | `jisr_upload` |
| `ANDROID_KEY_PASSWORD` | Password for key alias | Secure password |
| `ANDROID_KEYSTORE_PASSWORD` | Password for keystore file | Secure password |
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | Google Play Console API service account (optional) | Full JSON credentials string |

---

## 4. Operational Runbook Procedures

### 4.1 How to Trigger a Production Deployment
```bash
# Method A: Standard Git Flow (Recommended)
git checkout main
git pull origin main
git merge staging
git push origin main
# -> Automatically triggers .github/workflows/deploy.yml

# Method B: GitHub UI Manual Dispatch
# 1. Navigate to Actions > "JISR Arabic CD (Continuous Deployment)"
# 2. Click "Run workflow"
# 3. Select branch: "main", Run Migrations: "true"
# 4. Click "Run workflow"
```

### 4.2 How to Release a New Mobile Version
```bash
# 1. Update version in mobile/pubspec.yaml
#    e.g. version: 2.4.1+25

# 2. Commit and push version bump:
git add mobile/pubspec.yaml
git commit -m "chore(release): bump mobile version to 2.4.1+25"
git push origin main

# 3. Create and push Git tag:
git tag v2.4.1
git push origin v2.4.1
# -> Automatically triggers .github/workflows/release_mobile.yml
```

### 4.3 Emergency Rollback Procedure
If a production deployment encounters issues:
1. **ECS Backend Rollback:**
   In AWS Console, open **ECS > Clusters > jisr-production-cluster > jisr-backend-service > Deployments**. Select the previous stable task definition and click **Update Service**, or run via AWS CLI:
   ```bash
   aws ecs update-service \
     --cluster jisr-production-cluster \
     --service jisr-backend-service \
     --task-definition jisr-backend-api:<PREVIOUS_REVISION_NUMBER> \
     --force-new-deployment
   ```
2. **Frontend CDN Rollback:**
   To revert the web client, redeploy the previous stable commit using the GitHub Actions manual workflow dispatch, or restore the prior S3 version.
