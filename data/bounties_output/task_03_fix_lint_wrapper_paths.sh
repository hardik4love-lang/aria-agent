#!/usr/bin/env bash
# Fix wrapper paths in lint tooling package scripts
set -euo pipefail

# Ensure scripts point to localized bin wrapper rather than global symlink
sed -i 's|"lint": "eslint .|"lint": "node_modules/.bin/eslint .|g' package.json
sed -i 's|"typecheck": "tsc |"typecheck": "node_modules/.bin/tsc |g' package.json
echo "Wrapper paths successfully pinned to local node_modules"
