# JISR Arabic — Deploying to Railway

This replaces the "Docker on a Windows PC + Cloudflare quick tunnel" setup with managed
hosting on the product's own domain, **jisrarabic.com** (registered 13 Oct 2026, DNS at Wix).
Allow about an hour for the first deployment, plus up to a few hours for DNS to propagate.

| Address | Serves |
| :--- | :--- |
| `https://api.jisrarabic.com` | API (Railway `api` service); the mobile app's built-in default |
| `https://app.jisrarabic.com` | Web app (Railway `web` service) |
| `noreply@jisrarabic.com` | Sender of OTP and digest emails (Resend) |
| `https://jisrarabic.com` | Left free for a marketing site on Wix |

## What runs where

| Railway service | Built from | Purpose |
| :--- | :--- | :--- |
| **Postgres** | Railway database template | Main database (replaces `jisr_postgres` on the PC) |
| **Redis** | Railway database template | Rate limiting, cache, background task queue |
| **api** | `Dockerfile`, config `/railway/api.toml` | FastAPI backend + in-process background worker, with a volume for textbook scans |
| **web** | `Dockerfile.frontend`, config `/railway/web.toml` | React web app served by nginx; calls the API directly |

The background worker runs inside the `api` service on purpose: textbook page images are
rendered by the worker and served by the API, and a Railway volume can attach to only one
service. Split the worker out later, once page images move to S3/R2 storage.

## Before you start

1. A Railway account on the **Hobby plan or above** (the trial cannot attach volumes long-term).
2. Your current production secrets from `C:\JISR ARABIC\.env.production` (or `backend\.env`).
3. A [Resend](https://resend.com) account for email (Railway blocks outbound SMTP below the
   Pro plan; Resend's free tier covers OTP volumes).
4. Access to the Wix dashboard for jisrarabic.com: **Domains → jisrarabic.com → Manage DNS
   Records**. Every DNS record below is added there.

## Step 1 — Create the project

1. Railway dashboard → **New Project** → **Deploy from GitHub repo** → `ajithalex2004/JISR-ARABIC`.
   This creates one service; rename it to **api**.
2. In the project, **+ New → Database → PostgreSQL**, then **+ New → Database → Redis**.
3. **+ New → GitHub Repo** → the same repository again; rename this service to **web**.

## Step 2 — Configure the `api` service

**Settings → Config-as-code → Railway config file:** `/railway/api.toml`

**Settings → Volumes → Add volume**, mount path: `/app/content`

**Variables** (Raw editor):

```
FAHIM_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Reuse the value from your current .env.production so existing logins keep working
FAHIM_SECRET_KEY=<existing secret, 32+ characters>

# The web app's address. While testing before DNS is live, add its Railway address too,
# comma-separated: https://app.jisrarabic.com,https://<web-service>.up.railway.app
FAHIM_CORS_ORIGINS=https://app.jisrarabic.com

GEMINI_API_KEY=<your key>

RESEND_API_KEY=<your Resend key>
FAHIM_SMTP_FROM=JISR Arabic <noreply@jisrarabic.com>

# Payments are not live yet, but production startup requires these to be set
FAHIM_PAYMENT_PROVIDER=stripe
FAHIM_PAYMENT_WEBHOOK_SECRET=<random string, 24+ characters>

# Textbook scans, OCR output and audio cache live on the volume
FAHIM_CONTENT_DIR=/app/content
FAHIM_AUDIO_CACHE_DIR=/app/content/audio-cache
STORAGE_BACKEND=local

# Railway mounts volumes as root; the image runs as a non-root user
RAILWAY_RUN_UID=0

# Railway's edge proxy sets X-Forwarded-For; trust it for client IPs / rate limits
FORWARDED_ALLOW_IPS=*
STRICT_MIGRATION_CHECK=1
WEB_CONCURRENCY=2
```

Generate random secrets with:
`python -c "import secrets; print(secrets.token_urlsafe(48))"`

To create an admin account on an **empty** database, also set `FAHIM_SEED_DEMO=0`,
`FAHIM_SEED_ADMIN_EMAIL` and `FAHIM_SEED_ADMIN_PASSWORD` — not needed if you restore your
existing database in Step 5.

**Settings → Networking**: **Generate Domain** (target port `8000`) for testing, then
**Custom Domain** → `api.jisrarabic.com` (port `8000`). Note the DNS records Railway shows.

## Step 3 — Configure the `web` service

**Settings → Config-as-code → Railway config file:** `/railway/web.toml`

**Variables:**

```
NGINX_CONF=nginx/nginx.railway.conf
VITE_API_URL=https://api.jisrarabic.com
PORT=8080
```

`VITE_API_URL` is baked in at build time; redeploy the web service whenever it changes.

**Settings → Networking**: **Generate Domain** (target port `8080`) for testing, then
**Custom Domain** → `app.jisrarabic.com` (port `8080`). Note the DNS records Railway shows.

If you want to test before DNS is live, temporarily set `VITE_API_URL` to the api's
`…up.railway.app` address and add the web's Railway address to `FAHIM_CORS_ORIGINS`.

## Step 3b — DNS records in Wix

In Wix → **Manage DNS Records**, add exactly what Railway and Resend show you:

| Purpose | Type | Host name | Value |
| :--- | :--- | :--- | :--- |
| API | CNAME | `api` | the `…railway.app` target Railway shows for `api.jisrarabic.com` |
| Web app | CNAME | `app` | the `…railway.app` target Railway shows for `app.jisrarabic.com` |
| Railway ownership (if shown) | TXT | as shown | as shown |
| Email (Resend → Domains → Add `jisrarabic.com`) | MX, TXT (SPF, DKIM) | as shown, e.g. `send`, `resend._domainkey` | as shown |

Do not change the existing records Wix created for the root domain. Railway issues HTTPS
certificates automatically once the CNAMEs resolve; Resend marks the domain "Verified"
once its records resolve (both usually within an hour).

## Step 4 — First deploy and health check

Deploy both services. The api runs database migrations on start, then:

- `https://api.jisrarabic.com/api/health` → `200`
- `https://api.jisrarabic.com/api/ready` → `200` (database and Redis reachable)
- `https://app.jisrarabic.com` → the web app loads; sign up to confirm the OTP email arrives

## Step 5 — Move your existing data

**Database.** In Railway, open the Postgres service → **Variables** → copy
`DATABASE_PUBLIC_URL`. Then on the PC (Docker Desktop running), in `C:\JISR ARABIC`:

```cmd
docker exec jisr_postgres pg_dump -U jisr_user -d jisr_production -Fc -f /tmp/jisr.dump
docker cp jisr_postgres:/tmp/jisr.dump jisr.dump
docker run --rm -v "%cd%":/backup postgres:16 pg_restore --no-owner --no-acl --clean --if-exists -d "<DATABASE_PUBLIC_URL>" /backup/jisr.dump
```

If your current `DATABASE_URL` points to Neon rather than the local container, replace the
first two commands with
`docker run --rm -v "%cd%":/backup postgres:16 pg_dump -Fc -f /backup/jisr.dump "<current DATABASE_URL>"`.
Redeploy the api afterwards so it re-checks migrations. Delete `jisr.dump` from the PC once
the restore is verified: it contains children's personal data.

**Textbook scans.** The reader needs `pdf_pages_sample/` (page images, ~1.7 GB) and
`vision-output-new/` (OCR, ~1.1 GB) on the api volume at `/app/content`. Upload them from
the PC with the bundled script (admin account required; it sends ~200 MB parts and resumes
if interrupted):

```cmd
pip install requests
python scripts\upload_content.py --api https://api.jisrarabic.com
```

The Hobby plan allows volumes up to 5 GB, which covers these folders with room to spare.
Delete `.content-upload-progress.json` only if you want to upload everything again.

## Step 6 — Mobile app

The app's built-in API address is `https://api.jisrarabic.com`, so release builds need no
extra settings once DNS is live:

```cmd
cd mobile
flutter build apk --release
```

To point a test build elsewhere (for example the Railway address before DNS is ready), add
`--dart-define=FAHIM_API_BASE=https://<api-service>.up.railway.app`. The GitHub mobile release
workflow uses the `api_base` input, then the `FAHIM_API_BASE` repository variable, then the
built-in address.

Users of older builds still pointed at the Cloudflare tunnel must install the new build.

## Step 7 — Retire the PC setup

Once the Railway app works end to end (sign up, OTP email, lesson, textbook page, Ask Fahim):

1. Stop the Cloudflare tunnel and `docker compose -f docker-compose.prod.yml down` on the PC.
2. Move `.env.production` and the Google service-account key off the PC into Railway variables
   or a password manager.

## Costs (approximate)

Hobby plan USD 5/month includes USD 5 of usage; this stack (api + web + Postgres + Redis +
a small volume) typically runs USD 10–25/month at pilot scale.
