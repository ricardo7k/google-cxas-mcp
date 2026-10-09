#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from .env if present
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  # Load non-comment lines
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:-${1:-}}"
SERVICE_NAME="${GCP_SERVICE_NAME:-shows-mcp-server}"
REGION="${GCP_REGION:-us-central1}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Error: GCP_PROJECT_ID is not set."
  echo "Please create a .env file based on .env.example or set GCP_PROJECT_ID in your environment."
  echo "Usage: ./deploy.sh [PROJECT_ID]"
  exit 1
fi

echo "=================================================="
echo "Deploying Shows MCP Server to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region:  $REGION"
echo "=================================================="

# Deploy source code to Cloud Run (Cloud Build automatically builds container)
gcloud run deploy "$SERVICE_NAME" \
  --source "$SCRIPT_DIR" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --allow-unauthenticated

# Retrieve public Cloud Run URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --format='value(status.url)')

echo ""
echo "=================================================="
echo "Deployment completed successfully!"
echo "Cloud Run URL: $SERVICE_URL"
echo ""
echo "Configuration for CX Agent Studio / CES:"
echo "--------------------------------------------------"
echo "Server Address:   ${SERVICE_URL}/mcp/"
echo "Transport:        Streamable HTTP"
echo "Tools available:  list"
echo "=================================================="
