#!/usr/bin/env python3
"""Shared rename rules for the Hermes -> VAEL identity rename (IR-1..IR-6).

The core principle is deliberately narrow: **only a bare ``hermes`` / ``Hermes``
word is an identity word**. Anything joined to another identifier character is
an upstream artifact that must survive verbatim:

* environment/config layer — ``HERMES_*``, ``~/.hermes``, ``.hermes.md``
* Python + package identifiers — ``hermes_cli``, ``hermes-agent``, ``hermes_yaml``
* filesystem/service/artifact names — ``/opt/hermes/…``, ``hermes.service``,
  ``@hermes/plugin-sdk``, ``hermes.update.run``
* wire protocol — ``X-Hermes-Session-Id``, ``Hermes-Monitor/1.0``, ``data-hermes-send``
* upstream references — the NousResearch repo/domain, the Hermes 4 model names,
  and attribution/credit lines

Rename rules therefore only fire on a standalone word (``run `hermes doctor```
becomes ``run `vael doctor```, ``Hermes delivers`` becomes ``VAEL delivers``), and
attribution phrases/credit lines stay untouched.
"""

from __future__ import annotations

import io
import re
import tokenize
from typing import Callable, Iterator

#: Python 3.12+ tokenizes f-strings into their own token types.
FSTRING_MIDDLE = getattr(tokenize, "FSTRING_MIDDLE", tokenize.STRING)
#: Token types that carry model-facing prose inside a Python source file.
PYTHON_PROSE_TYPES: frozenset[int] = frozenset({tokenize.STRING, tokenize.COMMENT, FSTRING_MIDDLE})

#: A bare identity word: not glued to an identifier/path character on either side.
#: ``.`` is special — it blocks path/suffix/attribute use (``~/.hermes``,
#: ``hermes.json``, ``f"hermes.{key}"``, ``startswith("hermes.")``) but not
#: sentence punctuation (``run hermes.``), hence the two-part lookahead.
BARE_HERMES: re.Pattern[str] = re.compile(
    r"(?<![A-Za-z0-9_/@$:.\-])(?P<word>Hermes|hermes)(?![A-Za-z0-9_/@\-])(?!\.[A-Za-z0-9_{$<\[])"
)

#: A string literal whose whole content is one hermes-ish token (`"hermes."`,
#: `"hermes.exe"`, `"hermes-acp"`) is a runtime value, never prose.
RUNTIME_TOKEN_RE = re.compile(
    r"^[A-Za-z0-9_./\\@${\-]*[Hh]ermes[A-Za-z0-9_./\\@${}\-]*$"
)

#: Attribution phrases that name the upstream project — never rewritten.
ATTRIBUTION_PHRASES: tuple[str, ...] = (
    r"\b(?:based on|derived from|fork of|port of|adapted from|built on|from)\s+(?:the\s+)?Hermes Agent\b",
    r"\bHermes Agent\s+by\s+Nous Research\b",
    r"\bHermes Agent\s*\(Nous Research\)",
    r"\bHermes Agent (?:project|repo|repository|codebase|source|tree|GitHub)\b",
    r"\b(?:upstream|original|official) Hermes\b",
    r"\bHermes Agent\b,?\s*MIT\b",
)

#: Whole-line attribution/credit: skill-frontmatter credits and upstream mentions.
ATTRIBUTION_LINE: re.Pattern[str] = re.compile(
    r"(?i)^\s*author:.*\bhermes\b"
    r"|\bhermes\b[^\n]*\bby Nous Research\b"
    r"|\b(?:upstream|original|official)\b[^\n]*\bhermes\b"
)

#: Upstream model names (Hermes 4 family) must stay verbatim.
MODEL_NAME_PATTERNS: tuple[str, ...] = (
    r"\bHermes[ -]4(?:[ -][A-Za-z0-9.]+)?\b",
    r"\bhermes-4(?:[ -][A-Za-z0-9.]+)?\b",
)

#: Upstream project references (repo, docs domain, package name).
UPSTREAM_URL_PATTERNS: tuple[str, ...] = (
    r"hermes-agent\.nousresearch\.com",
    r"github\.com/NousResearch[/A-Za-z0-9_.-]*",
    r"NousResearch/hermes-agent",
)

#: R-7 compatibility layer: env vars and config paths (aliased, not renamed).
ENV_VAR_PATTERNS: tuple[str, ...] = (
    r"\bHERMES_[A-Z0-9_]+\b",
    r"\$HERMES_HOME\b",
    r"\.hermes\.md\b",
    r"\bHERMES\.md\b",
    r"\.hermes\b",
)

#: Identifier-joined uses — protected by :data:`BARE_HERMES`, categorised for reports.
JOINED_PATTERNS: tuple[str, ...] = (
    r"[A-Za-z0-9_/@$:.\-][Hh]ermes\b",
    r"\b[Hh]ermes[A-Za-z0-9_/@.\-]",
)

#: Public: (category, pattern) pairs, most specific first — shared by audit and guard.
CATEGORISED_PATTERNS: tuple[tuple[str, str], ...] = (
    *((f"attribution[{i}]", p) for i, p in enumerate(ATTRIBUTION_PHRASES)),
    ("upstream-url", UPSTREAM_URL_PATTERNS[0]),
    ("upstream-url", UPSTREAM_URL_PATTERNS[1]),
    ("upstream-url", UPSTREAM_URL_PATTERNS[2]),
    ("upstream-model", MODEL_NAME_PATTERNS[0]),
    ("upstream-model", MODEL_NAME_PATTERNS[1]),
    ("env-var", ENV_VAR_PATTERNS[0]),
    ("env-var", ENV_VAR_PATTERNS[1]),
    ("config-path", ENV_VAR_PATTERNS[2]),
    ("config-path", ENV_VAR_PATTERNS[3]),
    ("config-path", ENV_VAR_PATTERNS[4]),
    ("joined-ident", JOINED_PATTERNS[0]),
    ("joined-ident", JOINED_PATTERNS[1]),
    ("wire-service", r"\bhermes\.[A-Za-z0-9_{$]"),
)

#: An exact-quoted bare token is a runtime value (`sys.argv` sentinel, launcher name).
EXACT_TOKEN = "exact-token"
EXACT_TOKEN_RE = re.compile(r"""([\"'])(?:hermes|Hermes)\1""")

_PHRASE_RE = re.compile("|".join(f"(?:{p})" for p in ATTRIBUTION_PHRASES + MODEL_NAME_PATTERNS))
_PHRASE_CATEGORIES = tuple(
    (category, re.compile(pattern)) for category, pattern in CATEGORISED_PATTERNS
)
_PLACEHOLDER = "\x00{}\x00"
_WORD_MAP = {"hermes": "vael", "Hermes": "VAEL"}

#: Possessive without the second ``s`` (``Hermes' own frames`` -> ``VAEL's own frames``).
POSSESSIVE_RE = re.compile(r"(?<![A-Za-z0-9_/@$:.\-])Hermes'(?![sS])")


def shield(text: str) -> tuple[str, list[str]]:
    """Protect attribution phrases and upstream model names; return (text, kept)."""
    kept: list[str] = []

    def _sub(match: re.Match[str]) -> str:
        kept.append(match.group(0))
        return _PLACEHOLDER.format(len(kept) - 1)

    return _PHRASE_RE.sub(_sub, text), kept


def restore(text: str, kept: list[str]) -> str:
    for index, original in enumerate(kept):
        text = text.replace(_PLACEHOLDER.format(index), original)
    return text


def _line_at(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    return text[line_start: line_end if line_end != -1 else len(text)]


def rename(text: str) -> str:
    """Rename bare model-facing identity words in *text*, keeping every shield."""
    shielded, kept = shield(text)
    shielded = POSSESSIVE_RE.sub("VAEL's", shielded)

    def _sub(match: re.Match[str]) -> str:
        if ATTRIBUTION_LINE.search(_line_at(shielded, match.start(), match.end())):
            return match.group(0)
        return _WORD_MAP[match.group("word")]

    return restore(BARE_HERMES.sub(_sub, shielded), kept)


def has_bare_hermes(text: str) -> bool:
    """True when *text* contains a bare identity word that :func:`rename` would change."""
    return rename(text) != text


def is_runtime_token(content: str) -> bool:
    """True when a string literal's whole content is a single hermes-ish token."""
    return bool(RUNTIME_TOKEN_RE.match(content))


def classify_python(source: str) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` for every *violation* inside a Python source file."""
    for lineno, text in iter_python_prose(source):
        if classify(text) == "VIOLATION":
            yield lineno, text


def classify(text: str) -> str | None:
    """Category of the first hermes match in *text*, else ``VIOLATION`` / ``None``.

    ``None`` for text with no match, a keep-category name for a documented
    exception (``env-var``, ``joined-ident``, ``attribution[0]`` …),
    ``exact-token`` for a protected quoted runtime value, and ``VIOLATION`` for a
    bare identity word that still needs renaming.
    """
    if "hermes" not in text.lower():
        return None
    if ATTRIBUTION_LINE.search(text):
        return "attribution"
    for category, pattern in _PHRASE_CATEGORIES:
        if pattern.search(text):
            # The attribution buckets are all `attribution[i]`; report the family.
            return "attribution" if category.startswith("attribution") else category
    if EXACT_TOKEN_RE.search(text):
        return EXACT_TOKEN
    return "VIOLATION" if rename(text) != text else None


#: Exact-token Python string, e.g. ``"hermes"`` as a launcher name.
_EXACT_TOKEN_RE = re.compile(r'''^\s*(?:[rubfRUBF]{0,2})?(["'])(?:hermes|Hermes)\1\s*;?\s*$''')
#: f-string chunk that is an attribute prefix (``f"hermes.{key}"``): a namespace.
_FSTRING_ATTR_PREFIX_RE = re.compile(r'''^[A-Za-z0-9_]*[Hh]ermes\.$''')
#: Python string prefix + quotes, for unwrapping a literal's content.
_STRING_WRAPPER_RE = re.compile(r"""^[A-Za-z]{0,3}(?P<q>\"\"\"|'''|\"|')""")


def _literal_content(token_text: str) -> str | None:
    """Content of a Python string literal, or None when it cannot be unwrapped."""
    match = _STRING_WRAPPER_RE.match(token_text)
    if not match:
        return None
    quote = match.group("q")
    if not token_text.endswith(quote) or len(token_text) < 2 * len(quote):
        return None
    return token_text[match.end(): -len(quote)]


def iter_python_prose(source: str) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` for every renaming-eligible Python token.

    Keywords, identifiers, numbers and runtime values are skipped, so callers see
    exactly the strings/comments that :func:`rename_python` would rewrite.
    """
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        for lineno, line in enumerate(source.splitlines(), 1):
            yield lineno, line
        return
    for tok in tokens:
        if tok.type not in PYTHON_PROSE_TYPES:
            continue
        if _EXACT_TOKEN_RE.match(tok.string):
            continue
        literal = _literal_content(tok.string)
        if literal is not None and is_runtime_token(literal):
            continue
        if tok.type == FSTRING_MIDDLE and _FSTRING_ATTR_PREFIX_RE.match(tok.string):
            continue
        yield tok.start[0], tok.string


def rename_python(source: str) -> str:
    """Rewrite the prose in a Python source file; identifiers stay untouched."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return rename(source)

    line_starts = [0]
    for line in source.splitlines(keepends=True):
        line_starts.append(line_starts[-1] + len(line))

    def offset(row: int, col: int) -> int:
        return line_starts[row - 1] + col

    edits: list[tuple[int, int, str]] = []
    for tok in tokens:
        if tok.type not in PYTHON_PROSE_TYPES:
            continue
        if _EXACT_TOKEN_RE.match(tok.string):
            continue
        literal = _literal_content(tok.string)
        if literal is not None and is_runtime_token(literal):
            continue
        if tok.type == FSTRING_MIDDLE and _FSTRING_ATTR_PREFIX_RE.match(tok.string):
            continue
        new = rename(tok.string)
        if new != tok.string:
            edits.append((offset(*tok.start), offset(*tok.end), new))

    for start, end, new in sorted(edits, reverse=True):
        source = source[:start] + new + source[end:]
    return source


def rename_lines(text: str, line_transform: Callable[[str], str] | None = None) -> str:
    """Apply :func:`rename` line by line (keeps attribution-line shields local)."""
    out = []
    for line in text.splitlines(keepends=True):
        if ATTRIBUTION_LINE.search(line):
            out.append(line)
            continue
        new = rename(line)
        out.append(line_transform(new) if line_transform else new)
    return "".join(out)
