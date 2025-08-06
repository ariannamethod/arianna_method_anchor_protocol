#!/usr/bin/env bash
LOG_DIR="$(cd "$(dirname "$0")/../log" && pwd)"

tail -f "$LOG_DIR"/*.log
