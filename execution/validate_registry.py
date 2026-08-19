#!/usr/bin/env python3
"""Validate paper-registry.json against CLAUDE.md section 1.2 rules V1-V9.

See /architecture/SOP-002-registry-validation.md.

Two classes of outcome, deliberately distinct:
  * REJECTION  - the record is malformed and is not written at all.
  * NOT USABLE - the record is well-formed but may not enter the evidence base
                 (section 3.0's candidate-vs-support distinction). It stays in the
                 registry as a candidate.

Verify: python3 execution/tests/test_validate_registry.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

INVALID = 4

VERDICTS = {"relevant", "uncertain", "irrelevant", "unscreened"}
CATEGORIES = {"foundational", "closest_to_work", "methodological_precedent",
              "novelty_threat", "challenges_assumption", "needs_citation_support"}
ZOTERO_STATUS = {"in_library", "not_submitted", "pending_approval", "accepted", "rejected"}
EVIDENCE_KINDS = {"title", "abstract", "metadata", "keywords", "introduction",
                  "conclusion", "methods", "results", "full_text"}
STAGING_STATES = {"staged", "accepted", "rejected"}
AUTHORITIES = {"crossref", "publisher", "zotero", "openalex", "semantic_scholar",
               "pubmed", "consensus"}
IDENTIFIER_FIELDS = ("doi", "zotero_key", "openalex_id", "pmid", "s2_id", "arxiv_id")


def normalize_doi(doi: str) -> str:
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    return re.sub(r"^doi:", "", doi)


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def compute_record_id(record: dict) -> str:
    """SHA1 of the normalized DOI, else of normalized title + year (schema section 1.1)."""
    doi = (record.get("identifiers") or {}).get("doi")
    if doi:
        basis = normalize_doi(doi)
    else:
        bib = record.get("bibliographic") or {}
        basis = f"{normalize_title(bib.get('title') or '')}|{bib.get('year') or ''}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def validate_record(record: dict) -> tuple[list[str], list[str]]:
    """Return (rejections, evidence_blocks). Empty rejections means writable."""
    rejections: list[str] = []
    evidence_blocks: list[str] = []

    screening = record.get("screening") or {}
    provenance = record.get("provenance") or {}
    bibliographic = record.get("bibliographic") or {}
    staging = record.get("staging") or {}

    verdict = screening.get("verdict", "unscreened")
    if verdict not in VERDICTS:
        rejections.append(f"screening.verdict {verdict!r} is not one of {sorted(VERDICTS)}")
    judged = verdict in VERDICTS and verdict != "unscreened"

    # V1 - a verdict must carry a stated reason, never a score alone.
    if judged and not (screening.get("reason") or "").strip():
        rejections.append("V1: screening.reason is empty but a verdict was recorded")

    # V2 - no claim about a paper without naming what was actually inspected (F4, P2).
    inspected = provenance.get("evidence_inspected") or []
    if judged and not inspected:
        rejections.append("V2: provenance.evidence_inspected is empty but a verdict was recorded")
    unknown = set(inspected) - EVIDENCE_KINDS
    if unknown:
        rejections.append(f"V2: unknown evidence_inspected values {sorted(unknown)}")

    # V3 - relevance is judged against a user-confirmed document, not keywords (F5, BR-10).
    if judged:
        if not (screening.get("anchor_document") or "").strip():
            rejections.append("V3: screening.anchor_document is missing but a verdict was recorded")
        if screening.get("anchor_document_confirmed_by_user") is not True:
            rejections.append("V3: anchor_document_confirmed_by_user is not true "
                              "(an unconfirmed anchor is exactly the BR-9 failure)")

    # V4 - metadata must name a real inspected source (F3, P1).
    authority = bibliographic.get("authority")
    if bibliographic and authority not in AUTHORITIES:
        rejections.append(f"V4: bibliographic.authority {authority!r} is not an allowed source")

    # V7 - a staged paper must state why it may matter.
    if staging.get("state") == "staged" and not (staging.get("reason_it_may_matter") or "").strip():
        rejections.append("V7: staging.reason_it_may_matter is empty for a staged paper")
    if staging and staging.get("state") not in STAGING_STATES:
        rejections.append(f"V7: staging.state {staging.get('state')!r} is not allowed")

    # Enum checks on the remaining controlled fields.
    bad_categories = set(screening.get("categories") or []) - CATEGORIES
    if bad_categories:
        rejections.append(f"screening.categories has unknown values {sorted(bad_categories)}")
    if provenance and provenance.get("zotero_status") not in ZOTERO_STATUS:
        rejections.append(f"provenance.zotero_status {provenance.get('zotero_status')!r} is not allowed")

    # V9 - record_id must match its derivation, so one work cannot become two records.
    expected = compute_record_id(record)
    actual = record.get("record_id")
    if actual and actual != expected:
        rejections.append(f"V9: record_id {actual!r} does not match its derivation {expected!r}")

    # --- Usability flags: valid record, but not admissible as evidence -------------
    # V5 - nothing enters the evidence base without a verified identifier (3.0, F3).
    identifiers = record.get("identifiers") or {}
    if not any(identifiers.get(f) for f in IDENTIFIER_FIELDS):
        evidence_blocks.append("V5: no identifier present - candidate only, never citable as support")
    elif not record.get("identifier_verified_against_source"):
        evidence_blocks.append("V5: no identifier has been verified against its source - "
                               "surface as an unverified candidate, not as support")

    # V6 - an unresolved conflict means no source is authoritative yet (BR-14, P8).
    unresolved = [c for c in (record.get("conflicts") or [])
                  if c.get("status") == "unresolved"]
    if unresolved:
        fields = sorted({c.get("field", "?") for c in unresolved})
        evidence_blocks.append(f"V6: unresolved conflict(s) on {fields} - "
                               f"surface the disagreement, do not cite as authoritative")

    return rejections, evidence_blocks


def validate_registry(registry: dict) -> dict:
    """Validate a whole registry. Zero records is a legitimate state, not an error."""
    report = {"valid": True, "records_checked": 0, "rejected": [],
              "not_usable_as_evidence": [], "duplicate_record_ids": []}

    records = registry.get("records", [])
    seen: dict[str, int] = {}

    for index, record in enumerate(records):
        report["records_checked"] += 1
        rejections, blocks = validate_record(record)
        rid = record.get("record_id") or f"<index {index}>"
        if rejections:
            report["valid"] = False
            report["rejected"].append({"record_id": rid, "reasons": rejections})
        if blocks:
            report["not_usable_as_evidence"].append({"record_id": rid, "reasons": blocks})
        # V9 - a preprint and its published version share one record_id.
        if record.get("record_id"):
            if record["record_id"] in seen:
                report["valid"] = False
                report["duplicate_record_ids"].append(record["record_id"])
            seen[record["record_id"]] = index

    return report


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("state/paper-registry.json")
    if not path.exists():
        print(json.dumps({"valid": False, "error": f"{path} not found"}))
        return INVALID

    report = validate_registry(json.loads(path.read_text()))
    print(json.dumps(report, indent=2))

    if not report["valid"]:
        print(f"\n❌ REJECTED {len(report['rejected'])} record(s) — not written.",
              file=sys.stderr)
        return INVALID

    print(f"\n✅ {report['records_checked']} record(s) valid.", file=sys.stderr)
    if report["not_usable_as_evidence"]:
        print(f"⚠️  {len(report['not_usable_as_evidence'])} record(s) are valid but NOT "
              f"citable as evidence — candidates only (§3.0).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
