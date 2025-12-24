#!/bin/bash

set -Eeuo pipefail

echo "Generating OpenAPI specification"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/../server"
CLIENT_DIR="$SCRIPT_DIR/../client"
OUT_FILE="$CLIENT_DIR/openapi_spec.json"

cd "$SERVER_DIR"

uv sync > /dev/null 2>&1
source .venv/bin/activate

tmpfile="$(mktemp)"

python3 <<EOF
import json
import app.main

spec = app.main.app.openapi()
with open("$tmpfile", "w") as f:
    json.dump(spec, f, indent=4)
EOF

mv "$tmpfile" "$OUT_FILE"
echo "OpenAPI spec written to $OUT_FILE"

echo "Generating API client code"

cd "$CLIENT_DIR"
npm run generate-api > /dev/null 2>&1

echo "Formatting generated code"

cd ..
npm run format > /dev/null 2>&1
