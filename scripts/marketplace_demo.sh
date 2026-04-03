#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5050}"
TOKEN="${MARKETPLACE_INTEGRATION_TOKEN:-${TOKEN:-}}"

OWNER_EMAIL="${OWNER_EMAIL:-controller.smartotum@example.com}"
DELEGATE_EMAIL="${DELEGATE_EMAIL:-controller.general@example.com}"

APP_SLUG="${APP_SLUG:-demo-camera}"
APP_ID="${APP_ID:-com.marketplace.${APP_SLUG}}"
APP_NAME="${APP_NAME:-Marketplace Demo Camera}"
APP_DESCRIPTION="${APP_DESCRIPTION:-App created by external marketplace}"

PATCHED_TITLE="${PATCHED_TITLE:-Marketplace Demo Camera v2}"
PATCHED_DESCRIPTION="${PATCHED_DESCRIPTION:-Updated by marketplace during the demo}"

usage() {
  cat <<'EOF'
Usage:
  marketplace_demo.sh create
  marketplace_demo.sh patch
  marketplace_demo.sh recreate
  marketplace_demo.sh run

Commands:
  create    Create a marketplace application in the Privacy Dashboard
  patch     Patch title/description of the marketplace application
  recreate  Send the same create request again to show idempotent behavior
  run       Run create -> patch -> recreate in sequence

Environment variables:
  BASE_URL                        default: http://localhost:5050
  MARKETPLACE_INTEGRATION_TOKEN   required unless TOKEN is set
  TOKEN                           fallback token variable
  OWNER_EMAIL                     default: controller.smartotum@example.com
  DELEGATE_EMAIL                  default: controller.general@example.com
  APP_SLUG                        default: demo-camera
  APP_ID                          default: com.marketplace.${APP_SLUG}
  APP_NAME                        default: Marketplace Demo Camera
  APP_DESCRIPTION                 default: App created by external marketplace
  PATCHED_TITLE                   default: Marketplace Demo Camera v2
  PATCHED_DESCRIPTION             default: Updated by marketplace during the demo

Notes:
  - The owner and delegate must already exist as Data Controllers.
  - If you want a guaranteed fresh create demo, change APP_SLUG or APP_ID.
EOF
}

require_token() {
  if [[ -z "${TOKEN}" ]]; then
    echo "Missing marketplace token." >&2
    echo "Export MARKETPLACE_INTEGRATION_TOKEN or TOKEN first." >&2
    exit 1
  fi
}

print_context() {
  cat <<EOF
BASE_URL=${BASE_URL}
APP_ID=${APP_ID}
OWNER_EMAIL=${OWNER_EMAIL}
DELEGATE_EMAIL=${DELEGATE_EMAIL}
EOF
}

create_app() {
  require_token
  echo
  echo "[1/3] CREATE marketplace app"
  print_context

  curl -i -X POST "${BASE_URL}/api/integrations/marketplace/apps" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d "{
      \"id\": \"${APP_ID}\",
      \"name\": \"${APP_NAME}\",
      \"description\": \"${APP_DESCRIPTION}\",
      \"owner_email\": \"${OWNER_EMAIL}\",
      \"delegates_email\": [\"${DELEGATE_EMAIL}\"]
    }"
}

patch_app() {
  require_token
  echo
  echo "[2/3] PATCH marketplace app"
  print_context

  curl -i -X PATCH "${BASE_URL}/api/integrations/marketplace/apps/${APP_ID}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d "{
      \"title\": \"${PATCHED_TITLE}\",
      \"description\": \"${PATCHED_DESCRIPTION}\"
    }"
}

recreate_app() {
  require_token
  echo
  echo "[3/3] RE-CREATE same marketplace app to show idempotency"
  print_context

  curl -i -X POST "${BASE_URL}/api/integrations/marketplace/apps" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d "{
      \"id\": \"${APP_ID}\",
      \"name\": \"${APP_NAME}\",
      \"description\": \"${APP_DESCRIPTION}\",
      \"owner_email\": \"${OWNER_EMAIL}\",
      \"delegates_email\": [\"${DELEGATE_EMAIL}\"]
    }"
}

main() {
  local command="${1:-}"

  case "${command}" in
    create)
      create_app
      ;;
    patch)
      patch_app
      ;;
    recreate)
      recreate_app
      ;;
    run)
      create_app
      echo
      echo "Open the dashboard and refresh Managed Apps."
      patch_app
      echo
      echo "Refresh the selected app details in the dashboard."
      recreate_app
      ;;
    -h|--help|help|"")
      usage
      ;;
    *)
      echo "Unknown command: ${command}" >&2
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
