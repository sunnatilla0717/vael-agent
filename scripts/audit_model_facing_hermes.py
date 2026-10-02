#!/usr/bin/env python3
"""Audit model-facing content for leftover upstream "hermes" identity strings.

VAEL identity is a single source of truth: the model must never read "hermes" as
its own name.  Lots of *internal* identifiers legitimately keep the upstream
spelling (`hermes_*.py` modules, `HERMES_*` env vars, `~/.hermes` paths, wire
headers, upstream URLs) — those are covered by R-7 aliases or protected by the
upstream-merge constraint, and are allowed here by explicit pattern.

Everything else on a model-facing surface is a violation, so this script doubles
as the IR-1 audit and the IR-6 CI guard.

Usage:
    python scripts/audit_model_facing_hermes.py            # summary report
    python scripts/audit_model_facing_hermes.py --list     # every violation
    python scripts/audit_model_facing_hermes.py --fail     # exit 1 on violations
    python scripts/audit_model_facing_hermes.py --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vael_identity_rules import classify, iter_python_prose  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# Surfaces whose text the model reads (prompts, skills, tool descriptions) or
# that ship to the model as part of a tool result / CLI transcript.
MODEL_FACING_GLOBS: tuple[str, ...] = (
    "skills/**/*",
    "optional-skills/**/*",
    "agent/**/*.py",
    "tools/**/*.py",
    "hermes_cli/**/*.py",
    "hermes_cli/**/*.json",
    "plugins/**/*.py",
    "plugins/**/*.yaml",
    "locales/en.yaml",
    "web/src/i18n/en.ts",
)

# tools/computer_use/ is a separate security-sensitive PR (IR-8); the shared
# metrics schema is a frozen wire contract regenerated from its own source.
EXCLUDED_PREFIXES: tuple[str, ...] = (
    "tools/computer_use/",
    "hermes_cli/observability/schemas/",
)

TEXT_SUFFIXES: frozenset[str] = frozenset(
    {".py", ".md", ".yaml", ".yml", ".json", ".ts", ".tsx", ".js", ".mjs", ".sh", ".ps1", ".txt", ".toml"}
)

def iter_files(excluded: list[str] | None = None) -> Iterable[Path]:
    seen: set[Path] = set()
    for pattern in MODEL_FACING_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(EXCLUDED_PREFIXES):
                if excluded is not None:
                    excluded.append(rel)
                continue
            if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            seen.add(path)
            yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="print every violation with line numbers")
    parser.add_argument("--fail", action="store_true", help="exit 1 when violations are found")
    parser.add_argument("--json", metavar="PATH", help="write the full report as JSON")
    parser.add_argument("--max-per-file", type=int, default=12, help="violations printed per file in --list")
    args = parser.parse_args(argv)

    categories: dict[str, int] = {}
    violations: dict[str, list[tuple[int, str]]] = {}
    scanned = 0
    excluded: list[str] = []

    for path in iter_files(excluded):
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        rel = path.relative_to(REPO_ROOT).as_posix()
        # Python files are inspected token-by-token so identifiers, environment
        # variables and runtime string values are never mistaken for prose.
        scanned_lines = (
            iter_python_prose(text)
            if path.suffix.lower() == ".py"
            else enumerate(text.splitlines(), 1)
        )
        for lineno, line in scanned_lines:
            kind = classify(line)
            if kind is None:
                continue
            categories[kind] = categories.get(kind, 0) + 1
            if kind == "VIOLATION":
                violations.setdefault(rel, []).append((lineno, line.strip()))

    total_violations = sum(len(v) for v in violations.values())
    print(f"scanned {scanned} model-facing files")
    if excluded:
        print(f"excluded {len(excluded)} files (separate PR / frozen wire contract)")
    print("keep-category counts (allowed, documented in REBRANDING.md IR-8):")
    for kind, count in sorted(categories.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {kind:18} {count}")
    print(f"violations: {total_violations} in {len(violations)} files")

    if args.list and violations:
        for rel in sorted(violations):
            print(f"\n{rel}")
            for lineno, line in violations[rel][: args.max_per_file]:
                print(f"  {lineno}: {line}")
            extra = len(violations[rel]) - args.max_per_file
            if extra > 0:
                print(f"  ... {extra} more")

    if not args.list and violations:
        print("\ntop files by violation count:")
        for rel, hits in sorted(violations.items(), key=lambda kv: -len(kv[1]))[:25]:
            print(f"  {len(hits):4}  {rel}")

    if args.json:
        payload = {
            "scanned_files": scanned,
            "keep_categories": categories,
            "violations": {rel: [{"line": n, "text": t} for n, t in hits] for rel, hits in violations.items()},
        }
        Path(args.json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {args.json}")

    if args.fail and total_violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
