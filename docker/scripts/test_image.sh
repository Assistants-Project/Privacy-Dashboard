#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose-demo.yml"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-/env/privacydashboard-test.env}"
export TEST_PROJECT_NAME="privacy-dashboard-demo-test"
export APP_PORT="15050"
export APP_IMAGE="privacydashboard-demo-test:${CI_COMMIT_SHORT_SHA:-local}"
export MARKETPLACE_INGEST_TOKEN="BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4"
export COMPOSE_PROJECT_NAME="${TEST_PROJECT_NAME}"
# Default to testing, but allow running the same stack/tests in demo mode as well.
export FLASK_ENV="${TEST_FLASK_ENV:-testing}"
COLLECTION_PATH="backend/testing/tests/Privacy-Dashboard-API.postman_collection_cleaned.json"
COLLECTION_FILE="${PROJECT_ROOT}/${COLLECTION_PATH}"
HEALTHCHECK_URL="http://app:5050/api/sifis/health"
HEALTHCHECK_RETRIES="${HEALTHCHECK_RETRIES:-60}"
HEALTHCHECK_INTERVAL_SECONDS="${HEALTHCHECK_INTERVAL_SECONDS:-3}"

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Deploy env file not found: ${DEPLOY_ENV_FILE}" >&2
  exit 1
fi

if [[ ! -f "${COLLECTION_FILE}" ]]; then
  echo "Postman collection not found: ${COLLECTION_FILE}" >&2
  exit 1
fi

cleanup() {
  echo "Cleaning up temporary test stack ${TEST_PROJECT_NAME}"
  docker compose -f "${COMPOSE_FILE}" --env-file "${DEPLOY_ENV_FILE}" down --remove-orphans -v || true
}
trap cleanup EXIT

echo "Starting temporary test stack ${TEST_PROJECT_NAME} on port ${APP_PORT}"
docker compose -f "${COMPOSE_FILE}" --env-file "${DEPLOY_ENV_FILE}" up -d --remove-orphans --no-build

echo "Waiting for app health check"
for _ in $(seq 1 "${HEALTHCHECK_RETRIES}"); do
  if docker run --rm --network "${TEST_PROJECT_NAME}_default" curlimages/curl:8.11.1 -fsS "${HEALTHCHECK_URL}" >/dev/null; then
    echo "Test app is healthy"
    break
  fi
  sleep "${HEALTHCHECK_INTERVAL_SECONDS}"
done

if ! docker run --rm --network "${TEST_PROJECT_NAME}_default" curlimages/curl:8.11.1 -fsS "${HEALTHCHECK_URL}" >/dev/null; then
  echo "Test app failed health check (${HEALTHCHECK_URL})" >&2
  docker compose -f "${COMPOSE_FILE}" --env-file "${DEPLOY_ENV_FILE}" logs --no-color app || true
  exit 1
fi

echo "Running Postman collection with Newman"
NEWMAN_CONTAINER_ID="$(docker create \
  --network "${TEST_PROJECT_NAME}_default" \
  postman/newman:alpine \
  run /etc/newman/collection.json \
  --env-var "baseURL=http://app:5050" \
  --env-var "marketplace_ingest_token=${MARKETPLACE_INGEST_TOKEN}")"

docker cp "${COLLECTION_FILE}" "${NEWMAN_CONTAINER_ID}:/etc/newman/collection.json"

set +e
docker start -a "${NEWMAN_CONTAINER_ID}"
NEWMAN_EXIT_CODE=$?
set -e

docker rm -f "${NEWMAN_CONTAINER_ID}" >/dev/null 2>&1 || true

if [[ "${NEWMAN_EXIT_CODE}" -ne 0 ]]; then
  exit "${NEWMAN_EXIT_CODE}"
fi

echo "Image tests passed successfully."
