#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-120}"

printf '\n== Bun Runtime Execution ==\n'
curl -sS --max-time "$TIMEOUT_SECONDS" \
  -X POST "$BASE_URL/agent" \
  -H 'Content-Type: application/json' \
  -d '{"user_input":"Run ./tools/bin/bun --version, then run ./tools/bin/bun -e \"console.log(7*6)\". Return command, exit code, stdout, stderr for each."}'

printf '\n'
