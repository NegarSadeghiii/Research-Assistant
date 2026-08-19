#!/usr/bin/env python3
"""Probe: OpenAlex. API keys mandatory since 2026-02-13; mailto no longer accepted.

Verify: python3 execution/probes/probe_openalex.py
"""
from __future__ import annotations

import sys

from _common import (GREEN, MISSING, classify_error, emit, get_json, load_env,
                     require)

TOOL = "probe_openalex"


def main() -> int:
    env = load_env()
    missing = require(env, "OPENALEX_API_KEY")
    if missing:
        return emit(TOOL, MISSING,
                    "Missing OPENALEX_API_KEY (mandatory since 2026-02-13).",
                    {"missing_keys": missing})

    url = f"https://api.openalex.org/works?per-page=1&api_key={env['OPENALEX_API_KEY']}"
    try:
        status, body, _ = get_json(url)
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.openalex.org"
        # Distinguish an exhausted allowance from an invalid key (SOP-001 section 4).
        head = str(evidence.get("body_head", "")).lower()
        if "quota" in head or "allowance" in head or "limit" in head:
            detail = "OpenAlex daily allowance appears exhausted — the key itself may be valid."
        return emit(TOOL, code, detail, evidence)

    count = (body or {}).get("meta", {}).get("count")
    return emit(TOOL, GREEN, f"OpenAlex key accepted; corpus reports {count} works.",
                {"http_status": status, "meta_count": count})


if __name__ == "__main__":
    sys.exit(main())
