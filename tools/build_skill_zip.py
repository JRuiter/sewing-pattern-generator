#!/usr/bin/env python3
"""Build the installable skill ZIP for claude.ai / the Claude app.

The ZIP contains only what the skill needs at runtime (SKILL.md, scripts/, references/,
assets/, requirements.txt, LICENSE) inside one top-level folder named after the skill.
Tests, examples and test results stay out to keep the upload small.

Usage:
  python tools/build_skill_zip.py                 # -> dist/<skill>-<version>.zip
  python tools/build_skill_zip.py --check-tag v1.2.0
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDE = ["SKILL.md", "scripts", "references", "assets", "requirements.txt", "LICENSE"]
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def project_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise SystemExit("pyproject.toml: no version found")
    return m.group(1)


def skill_name() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
    if not m:
        raise SystemExit("SKILL.md: no 'name:' in the frontmatter")
    return m.group(1)


def iter_files():
    for entry in INCLUDE:
        path = ROOT / entry
        if not path.exists():
            raise SystemExit(f"missing: {entry}")
        if path.is_file():
            yield path
            continue
        for f in sorted(path.rglob("*")):
            if f.is_dir() or f.suffix in EXCLUDE_SUFFIXES:
                continue
            if EXCLUDE_DIRS & set(f.relative_to(ROOT).parts):
                continue
            yield f


def build(out_dir: Path) -> Path:
    name, version = skill_name(), project_version()
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{name}-{version}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in iter_files():
            zf.write(f, f"{name}/{f.relative_to(ROOT).as_posix()}")
    return target


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(ROOT / "dist"), help="output directory (default: dist/)")
    ap.add_argument("--check-tag", help="fail unless this git tag equals v<version from pyproject.toml>")
    args = ap.parse_args(argv)
    if args.check_tag is not None:
        expected = f"v{project_version()}"
        if args.check_tag != expected:
            print(f"tag {args.check_tag!r} does not match pyproject version {expected!r}", file=sys.stderr)
            return 1
    target = build(Path(args.out))
    with zipfile.ZipFile(target) as zf:
        n = len(zf.namelist())
    print(f"{target} ({n} files, {target.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
