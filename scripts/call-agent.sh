#!/bin/bash
# call-agent.sh — Call an agent via OpenCode's serve API
#
# Usage:
#   ./scripts/call-agent.sh <agent-name> "<prompt>"
#   ./scripts/call-agent.sh api-agent "List all available pets from petstore"
#   ./scripts/call-agent.sh nokia-netops-agent "Configure 3 SROS routers with eBGP"

set -euo pipefail

HOST="${OPENCODE_HOST:-http://localhost:4096}"
AGENT="${1:?Usage: call-agent.sh <agent-name> \"<prompt>\"}"
PROMPT="${2:?Usage: call-agent.sh <agent-name> \"<prompt>\"}"

AUTH_HEADER=""
if [ -n "${OPENCODE_SERVER_PASSWORD:-}" ]; then
  AUTH_HEADER="-u ${OPENCODE_SERVER_USERNAME:-opencode}:${OPENCODE_SERVER_PASSWORD}"
fi

echo "==> Creating session..."
SESSION_RESPONSE=$(curl -s -X POST "${HOST}/session" \
  ${AUTH_HEADER} \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"${AGENT}-task\"}")

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.data.id // .id // empty')

if [ -z "$SESSION_ID" ]; then
  echo "ERROR: Failed to create session"
  echo "$SESSION_RESPONSE" | jq . 2>/dev/null || echo "$SESSION_RESPONSE"
  exit 1
fi

echo "==> Session: ${SESSION_ID}"
echo "==> Sending to agent: ${AGENT}"

RESPONSE=$(curl -s -X POST "${HOST}/session/${SESSION_ID}/message" \
  ${AUTH_HEADER} \
  -H "Content-Type: application/json" \
  -d "{
    \"agent\": \"${AGENT}\",
    \"parts\": [{\"type\": \"text\", \"text\": $(echo "$PROMPT" | jq -Rs .)}]
  }")

echo "==> Response:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
