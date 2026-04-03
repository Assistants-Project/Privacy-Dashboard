#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/reset_postgres_and_run.sh [development|testing]

Resets local postgres, applies migrations, and starts the Flask backend on port 5050.

Arguments:
  development   Run with FLASK_ENV=development
  testing       Run with FLASK_ENV=testing

If omitted, the default environment is development.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo "Backend directory not found: ${BACKEND_DIR}" >&2
  exit 1
fi

# Load project env if present.
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_ROOT}/.env"
  set +a
fi

TARGET_ENVIRONMENT="development"
if [[ $# -gt 1 ]]; then
  usage >&2
  exit 1
fi

if [[ $# -eq 1 ]]; then
  case "$1" in
    development|testing)
      TARGET_ENVIRONMENT="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unsupported environment: $1" >&2
      echo >&2
      usage >&2
      exit 1
      ;;
  esac
fi

export FLASK_ENV="${TARGET_ENVIRONMENT}"
export FLASK_APP="${FLASK_APP:-run.py}"

echo "Using project root: ${PROJECT_ROOT}"
echo "Using backend dir: ${BACKEND_DIR}"
echo "FLASK_ENV=${FLASK_ENV}"
echo "FLASK_APP=${FLASK_APP}"

echo
echo "[1/5] Stopping and removing compose resources"
(
  cd "${PROJECT_ROOT}"
  docker compose down -v
)

echo
echo "[2/5] Resetting testing DHT output state"
if [[ "${FLASK_ENV}" == "testing" ]]; then
  find "${PROJECT_ROOT}/backend/testing/data/dht" -type f -name '*_output.json' -print -delete 2>/dev/null || true
else
  echo "Skipping DHT output cleanup because FLASK_ENV=${FLASK_ENV}"
fi

echo
echo "[3/5] Starting postgres"
(
  cd "${PROJECT_ROOT}"
  docker compose up -d postgres
)

echo
echo "[4/5] Applying database migrations"
(
  cd "${BACKEND_DIR}"
  flask db upgrade
)

echo
echo "[5/5] Starting Flask server on port 5050"
cd "${BACKEND_DIR}"
exec flask run --debug --port 5050
