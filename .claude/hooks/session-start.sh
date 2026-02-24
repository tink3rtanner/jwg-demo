#!/bin/bash
set -euo pipefail

# Only run in remote (cloud) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install Python dependencies for the facade and seed services
pip install --quiet fastapi uvicorn httpx pyyaml

# Ensure ruff linter is available
if ! command -v ruff &> /dev/null; then
  pip install --quiet ruff
fi

# Ensure system tools needed for tests are available
if ! command -v jq &> /dev/null; then
  apt-get update -qq && apt-get install -y -qq jq > /dev/null 2>&1 || true
fi

# Set environment variables for running the facade natively (without Docker)
echo "export CONFIG_PATH=\"${CLAUDE_PROJECT_DIR}/config/config.yaml\"" >> "$CLAUDE_ENV_FILE"
echo "export HAPI_BASE_URL=\"http://localhost:8081/fhir\"" >> "$CLAUDE_ENV_FILE"
echo "export PYTHONPATH=\"${CLAUDE_PROJECT_DIR}\"" >> "$CLAUDE_ENV_FILE"
