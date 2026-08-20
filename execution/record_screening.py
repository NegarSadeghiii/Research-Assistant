#!/usr/bin/env python3
"""Validate model-formed screening verdicts and merge them into the registry.

See SOP-003 sections 2 and 4.5.

This is the boundary between Navigation and Tools. The model forms verdicts; this
script decides whether they may be stored. A verdict missing a reason, missing the
evidence it rests on, or carrying an unconfirmed anchor is REJECTED and not written —
so a probabilistic judgement layer cannot put an unsupportable record into the registry.

    the model decides, the script refuses.

Verify: python3 execution/tests/test_screening_pipeline.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "execution"))
from validate_registry import compute_record_id, validate_record  # noqa: E402

SCREENER_VERSION = "1.0.0"
BODY_EVIDENCE = {"introduction", "conclusion", "methods", "results", "full_text"}


def build_record(v: dict, anchor: str, anchor_confirmed: bool) -> dict:
    """Assemble a schema-conforming record from a verdict plus its paper metadata."""
    paper = v.get("paper") or {}
    doi = (paper.get("doi") or "").strip() or None
    record = {
        "identifiers": {
            "doi": doi, "zotero_key": paper.get("zotero_key"),
            "openalex_id": paper.get("openalex_id"), "pmid": paper.get("pmid"),
            "s2_id": paper.get("s2_id"), "arxiv_id": paper.get("arxiv_id"),
        },
        # A Zotero item the user curated is a verified identifier: it exists in a
        # library the user controls, and we read it there. An externally discovered
        # paper is not verified until its DOI resolves against its source.
        "identifier_verified_against_source": bool(paper.get("zotero_key")) or
                                              bool(paper.get("identifier_verified")),
        "bibliographic": {
            "title": paper.get("title") or "", "authors": paper.get("authors") or [],
            "year": int(paper["year"]) if str(paper.get("year") or "").isdigit() else None,
            "venue": paper.get("venue") or "",
            "authority": paper.get("authority") or "zotero",
            "authority_retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "versions": [], "conflicts": v.get("conflicts") or [],
        "provenance": {
            "discovered_via": paper.get("discovered_via") or "zotero",
            "discovery_query": v.get("query") or "",
            "first_seen": datetime.now(timezone.utc).date().isoformat(),
            "evidence_inspected": v.get("evidence_inspected") or [],
            "full_text_available": bool(paper.get("has_full_text")),
            "user_read": False, "build_completed": False, "appeared_in_digest": [],
            "zotero_status": "in_library" if paper.get("zotero_key") else "not_submitted",
        },
        "screening": {
            "verdict": v.get("verdict") or "unscreened",
            "reason": (v.get("reason") or "").strip(),
            "categories": v.get("categories") or [],
            "anchor_document": anchor,
            "anchor_document_confirmed_by_user": anchor_confirmed,
            "screened_at": datetime.now(timezone.utc).date().isoformat(),
            "screener_version": SCREENER_VERSION,
        },
        "staging": {
            "state": "accepted" if paper.get("zotero_key") else "staged",
            "reason_it_may_matter": (v.get("reason") or "").strip() or "pending",
            "decided_at": None,
        },
    }
    record["record_id"] = compute_record_id(record)
    return record


def screening_rules(record: dict) -> list[str]:
    """Screening-specific checks layered on top of V1-V9 (SOP-003 4.4)."""
    problems = []
    inspected = set((record.get("provenance") or {}).get("evidence_inspected") or [])
    verdict = (record.get("screening") or {}).get("verdict")
    if verdict == "relevant" and not (inspected & BODY_EVIDENCE):
        problems.append(
            "SOP-003 4.4: a metadata-only record may not be marked 'relevant'. Judging a "
            "paper genuinely relevant is a claim about its content, and an abstract is "
            "the author's advertisement for that content. Use 'uncertain'.")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", required=True, help="JSON produced by the screening pass")
    ap.add_argument("--registry", default=str(REPO_ROOT / "state" / "paper-registry.json"))
    ap.add_argument("--anchor", required=True, help="the anchor document these were judged against")
    ap.add_argument("--anchor-confirmed", action="store_true",
                    help="the user confirmed this anchor is the current version (BR-9)")
    ap.add_argument("--dry-run", action="store_true", help="validate without writing")
    args = ap.parse_args()

    src = Path(args.verdicts)
    if not src.exists():
        print(json.dumps({"tool": "record_screening", "status": "invalid",
                          "detail": f"{src} not found"}))
        return 4

    payload = json.loads(src.read_text())
    verdicts = payload if isinstance(payload, list) else payload.get("verdicts", [])

    accepted, rejected = [], []
    for v in verdicts:
        record = build_record(v, args.anchor, args.anchor_confirmed)
        problems, _ = validate_record(record)
        problems += screening_rules(record)
        if problems:
            rejected.append({"title": (v.get("paper") or {}).get("title", "—"),
                             "reasons": problems})
        else:
            accepted.append(record)

    reg_path = Path(args.registry)
    existing = (json.loads(reg_path.read_text()) if reg_path.exists()
                else {"schema_version": "1.0.0", "records": []})
    by_id = {r.get("record_id"): r for r in existing.get("records", [])}

    added = updated = 0
    for r in accepted:
        if r["record_id"] in by_id:
            # Anchor-relative: a verdict against a DIFFERENT anchor replaces nothing
            # silently, it supersedes with the new anchor recorded (SOP-003 section 5).
            updated += 1
        else:
            added += 1
        by_id[r["record_id"]] = r

    if not args.dry_run:
        existing["records"] = list(by_id.values())
        existing["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = reg_path.with_suffix(".json.part")
        tmp.write_text(json.dumps(existing, indent=1))
        os.replace(tmp, reg_path)   # atomic (SOP-000 section 6)

    status = "green" if not rejected else "red"
    print(json.dumps({
        "tool": "record_screening", "status": status,
        "detail": (f"{len(accepted)} verdict(s) accepted ({added} new, {updated} updated); "
                   f"{len(rejected)} rejected and NOT written."
                   + (" Dry run — nothing written." if args.dry_run else "")),
        "evidence": {"accepted": len(accepted), "rejected": rejected,
                     "registry": str(reg_path), "dry_run": args.dry_run,
                     "anchor": args.anchor, "anchor_confirmed": args.anchor_confirmed},
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}))

    for r in rejected:
        print(f"[REJECTED] {r['title']}", file=sys.stderr)
        for reason in r["reasons"]:
            print(f"    · {reason}", file=sys.stderr)
    return 0 if not rejected else 4


if __name__ == "__main__":
    sys.exit(main())
