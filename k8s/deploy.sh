#!/usr/bin/env bash
# Build, push and deploy JISR Arabic to Kubernetes.
#
#   REGISTRY=registry.example.com/jisr ./k8s/deploy.sh            # tag = current git commit
#   REGISTRY=registry.example.com/jisr TAG=v1.2.3 ./k8s/deploy.sh
#   SKIP_BUILD=1 REGISTRY=... TAG=<existing tag> ./k8s/deploy.sh   # redeploy / roll back
#
# Needs docker (logged in to the registry), kubectl (pointed at the cluster) and kustomize
# (or kubectl >= 1.27, which bundles it). Run from the repository root.
set -euo pipefail

: "${REGISTRY:?Set REGISTRY, e.g. registry.example.com/jisr}"
TAG="${TAG:-$(git rev-parse --short HEAD)}"
API_URL="${API_URL:-https://api.jisrarabic.com}"
NAMESPACE="${NAMESPACE:-jisr}"
OVERLAY="k8s/overlays/production"

[ -f k8s/base/secrets.env ] || { echo "Missing k8s/base/secrets.env (copy secrets.env.example and fill it in)"; exit 1; }

if [ "${SKIP_BUILD:-0}" != "1" ]; then
  echo ">> Building images ${TAG}"
  docker build -f Dockerfile -t "${REGISTRY}/api:${TAG}" .
  docker build -f Dockerfile.frontend \
    --build-arg NGINX_CONF=nginx/nginx.railway.conf \
    --build-arg VITE_API_URL="${API_URL}" \
    -t "${REGISTRY}/web:${TAG}" .
  docker push "${REGISTRY}/api:${TAG}"
  docker push "${REGISTRY}/web:${TAG}"
fi

(cd "${OVERLAY}" && kustomize edit set image "jisr-api=${REGISTRY}/api:${TAG}" "jisr-web=${REGISTRY}/web:${TAG}")

MANIFESTS="$(kustomize build "${OVERLAY}")"

echo ">> Phase 1: namespace, config, secrets, volume, Redis, then database migrations"
# A Job can't be updated in place: remove the previous run first.
kubectl -n "${NAMESPACE}" delete job jisr-migrate --ignore-not-found 2>/dev/null || true
echo "${MANIFESTS}" | kubectl apply -l jisr.deploy/phase=pre -f -
kubectl -n "${NAMESPACE}" rollout status statefulset/redis --timeout=300s
if kubectl -n "${NAMESPACE}" get statefulset postgres >/dev/null 2>&1; then
  kubectl -n "${NAMESPACE}" rollout status statefulset/postgres --timeout=300s
fi
if ! kubectl -n "${NAMESPACE}" wait --for=condition=complete job/jisr-migrate --timeout=900s; then
  echo "!! Migrations failed; the running app was not changed. Logs:"
  kubectl -n "${NAMESPACE}" logs job/jisr-migrate --all-containers || true
  exit 1
fi

echo ">> Phase 2: API, worker, website, ingress"
echo "${MANIFESTS}" | kubectl apply -f -

echo ">> Waiting for the rollout"
for d in api worker web; do
  kubectl -n "${NAMESPACE}" rollout status "deployment/${d}" --timeout=600s
done
echo ">> Deployed ${TAG}"
