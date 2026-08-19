#!/usr/bin/env python3
"""Probe: Semantic Scholar Academic Graph. Key optional; raises rate limits.

Verify: python3 execution/probes/probe_semantic_scholar.py
"""
from __future__ import annotations

import sys

from _common import GREEN, classify_error, emit, get_json, load_env

TOOL = "probe_semantic_scholar"


def main() -> int:
    env = load_env()
    url = ("https://api.semanticscholar.org/graph/v1/paper/search"
           "?query=CAR-T+supply+chain&limit=1&fields=title,year")
    headers = {}
    if env.get("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = env["SEMANTIC_SCHOLAR_API_KEY"]

    try:
        status, body, _ = get_json(url, headers)
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.semanticscholar.org"
        evidence["authenticated"] = bool(headers)
        return emit(TOOL, code, detail, evidence)

    total = (body or {}).get("total")
    return emit(TOOL, GREEN,
                f"Semantic Scholar reachable{' (authenticated)' if headers else ' (unauthenticated)'}; "
                f"query matched {total} papers.",
                {"http_status": status, "total": total, "authenticated": bool(headers)})


if __name__ == "__main__":
    sys.exit(main())
