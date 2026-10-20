#!/usr/bin/env bash
# Kucuk Prens - Linux derleme betigi.
# Kullanim: scripts/build.sh [classic / ai / all]
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/build.py "$@"
