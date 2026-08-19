#!/usr/bin/env python3
"""Measure Zotero full-text coverage — the BR-8 / P4 precondition for screening.

Q1 requires reading introductions and conclusions during screening. The Zotero Web
API returns attachment full text only for files synced to Zotero storage AND indexed.
If coverage is poor, screening cannot be designed as specified, and this tool says so
rather than letting a metadata-only pipeline be built on an unstated assumption.

Verify: python3 execution/measure_zotero_coverage.py --sample 25
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "probes"))
from _common import (GREEN, MISSING, RED, classify_error, emit,  # noqa: E402
                     get_json, load_env, require)

TOOL = "measure_zotero_coverage"
MIN_MEANINGFUL_CHARS = 500  # below this an "indexed" PDF is effectively empty (unOCR'd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=25,
                        help="number of items to inspect (bounded; never the whole library)")
    args = parser.parse_args()

    env = load_env()
    missing = require(env, "ZOTERO_USER_ID", "ZOTERO_API_KEY")
    if missing:
        return emit(TOOL, MISSING, f"Missing required key(s): {', '.join(missing)}.",
                    {"missing_keys": missing})

    uid = env["ZOTERO_USER_ID"]
    headers = {"Zotero-API-Key": env["ZOTERO_API_KEY"], "Zotero-API-Version": "3"}
    base = f"https://api.zotero.org/users/{uid}"

    try:
        _, items, resp_headers = get_json(
            f"{base}/items?limit={args.sample}&itemType=-attachment||note", headers)
        library_total = resp_headers.get("Total-Results")

        with_pdf = indexed = meaningful = 0
        for item in items or []:
            key = item.get("key")
            if not key:
                continue
            _, children, _ = get_json(f"{base}/items/{key}/children", headers)
            pdfs = [c for c in (children or [])
                    if c.get("data", {}).get("contentType") == "application/pdf"]
            if not pdfs:
                continue
            with_pdf += 1
            try:
                _, ft, _ = get_json(f"{base}/items/{pdfs[0]['key']}/fulltext", headers)
            except Exception:
                continue
            content = (ft or {}).get("content", "")
            if content:
                indexed += 1
                if len(content) >= MIN_MEANINGFUL_CHARS:
                    meaningful += 1
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.zotero.org"
        return emit(TOOL, code, detail, evidence)

    sampled = len(items or [])
    evidence = {"library_total": library_total, "sampled": sampled,
                "items_with_pdf": with_pdf, "pdfs_with_indexed_text": indexed,
                "pdfs_with_meaningful_text": meaningful,
                "min_meaningful_chars": MIN_MEANINGFUL_CHARS}

    if sampled == 0:
        return emit(TOOL, RED, "Library returned no items to sample.", evidence)

    ratio = meaningful / sampled
    if ratio < 0.5:
        return emit(TOOL, RED,
                    f"⛔ HALT (BR-8): only {meaningful}/{sampled} sampled items expose "
                    f"meaningful full text. Screening as specified in Q1 requires reading "
                    f"introductions and conclusions. Report what further access is needed; "
                    f"do NOT design screening around metadata-only input.", evidence)

    return emit(TOOL, GREEN,
                f"Full-text coverage adequate: {meaningful}/{sampled} sampled items expose "
                f"meaningful indexed text.", evidence)


if __name__ == "__main__":
    sys.exit(main())
