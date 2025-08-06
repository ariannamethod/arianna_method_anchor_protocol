#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_TOOLS_DIR="$SCRIPT_DIR/apk-tools"

if [ ! -d "$APK_TOOLS_DIR" ]; then
  git clone https://github.com/AriannaMethod/AM-alpine-apk-tools "$APK_TOOLS_DIR"
fi

make -C "$APK_TOOLS_DIR"

# Print path to built apk binary
echo "$APK_TOOLS_DIR/src/apk"
