#!/usr/bin/env bash
set -euo pipefail

DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:?DOCKERHUB_USERNAME is required}"
DOCKERHUB_TOKEN="${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN is required}"

PROJECT_NAME="privacy-dashboard-demo"
COMPOSE_FILE="docker/docker-compose-demo.yml"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-/env/privacydashboard-demo.env}"
IMAGE_REPOSITORY="privacydashboard-demo"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-latest}"
APP_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_REPOSITORY}:${IMAGE_TAG}"

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Deploy env file not found: ${DEPLOY_ENV_FILE}" >&2
  exit 1
fi

echo "Logging in to Docker Hub as ${DOCKERHUB_USERNAME}"
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

echo "Pulling image ${APP_IMAGE}"
docker pull "${APP_IMAGE}"

echo "Stopping previous stack ${PROJECT_NAME} and removing demo DB volume (if present)"
APP_IMAGE="${APP_IMAGE}" docker compose \
  -f "${COMPOSE_FILE}" \
  --project-name "${PROJECT_NAME}" \
  --env-file "${DEPLOY_ENV_FILE}" \
  down --remove-orphans -v || true

echo "Starting updated stack ${PROJECT_NAME}"
APP_IMAGE="${APP_IMAGE}" docker compose \
  -f "${COMPOSE_FILE}" \
  --project-name "${PROJECT_NAME}" \
  --env-file "${DEPLOY_ENV_FILE}" \
  up -d --remove-orphans --no-build

echo "Deployment completed."
