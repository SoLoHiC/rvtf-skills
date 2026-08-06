#!/usr/bin/env python3
"""Repository-local checks used by the RVTF release workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Iterable


VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CHANGELOG_RE = re.compile(r"^## \[([^\]]+)\](?:\s+-\s+.*)?$", re.MULTILINE)
REQUIRED_PACKAGE_FILES = {
    "package/CHANGELOG.md",
    "package/LICENSE",
    "package/THIRD_PARTY_NOTICES.md",
    "package/VERSION",
    "package/package.json",
}
FORBIDDEN_PACKAGE_PREFIXES = ("package/scripts/tests/",)


class ReleaseError(ValueError):
    """Raised when a release preflight or archive check is invalid."""


def validate_version(version: str) -> None:
    if VERSION_RE.fullmatch(version) is None:
        raise ReleaseError(f"{version!r} is not a strict X.Y.Z version")


def read_package(root: Path) -> dict:
    try:
        return json.loads((root / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseError(f"cannot read package.json: {error}") from error


def check_version(root: Path, version: str) -> None:
    validate_version(version)
    root = Path(root)
    version_file = (root / "VERSION").read_text(encoding="utf-8").strip()
    package_version = read_package(root).get("version")
    if version_file != version or package_version != version:
        raise ReleaseError(
            f"project version does not match {version}: VERSION={version_file!r}, "
            f"package.json.version={package_version!r}"
        )


def set_version(root: Path, version: str) -> None:
    validate_version(version)
    root = Path(root)
    package_path = root / "package.json"
    package = read_package(root)
    package["version"] = version
    package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")


def extract_changelog(root: Path, version: str) -> str:
    validate_version(version)
    content = (Path(root) / "CHANGELOG.md").read_text(encoding="utf-8")
    matches = list(CHANGELOG_RE.finditer(content))
    for index, match in enumerate(matches):
        if match.group(1) != version:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        section = content[match.start() : end].strip()
        if section == match.group(0).strip():
            raise ReleaseError(f"CHANGELOG section for {version} is empty")
        return section
    raise ReleaseError(f"No CHANGELOG section for {version}")


def _safe_archive_name(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ReleaseError(f"unsafe archive path: {name}")


def _read_regular_member(handle: tarfile.TarFile, members: dict[str, tarfile.TarInfo], name: str) -> bytes:
    member = members.get(name)
    if member is None or not member.isfile():
        raise ReleaseError(f"archive member is not a regular file: {name}")
    extracted = handle.extractfile(member)
    if extracted is None:
        raise ReleaseError(f"archive member cannot be read: {name}")
    return extracted.read()


def audit_package(archive: Path, version: str) -> None:
    validate_version(version)
    archive = Path(archive)
    try:
        with tarfile.open(archive, "r:gz") as handle:
            members = handle.getmembers()
            names = {member.name for member in members}
            members_by_name = {member.name: member for member in members}
            for name in names:
                _safe_archive_name(name)
                if name.startswith(FORBIDDEN_PACKAGE_PREFIXES):
                    raise ReleaseError(f"archive contains forbidden test path: {name}")
            missing = REQUIRED_PACKAGE_FILES - names
            if missing:
                raise ReleaseError(f"archive is missing required files: {', '.join(sorted(missing))}")
            version_text = _read_regular_member(handle, members_by_name, "package/VERSION").decode().strip()
            package = json.loads(_read_regular_member(handle, members_by_name, "package/package.json").decode())
            if version_text != version or package.get("version") != version:
                raise ReleaseError("archive version identity does not match requested version")
            if package.get("name") != "rvtf-skills" or package.get("license") != "MIT":
                raise ReleaseError("archive package identity or license is invalid")
            skill_paths = {
                PurePosixPath(name).parts[2]
                for name in names
                if len(PurePosixPath(name).parts) == 4
                and name.startswith("package/skills/")
                and name.endswith("/SKILL.md")
            }
            if len(skill_paths) != 5:
                raise ReleaseError(f"archive must contain five Skills, found {len(skill_paths)}")
    except tarfile.TarError as error:
        raise ReleaseError(f"cannot read package archive: {error}") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)
    version = subparsers.add_parser("version")
    version_action = version.add_mutually_exclusive_group(required=True)
    version_action.add_argument("--check", dest="check_version", metavar="VERSION")
    version_action.add_argument("--set", dest="set_version", metavar="VERSION")
    notes = subparsers.add_parser("notes")
    notes.add_argument("version")
    audit = subparsers.add_parser("audit-package")
    audit.add_argument("archive", type=Path)
    audit.add_argument("version")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "version":
            if args.check_version is not None:
                check_version(args.root, args.check_version)
            else:
                set_version(args.root, args.set_version)
        elif args.command == "notes":
            print(extract_changelog(args.root, args.version))
        elif args.command == "audit-package":
            audit_package(args.archive, args.version)
        else:
            raise ReleaseError(f"unsupported command: {args.command}")
    except (OSError, ReleaseError, json.JSONDecodeError) as error:
        print(f"release check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
