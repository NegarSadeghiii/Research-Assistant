#!/usr/bin/env python3
"""Fetch the Zotero library into a local corpus cache. See SOP-003 section 4.1.

Deterministic and resumable: a re-run reuses whatever is already cached and only
fetches what is missing. Records per item whether indexed full text was available,
because that drives the evidence threshold screening is allowed to reach (SOP-003 4.4).

Verify:
    python3 execution/fetch_zotero_corpus.py --limit 5 --out .tmp/corpus-sample.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "execution" / "probes"))
from _common import (GREEN, MISSING, RED, classify_error, emit,  # noqa: E402
                     get_json, load_env, require)

TOOL = "fetch_zotero_corpus"
MIN_MEANINGFUL_CHARS = 500   # below this, an "indexed" PDF is effectively unreadable
PAGE = 100


def fetch_all_items(base: str, headers: dict, limit: int | None) -> tuple[list, str | None]:
    """Page through /items/top. Never silently returns a subset (SOP-003 section 5)."""
    items, start, total = [], 0, None
    while True:
        want = PAGE if limit is None else min(PAGE, limit - len(items))
        if want <= 0:
            break
        _, batch, hdrs = get_json(f"{base}/items/top?limit={want}&start={start}", headers)
        if total is None:
            total = hdrs.get("Total-Results")
        if not batch:
            break
        items.extend(batch)
        start += len(batch)
        if len(batch) < want or (limit is not None and len(items) >= limit):
            break
        time.sleep(0.1)   # courteous pacing; Zotero permits far more
    return items, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO_ROOT / ".tmp" / "zotero-corpus.json"))
    ap.add_argument("--limit", type=int, default=None, help="cap items fetched (testing)")
    ap.add_argument("--refresh", action="store_true", help="ignore the existing cache")
    args = ap.parse_args()

    env = load_env()
    missing = require(env, "ZOTERO_USER_ID", "ZOTERO_API_KEY")
    if missing:
        return emit(TOOL, MISSING, f"Missing required key(s): {', '.join(missing)}.",
                    {"missing_keys": missing})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict] = {}
    if out.exists() and not args.refresh:
        try:
            cache = {p["zotero_key"]: p for p in json.loads(out.read_text()).get("papers", [])}
        except Exception:
            cache = {}

    uid = env["ZOTERO_USER_ID"]
    base = f"https://api.zotero.org/users/{uid}"
    headers = {"Zotero-API-Key": env["ZOTERO_API_KEY"], "Zotero-API-Version": "3"}

    try:
        items, library_total = fetch_all_items(base, headers, args.limit)
        papers, fetched, reused = [], 0, 0

        for item in items:
            key = item.get("key")
            data = item.get("data") or {}
            if not key:
                continue
            if key in cache and not args.refresh:
                papers.append(cache[key]); reused += 1
                continue

            creators = data.get("creators") or []
            authors = [", ".join(filter(None, [c.get("lastName"), c.get("firstName")]))
                       or c.get("name") or "" for c in creators]
            authors = [a for a in authors if a]

            full_text, chars = "", 0
            try:
                _, children, _ = get_json(f"{base}/items/{key}/children", headers)
                pdfs = [c for c in (children or [])
                        if (c.get("data") or {}).get("contentType") == "application/pdf"]
                if pdfs:
                    _, ft, _ = get_json(f"{base}/items/{pdfs[0]['key']}/fulltext", headers)
                    full_text = (ft or {}).get("content", "") or ""
                    chars = len(full_text)
            except Exception:
                pass   # absence of full text is a fact to record, not an error to raise

            papers.append({
                "zotero_key": key,
                "title": data.get("title") or "",
                "authors": authors,
                "year": (data.get("date") or "")[:4] or None,
                "venue": data.get("publicationTitle") or data.get("bookTitle") or "",
                "doi": (data.get("DOI") or "").strip() or None,
                "abstract": data.get("abstractNote") or "",
                "item_type": data.get("itemType") or "",
                "tags": [t.get("tag") for t in (data.get("tags") or [])],
                # A near-empty index is an unreadable scan, not full text (SOP-003 5).
                "has_full_text": chars >= MIN_MEANINGFUL_CHARS,
                "full_text_chars": chars,
                "full_text": full_text,
            })
            fetched += 1
            time.sleep(0.05)
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "api.zotero.org"
        return emit(TOOL, code, detail, evidence)

    with_ft = sum(1 for p in papers if p["has_full_text"])
    payload = {
        "schema_version": "1.0.0",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "library_total_top_level": library_total,
        "papers": papers,
    }
    tmp = out.with_suffix(out.suffix + ".part")
    tmp.write_text(json.dumps(payload, indent=1))
    tmp.replace(out)   # atomic: a crash mid-write never leaves a truncated corpus

    detail = f"{len(papers)} paper(s) cached ({fetched} fetched, {reused} reused); {with_ft} with full text."
    if library_total and args.limit is None and str(library_total).isdigit() \
            and len(papers) < int(library_total):
        detail += (f" ⚠ library reports {library_total} top-level items but {len(papers)} "
                   f"were retrieved — do NOT screen this as if it were the whole library.")
        return emit(TOOL, RED, detail,
                    {"path": str(out), "papers": len(papers), "library_total": library_total})

    return emit(TOOL, GREEN, detail,
                {"path": str(out), "papers": len(papers), "with_full_text": with_ft,
                 "without_full_text": len(papers) - with_ft,
                 "library_total": library_total, "fetched": fetched, "reused": reused})


if __name__ == "__main__":
    sys.exit(main())
