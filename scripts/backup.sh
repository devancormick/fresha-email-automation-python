#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

source venv/bin/activate 2>/dev/null || true

echo "Creating database backup..."
python -m src.cli backup

echo "Backup completed!"
