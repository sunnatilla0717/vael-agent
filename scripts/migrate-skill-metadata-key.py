#!/usr/bin/env python3
"""Migrate in-repo skill frontmatter from ``metadata.hermes`` to ``metadata.vael`` (IR-2).

The skill schema block is model-facing: the model reads a ``SKILL.md`` verbatim
when it loads a skill, so the key must not say "hermes".  Readers accept both keys
(``agent.skill_utils.skill_metadata_block`` prefers ``vael`` and falls back to
``hermes``), so third-party and older skills keep working unchanged.

Only the ``hermes:`` line *directly nested under a ``metadata:`` key* is rewritten;
every other ``hermes:`` mapping (locales tables, unrelated YAML) is left alone.

Usage:
    python scripts/migrate-skill-metadata-key.py --check
    python scripts/migrate-skill-metadata-key.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOTS = ("skills", "optional-skills")
_KEY_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):\s*$")


def migrated(text: str) -> tuple[str, int]:
    """Rewrite ``metadata:`` -> ``hermes:`` blocks; returns (text, replacements)."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    metadata_indent: int | None = None
    count = 0
    for line in lines:
        match = _KEY_RE.match(line.rstrip("\n"))
        if match:
            indent = len(match.group("indent"))
            key = match.group("key")
            if key == "metadata":
                metadata_indent = indent
            elif metadata_indent is not None and indent > metadata_indent and key == "hermes":
                line = line.replace("hermes:", "vael:", 1)
                count += 1
                metadata_indent = None
            elif metadata_indent is not None and indent <= metadata_indent:
                metadata_indent = None
        out.append(line)
    return "".join(out), count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="rewrite files in place")
    parser.add_argument("--check", action="store_true", help="only report what would change")
    args = parser.parse_args(argv)

    files = 0
    total = 0
    for root in ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("SKILL.md")):
            text = path.read_text(encoding="utf-8")
            new, count = migrated(text)
            if not count:
                continue
            files += 1
            total += count
            if args.apply:
                path.write_text(new, encoding="utf-8", newline="")
    print(f"{'migrated' if args.apply else 'would migrate'} {total} keys in {files} skill files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
