#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker/docker-compose-demo.yml"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-/env/privacydashboard-test.env}"
export TEST_PROJECT_NAME="privacy-dashboard-demo-test"
export APP_PORT="15050"
export APP_IMAGE="privacydashboard-demo-test:${CI_COMMIT_SHORT_SHA:-local}"
export MARKETPLACE_INGEST_TOKEN="BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4"
export COMPOSE_PROJECT_NAME="${TEST_PROJECT_NAME}"
export FLASK_ENV="testing"
COLLECTION_PATH="backend/testing/tests/Privacy-Dashboard-API.postman_collection_cleaned.json"
HEALTHCHECK_URL="http://app:5050/api/sifis/health"
HEALTHCHECK_RETRIES="${HEALTHCHECK_RETRIES:-60}"
HEALTHCHECK_INTERVAL_SECONDS="${HEALTHCHECK_INTERVAL_SECONDS:-3}"

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Deploy env file not found: ${DEPLOY_ENV_FILE}" >&2
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
docker run --rm \
  --network "${TEST_PROJECT_NAME}_default" \
  -v "$(pwd):/etc/newman" \
  postman/newman:alpine \
  run "/etc/newman/${COLLECTION_PATH}" \
  --env-var "baseURL=http://app:5050" \
  --env-var "marketplace_ingest_token=${MARKETPLACE_INGEST_TOKEN}"

echo "Image tests passed successfully."
