#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-120}"

printf '\n== Skills Index Discovery ==\n'
curl -sS --max-time "$TIMEOUT_SECONDS" \
  -X POST "$BASE_URL/agent" \
  -H 'Content-Type: application/json' \
  -d '{"user_input":"List available skill names and SKILL.md paths from the skills index only."}'

printf '\n\n== git-github Skill Usage ==\n'
curl -sS --max-time "$TIMEOUT_SECONDS" \
  -X POST "$BASE_URL/agent" \
  -H 'Content-Type: application/json' \
  -d '{"user_input":"Use the git-github skill and provide a concise git/GitHub workflow for feature branch, commit, and PR. Include the SKILL.md path you used."}'

printf '\n'
