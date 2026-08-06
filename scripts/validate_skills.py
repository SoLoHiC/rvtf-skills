#!/usr/bin/env python3
"""Validate the Skill metadata contract shipped by this repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, Tuple

import yaml


ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---(?:\n|$)", re.DOTALL)


def validate_skill(skill_path: Path) -> Tuple[bool, str]:
    """Return whether one Skill directory satisfies the packaged metadata contract."""

    skill_path = Path(skill_path)
    skill_file = skill_path / "SKILL.md"
    if not skill_file.is_file():
        return False, "SKILL.md not found"

    content = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if match is None:
        return False, "No valid YAML frontmatter found"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return False, f"Invalid YAML in frontmatter: {error}"

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected = set(frontmatter) - ALLOWED_PROPERTIES
    if unexpected:
        return False, f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}"

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter["name"]
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return False, "Name must not be empty"
    if not re.fullmatch(r"[a-z0-9-]+", name):
        return False, f"Name '{name}' should be hyphen-case"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return False, f"Name is too long ({len(name)} characters)"

    description = frontmatter["description"]
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return False, "Description must not be empty"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description is too long ({len(description)} characters)"

    return True, "Skill is valid"


def validate_skills(skills_dir: Path) -> Tuple[int, list[str]]:
    """Validate all direct Skill directories and return count plus diagnostics."""

    skills_dir = Path(skills_dir)
    if not skills_dir.is_dir():
        return 0, [f"skills directory not found: {skills_dir}"]

    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    if not skill_dirs:
        return 0, [f"no skills found under {skills_dir}"]

    failures: list[str] = []
    for skill_dir in skill_dirs:
        valid, message = validate_skill(skill_dir)
        if valid:
            print(f"PASS {skill_dir.name}: {message}")
        else:
            failures.append(f"{skill_dir.name}: {message}")
            print(f"FAIL {skill_dir.name}: {message}")
    return len(skill_dirs), failures


def main(argv: Iterable[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    skills_dir = Path(args[0]) if args else Path(__file__).resolve().parents[1] / "skills"
    count, failures = validate_skills(skills_dir)
    if failures:
        print(f"skill metadata: {count - len(failures)} valid, {len(failures)} failed")
        return 1
    print(f"skill metadata: {count} valid, 0 failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
