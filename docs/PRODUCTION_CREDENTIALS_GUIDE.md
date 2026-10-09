# JISR Arabic (فهيم) — Production Credentials & SaaS Integrations Guide
## Enterprise Hardening for 10,000+ Students & 1,000 Concurrent Users

This document provides the operational runbook for provisioning, configuring, and verifying the third-party Software-as-a-Service (SaaS) integrations required for production operation in the UAE.

---

## 1. Credentials Checklist & Diagnostic Tool

Before routing production school traffic, run the automated diagnostic probe to verify all credentials:
```bash
# Offline syntax & format verification
python -m backend.scripts.verify_production_readiness --skip-network

# Live network handshake verification
python -m backend.scripts.verify_production_readiness --verbose
```

| Integration | Primary Environment Variables | UAE Data Residency Notes |
| :--- | :--- | :--- |
| **Object Storage & CDN** | `STORAGE_BACKEND`, `S3_BUCKET_NAME`, `S3_REGION_NAME`, `S3_CDN_DOMAIN`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS S3 in `me-central-1` (UAE) or Cloudflare R2 (UAE jurisdiction). |
| **Transactional Email** | `FAHIM_SMTP_HOST`, `FAHIM_SMTP_PORT`, `FAHIM_SMTP_USER`, `FAHIM_SMTP_PASS`, `FAHIM_SMTP_FROM` | Amazon SES in `me-central-1` (UAE) or Postmark EU/UAE. |
| **Payment Gateway** | `FAHIM_PAYMENT_PROVIDER`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `FAHIM_PAYMENT_WEBHOOK_SECRET` | Stripe Payments (UAE entity / AED currency) or Tap Payments GCC. |
| **Educational AI** | `GEMINI_API_KEY` | Google Gemini 2.5 Flash with MoE pedagogical guardrails. |
| **Database & Cache** | `DATABASE_URL`, `REDIS_URL` | Multi-AZ Aurora PostgreSQL & ElastiCache Redis in `me-central-1`. |

---

## 2. Amazon SES (Simple Email Service) Setup (`me-central-1`)

JISR Arabic uses transactional email for non-repudiable OTP signups, password resets, and invoice delivery.

### 2.1 Domain Verification & Anti-Spam Records (DNS)
In your DNS management console (Route 53 or Cloudflare for `jisr.ae`), configure:

1. **DKIM Records:**
   In AWS SES console (`me-central-1`), add your domain `jisr.ae` and enable Easy DKIM. Add the 3 generated CNAME records:
   ```text
   <token1>._domainkey.jisr.ae -> <token1>.dkim.amazonses.com
   <token2>._domainkey.jisr.ae -> <token2>.dkim.amazonses.com
   <token3>._domainkey.jisr.ae -> <token3>.dkim.amazonses.com
   ```
2. **SPF Record:**
   Add or update your TXT record on `jisr.ae`:
   ```text
   v=spf1 include:amazonses.com ~all
   ```
3. **DMARC Record:**
   Add TXT record for `_dmarc.jisr.ae`:
   ```text
   v=DMARC1; p=reject; rua=mailto:dmarc-reports@jisr.ae; pct=100
   ```

### 2.2 SMTP Credentials Generation
1. In the SES Console, navigate to **Account dashboard** -> **SMTP settings**.
2. Click **Create SMTP credentials**.
3. AWS generates an IAM user (`ses-smtp-user.jisr`) and displays:
   - **SMTP Host:** `email-smtp.me-central-1.amazonaws.com`
   - **SMTP Port:** `587` (STARTTLS)
   - **SMTP Username:** `AKIA...`
   - **SMTP Password:** `B...` (SES-derived password)
4. Update your container environment:
   ```bash
   FAHIM_SMTP_HOST=email-smtp.me-central-1.amazonaws.com
   FAHIM_SMTP_PORT=587
   FAHIM_SMTP_USER=AKIA...
   FAHIM_SMTP_PASS=B...
   FAHIM_SMTP_FROM=noreply@jisr.ae
   ```

---

## 3. Stripe Payments Setup (UAE / GCC AED Support)

JISR Arabic uses provider-hosted checkout sessions (Stripe Checkout) to maintain PCI-DSS SAQ-A compliance with zero cardholder data on application servers.

### 3.1 Stripe API Keys
1. In the Stripe Dashboard, navigate to **Developers** -> **API keys**.
2. Retrieve:
   - **Publishable Key:** `pk_live_...`
   - **Secret Key:** `sk_live_...` (or create a Restricted Key with permissions limited to `Charges: Write`, `Checkout Sessions: Write`, `Customers: Write`).

### 3.2 Webhook Configuration
1. In the Stripe Dashboard, go to **Developers** -> **Webhooks** -> **Add destination**.
2. Configure:
   - **Endpoint URL:** `https://api.jisr.ae/api/payments/webhook`
   - **Events to listen for:**
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `charge.refunded`
3. Click **Add endpoint** and reveal the **Signing secret** (`whsec_...`).
4. Set in your environment:
   ```bash
   FAHIM_PAYMENT_PROVIDER=stripe
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   FAHIM_PAYMENT_WEBHOOK_SECRET=whsec_...
   ```

---

## 4. Object Storage & CloudFront CDN Setup (Audio & PDFs)

To ensure zero container disk dependencies and high-speed audio playback across UAE classrooms:

### 4.1 S3 Bucket Configuration (`me-central-1`)
1. Create private bucket: `jisr-prod-assets-ae` in `me-central-1`.
2. Enable **Versioning** and **Server-side encryption** (SSE-S3).
3. Enable **Block All Public Access** (Traffic is served exclusively through CloudFront OAC).

### 4.2 CloudFront Distribution
1. Create a CloudFront distribution pointing to `jisr-prod-assets-ae.s3.me-central-1.amazonaws.com`.
2. Select **Origin access control settings (recommended)** to sign requests.
3. Configure Alternate domain name (CNAME): `cdn.jisr.ae`.
4. Configure S3 bucket policy allowing `cloudfront.amazonaws.com` read access.
5. Set environment variables:
   ```bash
   STORAGE_BACKEND=s3
   S3_BUCKET_NAME=jisr-prod-assets-ae
   S3_REGION_NAME=me-central-1
   S3_CDN_DOMAIN=cdn.jisr.ae
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   ```

---

## 5. Production Audio Pre-Warming Execution

Before launching a new academic term, execute the audio pre-warming utility to pre-generate all **1,787 curriculum phrases** across Grades 1–12 into the S3 bucket:

```bash
# 1. Verify scan count (dry-run)
python -m backend.scripts.prewarm_audio --grades all --term all --dry-run

# 2. Run full multi-grade synthesis & S3 upload
python -m backend.scripts.prewarm_audio --grades all --term all
```

### Why Pre-Warming is Mandatory:
- **Zero School-Hour TTS Latency:** Students streaming audio receive direct HTTP 307 redirects to CloudFront edge nodes (<25ms playback latency).
- **Cost Elimination:** External TTS synthesis APIs are invoked only once during pre-warming, avoiding hundreds of thousands of live API calls during peak hours.
- **Fail-Safe Reliability:** Even during internet transit drops or third-party TTS outages, all classroom audio files remain permanently cached and accessible.

---

## 6. Google Gemini AI API Configuration

1. In [Google AI Studio](https://aistudio.google.com/), create an API key (`AIzaSy...`).
2. Set in environment:
   ```bash
   GEMINI_API_KEY=AIzaSy...
   ```
3. The platform leverages `gemini-2.5-flash` with pinned pedagogical guardrails to assist non-native Arabic students without deviating from UAE Ministry of Education curriculum guidelines.
