#!/usr/bin/env bash
set -euo pipefail

LOCAL_IMAGE_REPOSITORY="privacydashboard-demo-test"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-local}"
LOCAL_APP_IMAGE="${LOCAL_IMAGE_REPOSITORY}:${IMAGE_TAG}"

echo "Building local test image ${LOCAL_APP_IMAGE}"
docker build \
  -f docker/Dockerfile.deploy \
  -t "${LOCAL_APP_IMAGE}" \
  .

echo "Image built successfully."
