# SOP-005 — External discovery and reconciliation

**Status:** active · **Owner:** Layers A + N + T · **Created:** 2026-08-19
**Implements:** CLAUDE.md §2.1 (positioning, novelty, monitoring), §2.5, BR-3, BR-7,
BR-13, BR-14, D-010.
**Completes:** Stage 1. Screening sees only the library; discovery is what lets the
system answer *"has someone already published this?"*

## 1. Goal

Find work outside the library that bears on an anchor document — including work that
uses **different terminology for the same idea** — and reconcile it against what is
already known, without ever asserting a novelty claim the search cannot support.

## 2. The distinction that keeps this out of F5

Discovery runs on keywords. APIs take query strings; there is no way around that. The
guard is not to avoid keywords — it is to keep them on the correct side of a line:

| Keywords used for | Verdict |
|---|---|
| **Retrieval** — casting a net wide enough to catch candidates | ✅ legitimate and unavoidable |
| **Relevance judgement** — deciding a caught paper matters | ⛔ **this is F5** |

A keyword match makes a paper a *candidate*. Nothing more. Every candidate then goes
through SOP-003 screening, judged against the anchor document like any library paper.
Discovery never emits a verdict.

## 3. Finding different terminology for the same idea

A single query formulation returns a single vocabulary's worth of literature. Q1
explicitly requires finding work that describes the same concept differently, so two
mechanisms are used together:

1. **Multiple query formulations.** Navigation reads the anchor and produces several
   query strings covering distinct vocabularies — the field's own terms, the adjacent
   field's terms, the method's generic name. E.g. *"CAR-T supply chain scheduling"*,
   *"perishable patient-specific manufacturing scheduling"*, *"time-critical
   personalised therapy logistics"*. One query is never enough and the tool warns when
   given only one.
2. **Citation-graph expansion.** From papers already judged relevant, walk OpenAlex
   `referenced_works` (backward) and `cited_by` (forward). Citation links are
   vocabulary-independent: a paper that cites yours is related whether or not it shares
   your words. **This is the mechanism that actually defeats terminology drift**, and
   keyword search is not a substitute for it.

## 4. Sources

Per §2.5 and D-010, no single database is treated as complete.

| Source | Role | Vocabulary-independent? |
|---|---|---|
| OpenAlex | broad search + citation graph both directions | ✅ for the graph |
| PubMed | clinical / biomedical coverage | ❌ |
| Crossref | DOI validation and metadata authority | n/a |
| Consensus | available via MCP in an interactive session | ❌ |

Semantic Scholar is optional (D-038); its recommendations API would have been a third
vocabulary-independent mechanism, and its absence is a known weakness of this design.

## 5. Tool logic

### 5.1 `discover_related.py`
Takes one or more `--query` strings, optional `--since` (monitoring), optional
`--seed-doi` values (citation expansion). Queries each configured source, normalises
every hit to a common candidate shape, and writes `/.tmp/candidates.json`.

Records **per candidate** which source and which query found it, so the coverage
statement in a positioning brief can be assembled from fact rather than memory.

### 5.2 `reconcile_candidates.py`
Deduplicates and classifies against the corpus and registry (BR-14):

1. Match on normalised **DOI** first.
2. Fall back to normalised **title + year**.
3. Classify each candidate as `in_library`, `already_screened`, or `new`.
4. Where two sources disagree on year, title or authors, emit a `conflicts[]` entry with
   `status: unresolved` — **never silently choose** (BR-14, V6).

Output feeds SOP-003 screening unchanged: a discovered paper is screened against the
anchor exactly like a library paper, and lands in the registry with
`provenance.discovered_via` naming its source.

## 6. Edge cases

| Case | Handling |
|---|---|
| Only one query formulation supplied | Warn. One vocabulary is not a search (§3) |
| A source is unreachable | Report it and continue; record it as **not searched** so the coverage statement stays truthful. Never silently drop a source |
| Candidate already in the library | Classified `in_library`, not re-screened, not duplicated |
| Candidate already screened against this anchor | Classified `already_screened`; the prior verdict stands (BR-20) |
| Preprint and published version both returned | One record, two `versions[]` entries (BR-14, V9) |
| A DOI that does not resolve at Crossref | Candidate is kept but `identifier_verified` stays false → V5 marks it non-citable (§3.0) |
| Zero results | A real finding, reported as such. Never widened silently to produce hits |

## 7. What discovery does NOT do

- ⛔ **It does not assess novelty.** Finding nothing similar is not evidence of a gap
  (BR-3, P3, F6). Discovery reports what it searched and what it found; the positioning
  brief bounds any claim by that coverage.
- It does not screen. It produces candidates.
- It does not write to Zotero (BR-12) or auto-import anything (BR-13).

## 8. Verify

```
python3 execution/tests/test_discovery.py
python3 execution/discover_related.py --query "CAR-T supply chain scheduling" --dry-run
```

`--dry-run` prints the exact requests that would be issued, without issuing them, so
query construction is inspectable before any network call.

## 9. Lessons recorded

- **2026-08-19** — The first sketch had discovery emit a relevance score from query
  match strength. That is F5 with an API in front of it: a keyword hit would have
  become a relevance claim. Discovery now emits candidates only, and every one is
  screened against the anchor before any verdict exists.
- **2026-08-19** — Sources that fail must be recorded as *not searched* rather than
  omitted. A positioning brief assembles its coverage statement from this record, and a
  silently dropped source would make that statement quietly false — which is exactly
  the failure the coverage statement exists to prevent.
