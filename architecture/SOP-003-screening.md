# SOP-003 — Screening

**Status:** active · **Owner:** Layers A + N + T · **Created:** 2026-08-19
**Implements:** CLAUDE.md §2.1 (Q1 screening requirements), §1.1–§1.2, BR-1, BR-10, D-041.

## 1. Goal

Decide, for each paper in the library, whether it is **genuinely relevant to a specific
anchor document** — and record that decision with the evidence it rests on, so the
decision can be explained months later and never has to be made twice.

## 2. The architectural problem this SOP solves

Invariant 2 says business logic lives in scripts, not model reasoning. But **relevance
is a judgement**, not a computation. "Does this paper's formulation bear on my
survival-aware MILP?" cannot be decided by a regex, and pretending otherwise produces
exactly F5 — keyword similarity dressed as relevance.

So the work is split along the A.N.T. boundary rather than forced into one layer:

| Layer | Does | Does NOT |
|---|---|---|
| **T — Tools** | fetch the corpus, extract the anchor, normalise identifiers, validate, write the registry, render payloads | judge relevance |
| **N — Navigation** | read the anchor and the paper, form a verdict, state a reason, name the evidence inspected | write to `/state/` directly |

**The model never writes the registry.** It emits verdicts as data, and
`record_screening.py` validates every one against V1–V9 before anything is stored. A
verdict without a reason, without named evidence, or without a confirmed anchor is
rejected at the boundary — so the judgement layer being probabilistic does not make the
record untrustworthy.

That is the whole design: *the model decides, the script refuses.*

## 3. Inputs

| Input | Source | Required |
|---|---|---|
| Anchor document | a path the **user names** (BR-9 — never assumed) | ✅ |
| Library corpus | Zotero Web API, cached to `/.tmp/` | ✅ |
| Research profile | `/state/research-profile.md` | optional |

## 4. Tool logic

### 4.1 `fetch_zotero_corpus.py`
Pulls top-level items and, where present, indexed attachment full text into
`/.tmp/zotero-corpus.json`. Resumable and cached — a re-run must not re-download.
Records per item whether full text was available, since that drives the evidence
threshold in 4.4.

### 4.2 `extract_anchor.py`
Reads `.docx`, `.md` or `.txt` into plain text. The anchor is what relevance is judged
**against** (BR-10); ranking by broad terms like "CAR-T" or "supply chain" is F5.

### 4.3 Navigation reads both and forms verdicts
For each paper the model states: `verdict`, `reason`, `categories`, and
`evidence_inspected` — the sections it actually read. **Free inspection is permitted
here** (BR-1): titles, abstracts, keywords, introductions, conclusions, methods. The
no-summary rule belongs to BUILD sessions, not screening.

### 4.4 Evidence thresholds — the mixed-library rule (D-041)

The library is ≈70% full text, ≈30% metadata only. The two cannot support the same
confidence:

| Evidence available | May reach | May NOT reach |
|---|---|---|
| Body text (intro / conclusion / methods) | `relevant`, `irrelevant`, `uncertain` | — |
| Metadata only (title / abstract) | `uncertain`, and `irrelevant` where the subject is plainly unrelated | **`relevant`** |

⛔ **A metadata-only record may not be marked `relevant`.** Judging a paper genuinely
relevant is a claim about its content, and an abstract is the author's advertisement for
that content. `uncertain` is the correct resting verdict (§3.2), and the screening
report displays it as metadata-only so the weakness is visible rather than asserted.

### 4.5 `record_screening.py`
Validates each verdict against V1–V9, merges into `paper-registry.json` by `record_id`,
and writes atomically. Rejected verdicts are reported with their rule violations and
**not stored**.

## 5. Edge cases

| Case | Handling |
|---|---|
| Item has no PDF | Screen from metadata; `evidence_inspected: ["title","abstract","metadata"]`; verdict capped at `uncertain` (4.4) |
| PDF present but indexed text is near-empty | Treat as metadata-only. A scanned page is not readable evidence |
| Paper already screened against the same anchor | Skipped. The prior verdict and reason stand — that is the point of retaining rejections (BR-20) |
| Paper screened against a *different* anchor | Re-screened. Relevance is anchor-relative; a fresh verdict is added, the old one is not overwritten |
| Anchor document not supplied | **Halt.** Not a degraded run — a schema error (§1.5, BR-10) |
| Zotero returns fewer items than the library holds | Report the discrepancy; never silently screen a subset |

## 6. What screening does NOT do

- It does not add papers to Zotero (BR-12 — read-only in Stage 1 v1).
- It does not decide novelty. That needs adjacent literature and belongs to positioning.
- It does not summarise anything.

## 7. Verify

```
python3 execution/tests/test_screening_pipeline.py
python3 execution/fetch_zotero_corpus.py --limit 5 --out .tmp/corpus-sample.json
python3 execution/record_screening.py --dry-run --verdicts .tmp/verdicts.json
```

## 8. Lessons recorded

- **2026-08-19** — The first design had one script that fetched, judged and wrote. That
  would have put a probabilistic judgement inside the deterministic core, and the
  registry would have inherited whatever the model produced. Splitting judgement
  (Navigation) from persistence (Tools), with validation at the boundary, is what makes
  a model-formed verdict safe to store.
- **2026-08-19** — The metadata-only cap (4.4) exists because the alternative is
  invisible. Nothing in a record marked `relevant` from an abstract alone *looks* wrong;
  the failure only surfaces when someone reads the paper. Capping at `uncertain` makes
  the limit structural instead of a matter of care.
