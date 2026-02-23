#!/usr/bin/env bash
set -euo pipefail

DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:?DOCKERHUB_USERNAME is required}"
DOCKERHUB_TOKEN="${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN is required}"

IMAGE_REPOSITORY="privacydashboard-demo"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-local}"
IMAGE_BASE="${DOCKERHUB_USERNAME}/${IMAGE_REPOSITORY}"
LOCAL_IMAGE_REPOSITORY="privacydashboard-demo-test"
LOCAL_APP_IMAGE="${LOCAL_IMAGE_REPOSITORY}:${IMAGE_TAG}"

APP_IMAGE="${IMAGE_BASE}:${IMAGE_TAG}"
LATEST_IMAGE="${IMAGE_BASE}:latest"

echo "Checking local test image ${LOCAL_APP_IMAGE}"
docker image inspect "${LOCAL_APP_IMAGE}" >/dev/null

echo "Tagging ${LOCAL_APP_IMAGE} as ${APP_IMAGE} and ${LATEST_IMAGE}"
docker tag "${LOCAL_APP_IMAGE}" "${APP_IMAGE}"
docker tag "${LOCAL_APP_IMAGE}" "${LATEST_IMAGE}"

echo "Logging in to Docker Hub as ${DOCKERHUB_USERNAME}"
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

echo "Pushing image ${APP_IMAGE}"
docker push "${APP_IMAGE}"

echo "Pushing image ${LATEST_IMAGE}"
docker push "${LATEST_IMAGE}"

echo "Image published successfully."
