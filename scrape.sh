#!/bin/bash
set -euo pipefail

TAG=ocl-$(date -u +%Y%m%d-%H%M%S)
DIST=$(mktemp -d)
trap 'rm -rf "$DIST"' EXIT

python scripts/fetch_ocl.py --output "$DIST" --repository "$GITHUB_REPOSITORY" --tag "$TAG"

# actions/checkout persists the job token as a basic-auth extra header.
# Recover it without printing it so gh can publish immutable release assets.
AUTH_B64=$(git config --local --get http.https://github.com/.extraheader | awk '{print $3}')
export GH_TOKEN=$(printf '%s' "$AUTH_B64" | base64 --decode | cut -d: -f2-)

gh release create "$TAG" "$DIST/communications_ocl_cal.zip" "$DIST/registrations_enregistrements_ocl_cal.zip" --repo "$GITHUB_REPOSITORY" --title "OCL snapshot $TAG" --notes "Validated automated snapshot from the official OCL bulk-data URLs."
cp "$DIST/manifest.json" manifest.json

# Keep only the four newest immutable snapshots.
gh release list --repo "$GITHUB_REPOSITORY" --limit 100 --json tagName,createdAt --jq 'sort_by(.createdAt) | reverse | .[4:] | .[].tagName' | while read -r old_tag; do
  [ -n "$old_tag" ] && gh release delete "$old_tag" --repo "$GITHUB_REPOSITORY" --cleanup-tag --yes
done
