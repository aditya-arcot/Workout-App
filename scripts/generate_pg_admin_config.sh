#!/bin/bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR/.."
ENV_DIR="$BASE_DIR/config/env"
ENV_FILE="$ENV_DIR/.env"
SERVERS_FILE="$ENV_DIR/servers.json"
PGPASS_FILE="$ENV_DIR/pgpass"

export $(grep -v '^#' "$ENV_FILE" | xargs)
envsubst < "$SERVERS_FILE".template > "$SERVERS_FILE"
envsubst < "$PGPASS_FILE".template > "$PGPASS_FILE"
chmod 600 "$PGPASS_FILE"
