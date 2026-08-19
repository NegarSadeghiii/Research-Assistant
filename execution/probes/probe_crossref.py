#!/usr/bin/env python3
"""Probe: Crossref REST. No key; a contact address joins the polite pool.

Crossref is the DOI validation layer — the mechanical guard for F3 — so this
probe resolves a known DOI rather than only running a search.

Verify: python3 execution/probes/probe_crossref.py
"""
from __future__ import annotations

import sys

from _common import GREEN, RED, classify_error, emit, get_json, load_env

TOOL = "probe_crossref"
# Any stably resolvable DOI serves this probe. The title is whatever Crossref
# asserts - this file makes no claim about which paper it is. An earlier comment here
# named the wrong paper; the live probe surfaced the mismatch (2026-08-19).
KNOWN_DOI = "10.1038/s41587-023-01911-8"


def main() -> int:
    env = load_env()
    headers = {}
    mailto = env.get("CROSSREF_MAILTO")
    if mailto:
        headers["User-Agent"] = f"research-assistant/0.1 (mailto:{mailto})"

    try:
        status, body, _ = get_json(f"https://api.crossref.org/works/{KNOWN_DOI}", headers)
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.crossref.org"
        return emit(TOOL, code, detail, evidence)

    title = (body or {}).get("message", {}).get("title", [None])[0]
    if not title:
        return emit(TOOL, RED, "Crossref responded but the DOI record had no title — unexpected shape.",
                    {"http_status": status})
    return emit(TOOL, GREEN, f"Crossref resolved a known DOI to: {title!r}",
                {"http_status": status, "doi": KNOWN_DOI, "resolved_title": title,
                 "polite_pool": bool(mailto)})


if __name__ == "__main__":
    sys.exit(main())
