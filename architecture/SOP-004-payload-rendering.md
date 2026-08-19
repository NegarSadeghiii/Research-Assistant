# SOP-004 — Payload rendering (Phase S)

**Status:** active · **Owner:** Layer T · **Created:** 2026-08-19
**Implements:** CLAUDE.md §2.9 payloads 1–4, §1.6.
**Gate:** G2 closes when every payload renders with a verify command and the user signs off.

## 1. Goal

Turn registry records into the four delivery payloads, **without any renderer ever
becoming a second source of truth.**

## 2. The binding constraint

> Every payload is generated **from** `paper-registry.json`, never independently.
> (CLAUDE.md §1.6)

A renderer reads records and lays them out. It does not compute verdicts, infer
categories, soften reasons, or add bibliographic detail. If a fact is not in the
registry, it does not appear in the payload — because the registry is the only place
the validator can reach, and an assertion the validator never saw is an F3 waiting to
happen (see SOP-001 lessons, 2026-08-19: a comment carried a false claim about a real
paper precisely because it sat outside the validated data).

**Consequence:** a renderer contains no domain logic. It is a pure function from
records to a file, and it is testable with synthetic records alone.

## 3. Inputs

| Payload | Input | Path | Auto-saved |
|---|---|---|---|
| Screening report | records for one batch | `/screening-results/YYYY-MM-DD.html` | ✅ write + commit + push (BR-21) |
| Monitoring digest | records for one run | `/literature-digests/YYYY-MM-DD.docx` | ✅ write + commit + push |
| Positioning brief | records + analysis | `/positioning-briefs/idea-short-name-YYYY-MM-DD.docx` | ❌ approval-gated (BR-5, BR-19) |
| BUILD notes | one record, per stage | `/literature-notes/YYYY-MM-DD-paper-short-title.md` | incremental, approval-gated |

## 4. Tool logic — what every renderer must show

### 4.1 Evidence must be visible, not summarised

`provenance.evidence_inspected` is rendered **for every record**, verbatim. A verdict
reached from `["title", "abstract"]` must look weaker on the page than one reached from
`["title", "abstract", "introduction", "conclusion"]` — without the reader being told
so in prose.

This is D-041 made visual. The library is mixed-evidence (≈70% full text, ≈30%
metadata only), and the honest way to present that is to show it per record rather than
disclaim it once at the top.

### 4.2 Rejections are retained (BR-20)

Irrelevant and uncertain papers appear in the screening report **with their reasons**.
Never pruned to shorten the output. The rejection record is what explains a past
decision and prevents re-screening.

### 4.3 Non-citable records are marked

A record flagged by V5 (identifier unverified) or V6 (unresolved conflict) is rendered
as a **candidate**, visually distinct, and never presented as support. This is §3.0's
candidate-vs-support distinction reaching the page.

### 4.4 Voice separation (P12)

Where a renderer emits any text beyond registry fields, it must not merge *what the
paper states*, *what the assistant infers*, and *what the user hypothesises*. In
practice renderers emit registry fields only, which satisfies this by construction.

### 4.5 An empty digest produces no file (BR-18)

Zero qualifying papers ⇒ no document, a status line only. Never an empty document.

## 5. Edge cases

| Case | Handling |
|---|---|
| Zero records in a screening batch | Render the report with an explicit "no papers screened" state — a screening run that examined nothing is a fact worth recording, unlike an empty digest |
| A record with `verdict: unscreened` | Listed separately as a candidate; never counted in the verdict tallies |
| Missing optional fields (venue, year) | Rendered as `—`. **Never inferred, never left silently blank** |
| A reason containing HTML or `<script>` | Escaped. Registry text is data, not markup |
| Very long author lists | Truncated visually with the full list retained in the title attribute; the registry is unchanged |
| Non-ASCII titles | UTF-8 throughout; the HTML declares it |

## 6. Style

Per CLAUDE.md §3.2: screening is a table with one line of reasoning per paper; a digest
is a few sentences per paper at most. Reports are self-contained single files — no
external assets, no network fetches — so they open anywhere and survive archiving.

## 7. Verify

```
python3 execution/tests/test_render_screening_report.py
python3 execution/render_screening_report.py --demo --out /.tmp/demo.html
```

The demo flag renders a synthetic batch covering every state: relevant, uncertain,
irrelevant, unscreened, metadata-only evidence, unverified identifier, and an
unresolved conflict. If a state cannot be seen in the demo output, it is not covered.

## 8. Lessons recorded

- **2026-08-19** — Renderers hold no domain logic by design. The first version was
  going to compute per-tier tallies from raw fields; that would have made the report a
  second place where "how many are relevant" is decided, and the two could diverge.
  Tallies are counted from the same records the page displays, in one pass, so the
  summary cannot disagree with the table beneath it.
