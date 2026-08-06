#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${ROOT}/skills"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "skills directory not found: ${SKILLS_DIR}" >&2
  exit 1
fi

"${PYTHON_BIN}" "${ROOT}/scripts/validate_skills.py" "${SKILLS_DIR}"

if [[ ! -f "${ROOT}/scripts/validate-schema-examples.py" ]]; then
  echo "schema example validator not found: ${ROOT}/scripts/validate-schema-examples.py" >&2
  exit 1
fi

"${PYTHON_BIN}" "${ROOT}/scripts/validate-schema-examples.py"
