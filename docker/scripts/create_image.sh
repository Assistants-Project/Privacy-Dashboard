#!/usr/bin/env bash
set -euo pipefail

DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:?DOCKERHUB_USERNAME is required}"
DOCKERHUB_TOKEN="${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN is required}"

IMAGE_REPOSITORY="privacydashboard-demo"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-local}"
IMAGE_BASE="${DOCKERHUB_USERNAME}/${IMAGE_REPOSITORY}"

echo "Logging in to Docker Hub as ${DOCKERHUB_USERNAME}"
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

echo "Building image ${IMAGE_BASE}:${IMAGE_TAG} and ${IMAGE_BASE}:latest"
docker build \
  -f docker/Dockerfile.deploy \
  -t "${IMAGE_BASE}:${IMAGE_TAG}" \
  -t "${IMAGE_BASE}:latest" \
  .

echo "Pushing image ${IMAGE_BASE}:${IMAGE_TAG}"
docker push "${IMAGE_BASE}:${IMAGE_TAG}"

echo "Pushing image ${IMAGE_BASE}:latest"
docker push "${IMAGE_BASE}:latest"

echo "Image published successfully."
