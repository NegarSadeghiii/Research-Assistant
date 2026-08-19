# SOP-002 — Paper registry validation

**Status:** active · **Owner:** Layer T · **Created:** 2026-08-19
**Implements:** CLAUDE.md §1.2 rules V1–V9.

## 1. Goal

Make the failure modes structurally unreachable rather than merely discouraged. A
record that cannot substantiate itself is **rejected at write time**, so no downstream
payload can assert something the registry cannot support.

This is invariant 2 applied to research integrity: the scripts decide, the model routes.

## 2. Inputs

A `paper-registry.json` conforming to CLAUDE.md §1.1, or a single record object.

## 3. Tool logic — the nine rules

| # | Rule | Rejects | Guards |
|---|---|---|---|
| V1 | `screening.reason` non-empty when `verdict != unscreened` | a verdict with no stated reason | score-alone verdicts |
| V2 | `provenance.evidence_inspected` non-empty when a verdict exists | claiming a judgment without naming what was read | **F4, P2** |
| V3 | `screening.anchor_document` set **and** `anchor_document_confirmed_by_user == true` when a verdict exists | ranking against keywords instead of the real document | **F5, BR-9, BR-10** |
| V4 | `bibliographic.authority` present and in the allowed enum | metadata attributed to no inspected source | **F3, P1** |
| V5 | at least one identifier verified against its source before the record is usable as evidence | citing something never confirmed to exist | **§3.0, F3** |
| V6 | any `conflicts[]` with `status == unresolved` marks the record non-authoritative | silently picking a year/title when sources disagree | **BR-14, P8** |
| V7 | `staging.reason_it_may_matter` non-empty when `state == staged` | a staged paper with no stated justification | Q3 §2.8.4 |
| V8 | `user_read` / `build_completed` may only transition via explicit user action | inferring that the user read something | **F4, P2, V8** |
| V9 | preprint + published share one `record_id`, expressed as `versions[]` | double-counting one work as two papers | **BR-14** |

### V5 and V6 are *usability* flags, not just validity flags

A record can be **valid but not citable**. V5 and V6 set `usable_as_evidence: false`
rather than rejecting the record outright — the paper still belongs in the registry as
a candidate (§3.0's candidate-vs-support distinction), it simply may not enter the
evidence base. Every other rule is a hard rejection.

## 4. Edge cases

| Case | Handling |
|---|---|
| Record has no DOI (preprint, thesis, working paper) | `record_id` falls back to SHA1 of normalized `title` + `year`; not an error |
| Two records resolve to one DOI | Merge into `versions[]`; never keep both (V9) |
| `verdict == "unscreened"` | V1–V3 do not apply; the record is a candidate, not a judgment |
| Author list differs between sources | `conflicts[]` entry, `status: unresolved` → V6 flags non-authoritative |
| Empty registry | Valid. Zero records is a legitimate state, not an error |

## 5. Verify

```
python3 execution/tests/test_validate_registry.py
```

Runs the fixture suite: one conforming record plus one deliberate violation per rule.
Exits `0` only if every rule both accepts what it should and rejects what it must.

## 6. Lessons recorded

- **2026-08-19** — V3 was written to require `anchor_document_confirmed_by_user`, not
  merely a non-empty `anchor_document`. A path alone would let a stale or guessed
  document satisfy the rule, which is exactly the BR-9 failure it exists to prevent.
