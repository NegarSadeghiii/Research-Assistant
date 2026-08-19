#!/usr/bin/env python3
"""Regression suite for .env parsing (SOP-000 section 4).

A quoted value used to pass through with its quotes attached, producing a wrong
credential that services reject as a bad key. The symptom pointed at the key; the
cause was the file. That failure is pinned here so it cannot return.

Verify: python3 execution/tests/test_env_loading.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
from _common import load_env, require  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'✅' if condition else '❌'} {name}{'' if condition else '  ' + detail}")
    if not condition:
        FAILURES.append(name)


def parse(text: str) -> dict[str, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as fh:
        fh.write(text)
        path = Path(fh.name)
    try:
        return load_env(path)
    finally:
        path.unlink()


print("\n  .env parsing\n")

KEY = "PlMhixmMHVstMMJNLPiGKUYL"

env = parse(f"ZOTERO_API_KEY={KEY}\n")
check("bare value parses", env.get("ZOTERO_API_KEY") == KEY, repr(env.get("ZOTERO_API_KEY")))

env = parse(f'ZOTERO_API_KEY="{KEY}"\n')
check("double-quoted value is unwrapped", env.get("ZOTERO_API_KEY") == KEY,
      repr(env.get("ZOTERO_API_KEY")))

env = parse(f"ZOTERO_API_KEY='{KEY}'\n")
check("single-quoted value is unwrapped", env.get("ZOTERO_API_KEY") == KEY,
      repr(env.get("ZOTERO_API_KEY")))

env = parse(f"ZOTERO_API_KEY=  {KEY}  \n")
check("surrounding whitespace is trimmed", env.get("ZOTERO_API_KEY") == KEY,
      repr(env.get("ZOTERO_API_KEY")))

env = parse(f"ZOTERO_API_KEY={KEY}\r\n")
check("CRLF line ending does not corrupt the value", env.get("ZOTERO_API_KEY") == KEY,
      repr(env.get("ZOTERO_API_KEY")))

# A lone quote is part of the value, not a wrapper - do not strip asymmetrically.
env = parse('WEIRD="unbalanced\n')
check("an unbalanced quote is left alone", env.get("WEIRD") == '"unbalanced',
      repr(env.get("WEIRD")))

env = parse("# a comment\n\nA=1\nB=2\n")
check("comments and blank lines are skipped", env == {"A": "1", "B": "2"}, repr(env))

env = parse("NOEQUALS\nA=1\n")
check("a line with no '=' is skipped", env == {"A": "1"}, repr(env))

env = parse("DB_URL=postgres://u:p@host:5432/db?x=1\n")
check("a value containing '=' keeps everything after the first one",
      env.get("DB_URL") == "postgres://u:p@host:5432/db?x=1", repr(env.get("DB_URL")))

env = parse("EMPTY=\n")
check("an empty value is falsy so require() catches it", not env.get("EMPTY"))
check("require() names an empty key as missing", require(env, "EMPTY") == ["EMPTY"])

missing = parse("A=1\n")
check("load_env on a nonexistent path returns {} rather than raising",
      load_env(Path("/nonexistent/.env")) == {})

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All .env parsing tests passed.\n")
