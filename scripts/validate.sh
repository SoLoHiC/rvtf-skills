#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${ROOT}/skills"
PYTHON_BIN="${PYTHON_BIN:-python3}"
QUICK_VALIDATE="${QUICK_VALIDATE:-${HOME}/.codex/skills/.system/skill-creator/scripts/quick_validate.py}"

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "skills directory not found: ${SKILLS_DIR}" >&2
  exit 1
fi

if [[ ! -f "${QUICK_VALIDATE}" ]]; then
  echo "quick_validate.py not found: ${QUICK_VALIDATE}" >&2
  echo "Set QUICK_VALIDATE=/path/to/quick_validate.py" >&2
  exit 1
fi

found=0
for skill_dir in "${SKILLS_DIR}"/*; do
  [[ -d "${skill_dir}" ]] || continue
  found=1
  "${PYTHON_BIN}" "${QUICK_VALIDATE}" "${skill_dir}"
done

if [[ "${found}" -eq 0 ]]; then
  echo "no skills found under ${SKILLS_DIR}" >&2
  exit 1
fi

