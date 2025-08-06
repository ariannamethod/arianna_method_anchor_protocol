#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_TOOLS_DIR="$SCRIPT_DIR/../for-codex-alpine-apk-tools"

if [ ! -d "$APK_TOOLS_DIR" ]; then
  echo "APK tools directory not found: $APK_TOOLS_DIR" >&2
  exit 1
fi

make -C "$APK_TOOLS_DIR"

# Print path to built apk binary
echo "$APK_TOOLS_DIR/src/apk"
