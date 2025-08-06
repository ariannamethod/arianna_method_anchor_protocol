#!/usr/bin/env bash
# Tail assistant logs from the repository root's log directory

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/log"

mkdir -p "$LOG_DIR"
# Wait for at least one log file to exist before tailing
shopt -s nullglob
log_files=("$LOG_DIR"/*.log)
while [ ${#log_files[@]} -eq 0 ]; do
  echo "Waiting for logs in $LOG_DIR..."
  sleep 1
  log_files=("$LOG_DIR"/*.log)
done
shopt -u nullglob
tail -f "$LOG_DIR"/*.log
