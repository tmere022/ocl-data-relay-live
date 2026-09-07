#!/bin/bash
set -uo pipefail
DIST=$(mktemp -d)
trap 'rm -rf "$DIST"' EXIT
TAG=diagnostic-$(date -u +%Y%m%d-%H%M%S)
set +e
python scripts/fetch_ocl.py --output "$DIST" --repository "$GITHUB_REPOSITORY" --tag "$TAG" > last-run.log 2>&1
CODE=$?
set -e
printf '\ndownloader_exit_code=%s\n' "$CODE" >> last-run.log
exit 0
