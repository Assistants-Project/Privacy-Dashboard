#!/usr/bin/env bash
set -euo pipefail

# Defaults for the runner launched in a container:
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-/env/.env.prod}"
APP_IMAGE="${APP_IMAGE:-privacy-dashboard-demo:latest}"
APP_IMAGE_SHA="${APP_IMAGE_SHA:-privacy-dashboard-demo:${CI_COMMIT_SHORT_SHA:-local}}"
COMPOSE_FILE="${COMPOSE_FILE:-docker/docker-compose.deploy.yml}"
PROJECT_NAME="${PROJECT_NAME:-privacy-dashboard-demo}"

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Deploy env file not found: ${DEPLOY_ENV_FILE}" >&2
  exit 1
fi

echo "Building image ${APP_IMAGE_SHA} and ${APP_IMAGE}"
docker build -f docker/Dockerfile.deploy -t "${APP_IMAGE_SHA}" -t "${APP_IMAGE}" .

echo "Deploying stack ${PROJECT_NAME} with env ${DEPLOY_ENV_FILE}"
APP_IMAGE="${APP_IMAGE}" docker compose \
  -f "${COMPOSE_FILE}" \
  --project-name "${PROJECT_NAME}" \
  --env-file "${DEPLOY_ENV_FILE}" \
  up -d --remove-orphans --no-build

echo "Deployment completed."
