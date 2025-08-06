#!/usr/bin/env bash
# Tail assistant logs from the repository root's log directory

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/log"

mkdir -p "$LOG_DIR"
tail -f "$LOG_DIR"/*.log
