#!/usr/bin/env python3
"""Deduplicate and classify discovered candidates. See SOP-005 section 5.2.

Reconciles on persistent identifiers, DOI first (BR-14). Where sources disagree on a
field, emits an unresolved conflict rather than picking a value — a silently chosen
year is a bibliographic fact no source actually asserts, which is F3 arriving through
the back door.

Verify: python3 execution/tests/test_discovery.py
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "execution"))
sys.path.insert(0, str(REPO_ROOT / "execution" / "probes"))
from validate_registry import normalize_doi, normalize_title  # noqa: E402
from _common import GREEN, emit  # noqa: E402

TOOL = "reconcile_candidates"
CONFLICT_FIELDS = ("year", "title")


def key_for(rec: dict) -> tuple[str, str]:
    """(kind, key). DOI first; title+year only as fallback (BR-14 step 2)."""
    doi = rec.get("doi")
    if doi:
        return ("doi", normalize_doi(doi))
    return ("title", f"{normalize_title(rec.get('title') or '')}|{rec.get('year') or ''}")


def merge_group(items: list[dict]) -> dict:
    """Merge duplicate hits for one work, recording disagreements rather than resolving."""
    merged = dict(items[0])
    merged["found_via"] = sorted({i.get("found_via") for i in items if i.get("found_via")})
    merged["found_by"] = sorted({str(i.get("found_by")) for i in items if i.get("found_by")})
    merged["queries"] = sorted({str(i.get("query")) for i in items if i.get("query")})

    # Prefer a non-empty value for display, but never let that hide a disagreement.
    for field in ("title", "venue", "abstract"):
        for i in items:
            if not merged.get(field) and i.get(field):
                merged[field] = i[field]
    for field in ("doi", "openalex_id", "pmid"):
        for i in items:
            if not merged.get(field) and i.get(field):
                merged[field] = i[field]
    if not merged.get("authors"):
        for i in items:
            if i.get("authors"):
                merged["authors"] = i["authors"]
                break

    conflicts = []
    for field in CONFLICT_FIELDS:
        values = {}
        for i in items:
            v = i.get(field)
            if v in (None, ""):
                continue
            norm = normalize_title(str(v)) if field == "title" else str(v)
            values.setdefault(norm, (i.get("found_via") or "?", v))
        if len(values) > 1:
            conflicts.append({
                "field": field,
                "values": {src: val for src, val in values.values()},
                "status": "unresolved",
                "flagged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
    merged["conflicts"] = conflicts
    return merged


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=str(REPO_ROOT / ".tmp" / "candidates.json"))
    ap.add_argument("--corpus", default=str(REPO_ROOT / ".tmp" / "zotero-corpus.json"))
    ap.add_argument("--registry", default=str(REPO_ROOT / "state" / "paper-registry.json"))
    ap.add_argument("--anchor", default=None,
                    help="if given, a paper already screened against THIS anchor is "
                         "classified already_screened rather than new")
    ap.add_argument("--out", default=str(REPO_ROOT / ".tmp" / "candidates-reconciled.json"))
    args = ap.parse_args()

    cand_doc = json.loads(Path(args.candidates).read_text())
    candidates = cand_doc.get("candidates", [])

    library = {}
    corpus_path = Path(args.corpus)
    if corpus_path.exists():
        for p in json.loads(corpus_path.read_text()).get("papers", []):
            library[key_for(p)] = p

    screened = {}
    reg_path = Path(args.registry)
    if reg_path.exists():
        for r in json.loads(reg_path.read_text()).get("records", []):
            ids = r.get("identifiers") or {}
            bib = r.get("bibliographic") or {}
            screened[key_for({"doi": ids.get("doi"), "title": bib.get("title"),
                              "year": bib.get("year")})] = r

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in candidates:
        groups[key_for(c)].append(c)

    out_new, out_in_library, out_already = [], [], []
    conflict_count = 0

    for key, items in groups.items():
        merged = merge_group(items)
        merged["duplicate_hits"] = len(items)
        conflict_count += len(merged["conflicts"])

        if key in library:
            merged["classification"] = "in_library"
            merged["zotero_key"] = library[key].get("zotero_key")
            out_in_library.append(merged)
            continue

        prior = screened.get(key)
        if prior is not None:
            prior_anchor = (prior.get("screening") or {}).get("anchor_document")
            # Relevance is anchor-relative: a verdict against a different anchor does not
            # settle this one (SOP-003 section 5).
            if args.anchor is None or prior_anchor == args.anchor:
                merged["classification"] = "already_screened"
                merged["prior_verdict"] = (prior.get("screening") or {}).get("verdict")
                merged["prior_anchor"] = prior_anchor
                out_already.append(merged)
                continue

        merged["classification"] = "new"
        # BR-13: staged, never auto-imported. Screening decides relevance next.
        merged["staging_state"] = "staged"
        out_new.append(merged)

    payload = {
        "schema_version": "1.0.0",
        "reconciled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "anchor": args.anchor,
        "sources_searched": cand_doc.get("sources_searched", []),
        "sources_not_searched": cand_doc.get("sources_not_searched", []),
        "queries": cand_doc.get("queries", []),
        "seed_dois": cand_doc.get("seed_dois", []),
        "counts": {"raw_candidates": len(candidates), "unique_works": len(groups),
                   "new": len(out_new), "in_library": len(out_in_library),
                   "already_screened": len(out_already), "conflicts": conflict_count},
        "new": out_new, "in_library": out_in_library, "already_screened": out_already,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1))

    detail = (f"{len(candidates)} raw → {len(groups)} unique work(s): {len(out_new)} new, "
              f"{len(out_in_library)} already in library, {len(out_already)} already screened.")
    if conflict_count:
        detail += f" {conflict_count} unresolved metadata conflict(s) flagged, none resolved."

    return emit(TOOL, GREEN, detail, {"path": str(out), **payload["counts"]})


if __name__ == "__main__":
    sys.exit(main())
