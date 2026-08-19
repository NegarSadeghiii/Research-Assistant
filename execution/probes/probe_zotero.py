#!/usr/bin/env python3
"""Probe: Zotero Web API. See /architecture/SOP-001-connection-probes.md.

Smallest authenticated read: one item. Never writes — Zotero is read-only in
Stage 1 v1 (BR-12).

Verify: python3 execution/probes/probe_zotero.py
"""
from __future__ import annotations

import sys

from _common import (BLOCKED, GREEN, MISSING, RED, classify_error, emit,
                     get_json, load_env, require)

TOOL = "probe_zotero"


def main() -> int:
    env = load_env()
    missing = require(env, "ZOTERO_USER_ID", "ZOTERO_API_KEY")
    if missing:
        return emit(TOOL, MISSING, f"Missing required key(s): {', '.join(missing)}.",
                    {"missing_keys": missing})

    user_id = env["ZOTERO_USER_ID"]
    url = f"https://api.zotero.org/users/{user_id}/items?limit=1"
    headers = {"Zotero-API-Key": env["ZOTERO_API_KEY"],
               "Zotero-API-Version": "3"}
    try:
        status, body, resp_headers = get_json(url, headers)
    except BaseException as exc:  # noqa: BLE001 - classification is the point
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.zotero.org"
        return emit(TOOL, code, detail, evidence)

    total = resp_headers.get("Total-Results")
    return emit(TOOL, GREEN,
                f"Zotero key accepted for userID {user_id}; library reports {total} items.",
                {"http_status": status, "total_results": total,
                 "sample_returned": len(body) if isinstance(body, list) else None})


if __name__ == "__main__":
    sys.exit(main())
