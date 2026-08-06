#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SKILLS_CLI_VERSION="1.5.22"
VERSION="$(tr -d '[:space:]' < "${ROOT}/VERSION")"
ARCHIVE="${ROOT}/dist/rvtf-skills-${VERSION}.tgz"

"${ROOT}/scripts/validate.sh"
PYTHONPATH="${ROOT}/scripts" "${PYTHON_BIN}" -m unittest discover -s "${ROOT}/scripts/tests" -v
"${ROOT}/scripts/package.sh"

(
  cd "${ROOT}/dist"
  shasum -a 256 "rvtf-skills-${VERSION}.tgz" > SHA256SUMS
  shasum -a 256 -c SHA256SUMS
)

SMOKE_DIR="$(mktemp -d)"
trap 'rm -rf "${SMOKE_DIR}"' EXIT
tar -xzf "${ARCHIVE}" -C "${SMOKE_DIR}"
npx --yes "skills@${SKILLS_CLI_VERSION}" add "${SMOKE_DIR}/package" --list | tee "${SMOKE_DIR}/skills-list.txt"

for skill_name in \
  adapting-rvtf-to-agent-skills \
  adapting-rvtf-to-bmad \
  adapting-rvtf-to-gsd \
  adapting-rvtf-to-superpowers \
  tracing-requirements-to-verification; do
  if ! grep -F "${skill_name}" "${SMOKE_DIR}/skills-list.txt" >/dev/null; then
    echo "consumer smoke test did not list ${skill_name}" >&2
    exit 1
  fi
done
