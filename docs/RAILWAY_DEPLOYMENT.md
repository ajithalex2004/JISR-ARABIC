# JISR Arabic — Deploying to Railway

This replaces the "Docker on a Windows PC + Cloudflare quick tunnel" setup with managed
hosting on a fixed address. Allow about an hour for the first deployment.

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
3. An email sender. Railway blocks outbound SMTP below the Pro plan, so use
   [Resend](https://resend.com) (free tier covers OTP volumes): create an API key and verify
   a sending domain. Resend only delivers to arbitrary parents from a domain you own, so
   either use a domain you already control (for example your company domain) or register
   one for the product now.
4. No product domain is needed to start: the app runs on Railway's own `*.up.railway.app`
   addresses until you buy one (Step 6).

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

# The web service's public address (update after Step 3 and again if you add a custom domain)
FAHIM_CORS_ORIGINS=https://<web-service>.up.railway.app

GEMINI_API_KEY=<your key>

RESEND_API_KEY=<your Resend key>
FAHIM_SMTP_FROM=JISR Arabic <noreply@your-verified-domain>

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

**Settings → Networking → Generate Domain** (target port `8000`).

## Step 3 — Configure the `web` service

**Settings → Config-as-code → Railway config file:** `/railway/web.toml`

**Variables:**

```
NGINX_CONF=nginx/nginx.railway.conf
VITE_API_URL=https://<api-service>.up.railway.app
PORT=8080
```

`VITE_API_URL` is baked in at build time; redeploy the web service whenever it changes.

**Settings → Networking → Generate Domain** (target port `8080`). Put this address into the
api service's `FAHIM_CORS_ORIGINS` (Step 2) and redeploy the api.

## Step 4 — First deploy and health check

Deploy both services. The api runs database migrations on start, then:

- `https://<api-service>.up.railway.app/api/health` → `200`
- `https://<api-service>.up.railway.app/api/ready` → `200` (database and Redis reachable)
- `https://<web-service>.up.railway.app` → the web app loads

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
python scripts\upload_content.py --api https://<api-service>.up.railway.app
```

The Hobby plan allows volumes up to 5 GB, which covers these folders with room to spare.
Delete `.content-upload-progress.json` only if you want to upload everything again.

## Step 6 — Mobile app and domains

**Mobile builds.** The app has no API address built in; it is supplied at build time. In
GitHub → repository **Settings → Secrets and variables → Actions → Variables**, add
`FAHIM_API_BASE` = `https://<api-service>.up.railway.app`. The mobile release workflow refuses
to build without it. For a local build on the PC:

```cmd
cd mobile
flutter build apk --release --dart-define=FAHIM_API_BASE=https://<api-service>.up.railway.app
```

**Your own domain (later).** Railway addresses work indefinitely, but a product domain looks
more trustworthy to schools and lets you move hosts without republishing the app. Once you
own one (say `example.ae`), in each service → **Settings → Networking → Custom Domain** add
`api.example.ae` (api) and `app.example.ae` (web), create the CNAME records Railway shows, then
update `FAHIM_CORS_ORIGINS` on the api, `VITE_API_URL` on the web service and the
`FAHIM_API_BASE` GitHub variable, and release a new app build.

Never point the app at a domain you do not own: whoever controls it would receive users'
logins and children's data.

## Step 7 — Retire the PC setup

Once the Railway app works end to end (sign up, OTP email, lesson, textbook page, Ask Fahim):

1. Stop the Cloudflare tunnel and `docker compose -f docker-compose.prod.yml down` on the PC.
2. Move `.env.production` and the Google service-account key off the PC into Railway variables
   or a password manager.

## Costs (approximate)

Hobby plan USD 5/month includes USD 5 of usage; this stack (api + web + Postgres + Redis +
a small volume) typically runs USD 10–25/month at pilot scale.
