#!/usr/bin/env python3
"""Verify the Hermes -> VAEL identity rename did not damage protected tokens.

Compares every changed model-facing file against its ``HEAD`` revision:

* every protected token from HEAD (``hermes_*`` identifiers, ``HERMES_*`` env vars,
  ``~/.hermes`` paths, kebab/dotted artifacts, upstream URLs, model names) must
  still be present — the R-7 layer and the upstream-merge surface are untouched;
* no *new* joined ``vael`` token may appear (``.vael``, ``@vael/…``,
  ``vael.service``) — the rename only mints the bare word ``vael`` / ``VAEL``.

Usage:
    python scripts/verify-identity-rename.py [--limit N]
"""

from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

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
    "tools/computer_use/",
    "hermes_cli/observability/schemas/",
)

#: Tokens that carry upstream/R-7 compatibility meaning and must survive verbatim.
PROTECTED_RE = re.compile(
    r"\bHERMES_[A-Z0-9_]+"
    r"|\bhermes_[a-z0-9_]+"
    r"|[A-Za-z0-9_./@$:-]*hermes[-_.@/][A-Za-z0-9_./@$-]*"
    r"|\bHermes[ -]4[A-Za-z0-9.-]*"
)

#: Joined `vael` tokens are artifacts: the rename only produces the bare word.
JOINED_VAEL_RE = re.compile(r"[A-Za-z0-9_/@$:-]*[Vv]ael[-_.@/][A-Za-z0-9_./@$-]*")


def head_text(rel: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout if proc.returncode == 0 else None


def changed_files() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", *TARGET_GLOBS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    out = []
    for rel in proc.stdout.splitlines():
        rel = rel.strip()
        if not rel or rel.startswith(EXCLUDED_PREFIXES):
            continue
        if (REPO_ROOT / rel).is_file():
            out.append(rel)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=25, help="examples printed per finding")
    args = parser.parse_args(argv)

    lost: collections.Counter[str] = collections.Counter()
    lost_examples: list[str] = []
    minted: list[str] = []
    checked = 0

    for rel in changed_files():
        old = head_text(rel)
        if old is None:
            continue
        new = (REPO_ROOT / rel).read_text(encoding="utf-8-sig")
        checked += 1
        count_new = collections.Counter(PROTECTED_RE.findall(new))
        for token, count in collections.Counter(PROTECTED_RE.findall(old)).items():
            if count_new[token] < count:
                lost[token] += count - count_new[token]
                if len(lost_examples) < args.limit:
                    lost_examples.append(f"{rel}: {token!r} ({count} -> {count_new[token]})")
        for token in set(JOINED_VAEL_RE.findall(new)):
            if token not in old:
                minted.append(f"{rel}: {token!r}")

    print(f"checked {checked} changed model-facing files")
    if lost:
        print(f"\nFAIL: {sum(lost.values())} protected token occurrences lost")
        for example in lost_examples:
            print(f"  {example}")
    else:
        print("OK: every protected token from HEAD is still present")
    if minted:
        print(f"\nFAIL: {len(minted)} minted joined-'vael' artifacts")
        for example in minted[: args.limit]:
            print(f"  {example}")
    else:
        print("OK: no new joined-vael artifacts")
    return 1 if (lost or minted) else 0


if __name__ == "__main__":
    sys.exit(main())
