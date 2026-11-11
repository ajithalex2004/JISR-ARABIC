# JISR Arabic on Kubernetes (with SeaweedFS)

These manifests run the same Docker images as Railway, with the files on SeaweedFS.

| Part | Kind | Notes |
| :--- | :--- | :--- |
| `web` | Deployment (2 pods) + Service | The React website (nginx, port 8080). It calls the API on its own domain. |
| `api` | Deployment (2 to 4 pods, autoscaled) + Service | The FastAPI backend. Probes: `/api/health` (process alive) and `/api/ready` (database and Redis reachable). |
| `worker` | Deployment (1 pod) | Background tasks: textbook pages, OCR, AI drafts, audio. |
| `jisr-migrate` | Job | Runs the database migrations and removes demo accounts, once per deploy, before the API rolls out. |
| `redis` | StatefulSet + Service | Cache, rate limits, logouts and the task queue. Only the app's pods can connect to it. |
| `jisr-content` | PersistentVolumeClaim, **SeaweedFS**, ReadWriteMany | Mounted at `/app/content` in the API, worker and migrate pods. Holds the textbook page images, the OCR text, uploaded PDFs and the audio cache. |
| `jisr` | Ingress | `app.jisrarabic.com` goes to web and `api.jisrarabic.com` goes to api, with TLS from cert-manager. |
| Postgres | Managed (recommended), or `components/postgres` | Postgres stays on block storage. Don't put it on SeaweedFS. |

No application code changes are needed. The app already reads its files from
`FAHIM_CONTENT_DIR`, and the SeaweedFS CSI driver presents that folder as a shared filesystem
to every pod.

```
k8s/
├── base/                    the app (kustomize)
│   ├── secrets.env.example  copy to secrets.env (git-ignored) and fill in
│   └── ...
├── components/postgres/     optional in-cluster Postgres
├── overlays/production/     image names and tags; enable components here
└── deploy.sh                build, push, migrate, roll out
```

## 1. What the cluster needs

- Kubernetes 1.27 or later, with a default StorageClass for block volumes (used by Redis and
  the optional Postgres).
- [ingress-nginx](https://kubernetes.github.io/ingress-nginx/), plus
  [cert-manager](https://cert-manager.io) with a ClusterIssuer named `letsencrypt-prod`. If
  you use a different ingress controller or issuer, change the annotations in
  `base/ingress.yaml`.
- SeaweedFS (master, volume and filer servers) and the
  [SeaweedFS CSI driver](https://github.com/seaweedfs/seaweedfs-csi-driver):
  ```bash
  helm repo add seaweedfs-csi-driver https://seaweedfs.github.io/seaweedfs-csi-driver/helm
  helm install seaweedfs-csi-driver seaweedfs-csi-driver/seaweedfs-csi-driver \
    --namespace seaweedfs --set seaweedfsFiler=<filer-service>.<namespace>:8888
  ```
  The chart creates the StorageClass `seaweedfs-storage`. If yours has another name, change
  `storageClassName` in `base/content-pvc.yaml`. Set the SeaweedFS replication to at least
  `001` (two copies) so that losing one disk doesn't lose the textbooks.
- A container registry that the cluster can pull from. On your machine, `docker`, `kubectl`
  and `kustomize` (or kubectl 1.27 or later, which includes it).
- **Postgres:** a managed one (with backups) or `components/postgres`. Its
  `max_connections` must be at least 100. See *Scaling* below.

## 2. First deploy

1. **Secrets.** Copy `base/secrets.env.example` to `base/secrets.env` and fill it in.
   Reuse the **current `FAHIM_SECRET_KEY`** from Railway so existing logins keep working.
   This file is git-ignored; never commit it.
2. **In-cluster Postgres only.** Copy `components/postgres/postgres.env.example` to
   `postgres.env`, then uncomment the `components:` lines in
   `overlays/production/kustomization.yaml`. Point `DATABASE_URL` at
   `postgres:5432` using the same password.
3. **Domains.** If you use different domains, update them in:
   - `base/ingress.yaml`;
   - `FAHIM_CORS_ORIGINS` and `FAHIM_APP_URL` in `base/configmap.yaml`;
   - `API_URL` when you run deploy.sh.
4. **Deploy** from the repository root:
   ```bash
   REGISTRY=registry.example.com/jisr ./k8s/deploy.sh
   ```
   The script:
   1. builds both images, tagged with the git commit;
   2. creates the configuration, secrets, volume and Redis;
   3. runs the migrations and waits for them to finish;
   4. rolls out api, worker and web.

   If the migrations fail, it stops before changing the running app.

## 3. Moving the data from Railway

Do this before the DNS switch. Railway keeps serving users until step 4.

1. **Database.** Copy it:
   ```bash
   pg_dump -Fc -f jisr.dump "<Railway DATABASE_URL>"
   pg_restore --no-owner --no-acl -d "<new DATABASE_URL>" jisr.dump
   ```
   Then run `./k8s/deploy.sh` again, with `SKIP_BUILD=1` and the same `TAG`, so the
   migrations check the restored schema. Delete `jisr.dump` afterwards: it contains
   children's personal data.
2. **Textbook files** (`pdf_pages_sample/` and `vision-output-new/`, about 2.8 GB) go onto the
   SeaweedFS volume. Option A uses the same upload script as Railway, sent to the new API
   through a port-forward:
   ```bash
   kubectl -n jisr port-forward svc/api 8000:8000
   python scripts/upload_content.py --api http://localhost:8000
   ```
   Option B mounts the SeaweedFS filer on a machine that has the folders, or uses
   `weed filer.copy`, and copies them into the PVC's folder. The files must end up owned by
   user 10001.
3. **Check before the switch.** Point your hosts file at the ingress IP and open
   `https://app.jisrarabic.com`:
   - log in as admin;
   - open a Class 5 lesson and its Reading tab (this checks the page images on SeaweedFS);
   - play a word's audio;
   - check `https://api.jisrarabic.com/api/ready`.
4. **Switch DNS.** In Wix, point `app` and `api` at the ingress load balancer. Then:
   - take one last `pg_dump`/`pg_restore` if users were active during the move;
   - watch the logs (`kubectl -n jisr logs deploy/api -f`);
   - keep Railway running, but idle, for a few days before deleting it.
5. **Stripe**, once payments are live: update the webhook URL if the API domain changed.

## 4. Day-to-day

| Task | Command |
| :--- | :--- |
| Deploy the current commit | `REGISTRY=... ./k8s/deploy.sh` |
| Roll back | `SKIP_BUILD=1 TAG=<previous tag> REGISTRY=... ./k8s/deploy.sh` |
| API logs | `kubectl -n jisr logs deploy/api -f` |
| Worker logs | `kubectl -n jisr logs deploy/worker -f` |
| Migration logs | `kubectl -n jisr logs job/jisr-migrate` |
| Re-import curriculum content (overwrites admin edits to those lessons) | `kubectl -n jisr exec deploy/api -- python -m backend.content_import` |
| Change a setting | Edit `base/configmap.yaml` or `base/secrets.env`, then deploy. kustomize renames the Secret when it changes, so the pods restart and pick it up. |

**Rolling back the code doesn't undo migrations.** They only add things, so older code keeps
working against a newer database.

## 5. Scaling and limits

- **Database connections.** Each API pod runs `WEB_CONCURRENCY=2` processes. Each process
  keeps `DB_POOL_SIZE + DB_MAX_OVERFLOW = 10` connections, so at 4 pods the API uses 80, the
  worker about 10, and a migration a few more. Before raising `maxReplicas` in
  `base/api.yaml`, raise Postgres `max_connections` or add PgBouncer.
- **One worker.** The task queue lives in Redis, so more workers are possible. But textbook
  rendering is memory-heavy, so add workers only when the queue backs up.
- **SeaweedFS speed.** The CSI driver mounts the filer over FUSE. Page images are read often
  and are small, which suits it. If the Reading tab feels slow, add an nginx cache in front of
  the API or move the page images to a CDN later (that needs a code change).
- **Backups.** Postgres needs its own backups (point-in-time recovery for a managed one, or
  scheduled `pg_dump` for the in-cluster one). SeaweedFS needs a replication factor of at
  least 2, or a periodic `weed filer.backup` to another site. The textbook files can be
  re-uploaded from the source folders; generated audio can be rebuilt.
- **Audio through the SeaweedFS S3 gateway (optional).** Instead of keeping audio on the
  shared volume, you can set these in the ConfigMap:
  - `STORAGE_BACKEND=s3`;
  - `S3_ENDPOINT_URL=http://<seaweedfs-s3>:8333`;
  - `S3_BUCKET_NAME`;
  - `S3_CDN_DOMAIN=https://<public-s3-host>/<bucket>`.

  Put the S3 keys in `secrets.env` as `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`. Without
  `S3_CDN_DOMAIN` the app builds amazonaws.com links, and the bucket must be publicly
  readable. The textbook files still need the shared volume either way.
