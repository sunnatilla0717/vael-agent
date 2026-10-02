#!/usr/bin/env python3
"""Apply the Hermes -> VAEL identity rename to model-facing content (IR-2/IR-3).

The rewrite strategy per file family lives in :mod:`vael_identity_rules`:

* ``.py`` — only ``STRING``/``COMMENT``/f-string tokens are rewritten, so
  identifiers, imports and ``sys.argv`` sentinels are never touched, and runtime
  values (``"hermes"``, ``"hermes."``, ``f"hermes.{key}"``) stay verbatim.
* machine-readable files (``.yaml``/``.json``/``.ts``/``.js``) — prose is rewritten,
  but a quoted literal holding a single hermes-ish token is a value, not prose.
* ``.md``/``.sh`` — everything is prose or an example the model reads; a bare
  ``hermes:`` mapping key (locales tables, skill frontmatter) is skipped.

Usage:
    python scripts/apply-identity-rename.py --check          # list files that would change
    python scripts/apply-identity-rename.py --diff --only agent/prompt_builder.py
    python scripts/apply-identity-rename.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vael_identity_rules import rename, rename_python  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_GLOBS: tuple[str, ...] = (
    "skills/**/*",
    "optional-skills/**/*",
    "agent/**/*.py",
    "tools/**/*.py",
    "hermes_cli/**/*.py",
    "plugins/**/*.py",
    "plugins/**/*.yaml",
    "plugins/**/*.yml",
    "locales/en.yaml",
    "web/src/i18n/en.ts",
)

EXCLUDED_PREFIXES: tuple[str, ...] = (
    # Separate security-sensitive PR (IR-8).
    "tools/computer_use/",
    # Frozen wire contract regenerated from its own source.
    "hermes_cli/observability/schemas/",
)

TEXT_SUFFIXES: frozenset[str] = frozenset(
    {".py", ".md", ".yaml", ".yml", ".json", ".ts", ".tsx", ".js", ".mjs", ".sh", ".ps1", ".txt"}
)

#: A bare ``hermes:`` mapping key is schema, not prose (locales tables, skill
#: frontmatter ``metadata.hermes`` — migrated separately with dual-read support).
_MAPPING_KEY_RE = re.compile(r"^\s*hermes:\s*$")
#: Machine-readable files: a quoted literal holding one hermes-ish token is a value.
_QUOTED_TOKEN_RE = re.compile(r"""(["'])([^\s"']*[Hh]ermes[^\s"']*)\1""")


def rename_code_text(text: str) -> str:
    """Rename prose inside a code file, leaving machine-readable values alone."""
    kept: list[str] = []

    def _sub(match: re.Match[str]) -> str:
        kept.append(match.group(0))
        return f"\x01{len(kept) - 1}\x01"

    renamed = rename(_QUOTED_TOKEN_RE.sub(_sub, text))
    for index, original in enumerate(kept):
        renamed = renamed.replace(f"\x01{index}\x01", original)
    return renamed


def iter_targets(only: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in TARGET_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(EXCLUDED_PREFIXES):
                continue
            if only and not rel.startswith(tuple(only)):
                continue
            if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            seen.add(path)
            files.append(path)
    return files


def transform(path: Path, text: str) -> str:
    """Renamed text for one file, per its family's strategy."""
    suffix = path.suffix.lower()
    if suffix == ".py":
        return rename_python(text)
    if suffix in {".yaml", ".yml", ".json", ".ts", ".tsx", ".js", ".mjs"}:
        return rename_code_text(text)
    return "".join(
        line if _MAPPING_KEY_RE.match(line.rstrip("\n")) else rename(line)
        for line in text.splitlines(keepends=True)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="rewrite files in place")
    parser.add_argument("--check", action="store_true", help="only list files that would change")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="PREFIX",
        help="restrict to a repo-relative path prefix (repeatable)",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--diff", action="store_true", help="print a unified diff of the changes")
    parser.add_argument("--limit", type=int, default=40, help="max files shown with --diff")
    args = parser.parse_args(argv)

    changed: list[tuple[str, int]] = []
    for path in iter_targets(tuple(args.only)):
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        new = transform(path, text)
        if new == text:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        before_lines = text.splitlines()
        after_lines = new.splitlines()
        changed.append((rel, sum(1 for a, b in zip(before_lines, after_lines) if a != b)))
        if args.diff and len(changed) <= args.limit:
            import difflib

            print(f"\n--- {rel}")
            for line in difflib.unified_diff(before_lines, after_lines, lineterm="", n=0):
                if line.startswith(("---", "+++", "@@")):
                    continue
                print(line)
        if args.apply:
            path.write_text(new, encoding="utf-8", newline="")

    total_lines = sum(count for _, count in changed)
    if not args.quiet:
        for rel, count in changed:
            print(f"{count:5}  {rel}")
    print(f"{'rewrote' if args.apply else 'would rewrite'} {len(changed)} files ({total_lines} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
