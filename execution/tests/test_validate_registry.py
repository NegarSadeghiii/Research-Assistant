#!/usr/bin/env python3
"""Fixture suite for the registry validator (SOP-002 section 5).

Each rule is tested twice: once that a conforming record passes, once that a
deliberate violation is caught. A rule that only ever accepts is not a guard.

Verify: python3 execution/tests/test_validate_registry.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_registry import (compute_record_id, validate_record,  # noqa: E402
                               validate_registry)

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}  {detail}")
        FAILURES.append(name)


def good_record() -> dict:
    record = {
        "identifiers": {"doi": "10.1016/j.compchemeng.2020.106913",
                        "zotero_key": "ABCD1234", "openalex_id": None,
                        "pmid": None, "s2_id": None, "arxiv_id": None},
        "identifier_verified_against_source": True,
        "bibliographic": {"title": "Optimization of CAR T-cell therapies supply chains",
                          "authors": ["Karakostas, P."], "year": 2020,
                          "venue": "Computers & Chemical Engineering",
                          "authority": "crossref"},
        "versions": [], "conflicts": [],
        "provenance": {"discovered_via": "openalex", "discovery_query": "CAR-T supply chain",
                       "first_seen": "2026-08-19",
                       "evidence_inspected": ["title", "abstract", "introduction"],
                       "full_text_available": True, "user_read": False,
                       "build_completed": False, "appeared_in_digest": [],
                       "zotero_status": "in_library"},
        "screening": {"verdict": "relevant",
                      "reason": "Same patient-centric MILP without the time-window constraint.",
                      "categories": ["methodological_precedent"],
                      "anchor_document": "drive://methodology-v3.docx",
                      "anchor_document_confirmed_by_user": True,
                      "screened_at": "2026-08-19", "screener_version": "1.0.0"},
        "staging": {"state": "accepted", "reason_it_may_matter": "Closest published formulation.",
                    "decided_at": "2026-08-19"},
    }
    record["record_id"] = compute_record_id(record)
    return record


def mutate(**path_values) -> dict:
    """Deep-copy the good record and apply 'a.b.c' -> value mutations."""
    record = good_record()
    for dotted, value in path_values.items():
        parts = dotted.split(".")
        target = record
        for part in parts[:-1]:
            target = target[part]
        if value is ...:
            target.pop(parts[-1], None)
        else:
            target[parts[-1]] = value
    return record


print("\n  Registry validator — fixture suite\n")
print("  Baseline")
rejections, blocks = validate_record(good_record())
check("conforming record is accepted", not rejections, str(rejections))
check("conforming record is usable as evidence", not blocks, str(blocks))

print("\n  Rejections (malformed — not written at all)")

r, _ = validate_record(mutate(**{"screening.reason": "  "}))
check("V1 rejects a verdict with no reason", any("V1" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"provenance.evidence_inspected": []}))
check("V2 rejects a verdict with nothing inspected", any("V2" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"provenance.evidence_inspected": ["telepathy"]}))
check("V2 rejects an unknown evidence kind", any("V2" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"screening.anchor_document": ""}))
check("V3 rejects a verdict with no anchor document", any("V3" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"screening.anchor_document_confirmed_by_user": False}))
check("V3 rejects an UNCONFIRMED anchor document", any("V3" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"bibliographic.authority": "vibes"}))
check("V4 rejects an authority that is not a real source", any("V4" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"staging.state": "staged",
                                 "staging.reason_it_may_matter": ""}))
check("V7 rejects a staged paper with no stated reason", any("V7" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"record_id": "0000000000000000000000000000000000000000"}))
check("V9 rejects a record_id that does not match its derivation",
      any("V9" in x for x in r), str(r))

r, _ = validate_record(mutate(**{"screening.verdict": "very relevant"}))
check("rejects a verdict outside the enum", bool(r), str(r))

r, _ = validate_record(mutate(**{"screening.categories": ["interesting"]}))
check("rejects a category outside the enum", bool(r), str(r))

r, _ = validate_record(mutate(**{"provenance.zotero_status": "maybe"}))
check("rejects a zotero_status outside the enum", bool(r), str(r))

print("\n  Evidence blocks (valid record, but candidate only — §3.0)")

_, b = validate_record(mutate(**{"identifier_verified_against_source": False}))
check("V5 blocks an unverified identifier from being cited as support",
      any("V5" in x for x in b), str(b))

no_ids = mutate()
no_ids["identifiers"] = {k: None for k in no_ids["identifiers"]}
no_ids["record_id"] = compute_record_id(no_ids)
_, b = validate_record(no_ids)
check("V5 blocks a record with no identifier at all", any("V5" in x for x in b), str(b))

conflicted = mutate()
conflicted["conflicts"] = [{"field": "year", "values": {"crossref": 2020, "openalex": 2019},
                            "status": "unresolved", "flagged_at": "2026-08-19"}]
r, b = validate_record(conflicted)
check("V6 blocks a record with an unresolved conflict", any("V6" in x for x in b), str(b))
check("V6 does NOT reject it — the conflict is surfaced, not discarded", not r, str(r))

resolved = copy.deepcopy(conflicted)
resolved["conflicts"][0]["status"] = "resolved_by_user"
_, b = validate_record(resolved)
check("V6 clears once the user resolves the conflict", not any("V6" in x for x in b), str(b))

print("\n  Unscreened records")
unscreened = mutate(**{"screening.verdict": "unscreened", "screening.reason": "",
                       "screening.anchor_document": "",
                       "screening.anchor_document_confirmed_by_user": False,
                       "provenance.evidence_inspected": []})
r, _ = validate_record(unscreened)
check("V1-V3 do not apply to an unscreened candidate", not r, str(r))

print("\n  Registry level")
report = validate_registry({"schema_version": "1.0.0", "records": []})
check("an empty registry is valid", report["valid"] and report["records_checked"] == 0)

dup = validate_registry({"records": [good_record(), good_record()]})
check("V9 catches two records sharing one record_id",
      not dup["valid"] and dup["duplicate_record_ids"], str(dup["duplicate_record_ids"]))

report = validate_registry({"records": [good_record()]})
check("a one-record registry is valid", report["valid"], str(report))

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} test(s) failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All validator tests passed.\n")
