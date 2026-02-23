#!/usr/bin/env bash
set -euo pipefail

bash docker/scripts/create_image_local.sh
bash docker/scripts/test_image.sh
bash docker/scripts/push_image.sh
