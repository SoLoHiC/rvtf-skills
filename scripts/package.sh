#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT}/VERSION")"
DIST_DIR="${ROOT}/dist"

"${ROOT}/scripts/validate.sh"

mkdir -p "${DIST_DIR}"
rm -f "${DIST_DIR}/rvtf-skills-${VERSION}.tgz"
rm -f "${DIST_DIR}/rvtf-skills-${VERSION}.tar.gz"

(cd "${ROOT}" && npm pack --pack-destination "${DIST_DIR}")
