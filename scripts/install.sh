#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v skills >/dev/null 2>&1; then
  exec skills add "${ROOT}" "$@"
fi

exec npx --yes "${SKILLS_NPM_PACKAGE:-skills}" add "${ROOT}" "$@"
