# Progress Log — Research-Assistant

Append-only. What was done, errors hit, tests run, results.

---

## 2026-08-19 — Protocol 0: Initialization

**Done**
- Inspected repository: empty, zero commits, zero remote branches.
- Created directory scaffold: `/memory/`, `/architecture/`, `/execution/`, `/.tmp/`.
- Created `/memory/task_plan.md`, `findings.md`, `progress.md`, `decisions.md`.
- Created `CLAUDE.md` as the Project Constitution with unfilled B.L.A.S.T. sections.
- Created `.gitignore` (excludes `.env` and `.tmp/` contents) and an empty
  `.env.example` placeholder.

**Errors hit:** none.

**Tests run:** none — no logic exists yet, by design.

**Result:** 🔴 **EXECUTION HALTED** per Protocol 0. Awaiting Blueprint discovery
answers Q1–Q5. No file may be written to `/execution/` until `task_plan.md` shows
an approved Blueprint and CLAUDE.md contains a confirmed Data Schema.

**Next action:** ask Q1 (North Star), one question at a time.

### Phase L — Connection Verification Results
*(empty — no integrations declared yet)*

| Service | Credential | Probe script | Result | Date |
|---|---|---|---|---|
| — | — | — | — | — |

## 2026-08-19 — Blueprint Q2 answered + early reachability probe

**Done**
- Recorded Q2 into CLAUDE.md §2.5 (Integration Register) and BR-5..BR-8.
- Ran an early reachability probe **before** architecture decisions, as the user's Q2
  instruction requires ("stop and tell me what additional access is required rather
  than silently designing around missing content").

**Probe: connector inventory (`ListConnectors`)**
Result: Canva, Consensus, Gmail, Google Calendar, Google Drive.
**No Zotero connector in this session.** Consensus is the only one enabled in chat.

**Probe: discovery APIs via container egress (`curl`)**

| Target | Result |
|---|---|
| `api.openalex.org` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `api.semanticscholar.org` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `eutils.ncbi.nlm.nih.gov` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `api.crossref.org` | ❌ curl (56) CONNECT tunnel failed, 403 |

Confirmed against `$HTTPS_PROXY/__agentproxy/status`: all four logged as
`connect_rejected` — "gateway answered 403 to CONNECT (policy denial)". `selective:
false`; the `noProxy` allowlist covers only Anthropic domains and package registries
(npm, PyPI, crates, Go). This is the environment's network egress policy, not a
transient failure and not a TLS problem.

**Probe: alternate network paths**

| Path | Result |
|---|---|
| `WebFetch` → api.openalex.org | ❌ `EGRESS_BLOCKED` — same policy governs WebFetch |
| `WebSearch` | ✅ working — separate path from container egress |
| `mcp__Consensus__search` | ✅ working — live query "CAR-T cell therapy supply chain optimization" returned 20 papers / top 10 shown, including the user's own 2025 WSC papers |

**Errors hit:** the four 403s above. Diagnosed, not worked around. TLS verification
was never disabled and `HTTPS_PROXY` was never unset.

**Tests run:** 4 curl probes, 1 proxy status read, 1 WebFetch, 1 WebSearch, 1 Consensus
query. No scripts written to `/execution/` — G0 is still closed.

**External fact verified (WebSearch):** OpenAlex made API keys mandatory on
2026-02-13; polite pool discontinued, `mailto` no longer accepted; free keys with
usage-based pricing above a daily allowance. The user's Q2 statement was correct.

**Result:** 🔴 **BLOCKED on a runtime-target decision.** Stage 1's primary source
(Zotero) and 4 of 5 discovery sources are unreachable from this container. Reported
to the user rather than designed around.

### Phase L — Connection Verification Results

| Service | Credential | Probe | Result | Date |
|---|---|---|---|---|
| Zotero (connector) | n/a — connector | `ListConnectors` | ❌ not present in this session | 2026-08-19 |
| Consensus | OAuth (org) | live search | ✅ green | 2026-08-19 |
| OpenAlex | key required | curl | ❌ egress blocked | 2026-08-19 |
| Semantic Scholar | none/optional | curl | ❌ egress blocked | 2026-08-19 |
| PubMed E-utilities | optional key | curl | ❌ egress blocked | 2026-08-19 |
| Crossref | polite mailto | curl | ❌ egress blocked | 2026-08-19 |
| WebSearch | n/a | live query | ✅ green | 2026-08-19 |

## 2026-08-19 — Runtime target decided; G1 prerequisites raised

**Done**
- Probed four further candidate hosts to make the allowlist request evidence-based:
  `api.zotero.org`, `doi.org`, `export.arxiv.org`, `www.ebi.ac.uk` — **all four 403
  on CONNECT**, same egress policy denial.
- Confirmed the cause at source. `/root/.ccr/README.md`, section "403 / 407 from the
  proxy": *"The destination host is not allowed by your organization's egress policy
  for this session. Do not retry or route around it — report the blocked host."*
  Complied: reported, did not retry, did not route around.
- User chose **cloud environment** as the runtime target → D-015.
- Amended D-009: Zotero Web API becomes the active path; the user's own Phase-L
  fallback condition fired (on reachability rather than coverage).
- Wrote CLAUDE.md §2.7 — four prerequisites (P1 egress allowlist, P2 Zotero
  credentials, P3 OpenAlex key, P4 full-text coverage measurement).
- Updated `.env.example` with Zotero key names.

**Errors hit:** 4 further proxy 403s, all expected and diagnosed.

**Tests run:** 4 curl probes. Still no scripts in `/execution/` — G0 remains closed.

**Result:** Runtime unblocked as a *decision*, still blocked as a *capability*.
Nothing can be verified in Phase L until the egress policy is widened and a new
session started. Blueprint continues in parallel: Q3–Q5 do not depend on P1–P3.

**Next action:** Blueprint Q3 (Source of Truth).

## 2026-08-19 — Blueprint Q3 answered

**Done**
- Recorded Q3 into CLAUDE.md §2.8 (seven subsections) and rules BR-9..BR-16.
- Scoped BR-5 explicitly: operational state auto-updates, intellectual output does not
  (§2.8.2). This resolves the contradiction between BR-5 and capability 1d flagged
  before the question was asked.
- Defined `/state/` in the repository map: `paper-registry.json`,
  `digest-history.json`, `research-profile.md`.
- Fixed section ordering in CLAUDE.md (§2.8 had been inserted ahead of §2.7).
- Decisions D-016..D-021 recorded.

**Errors hit:** section-ordering slip in the CLAUDE.md edit; corrected in place.

**Tests run:** none — still no logic. G0 remains closed pending Q4–Q5.

**Result:** Input side of the Data Schema is now largely determined: the anchor
document, the paper registry fields, the staging record fields, and the provenance
fields all come from Q3. The output side waits on Q4.

**Next action:** Blueprint Q4 (Delivery Payload).

## 2026-08-19 — Blueprint Q4 answered

**Done**
- Recorded Q4 into CLAUDE.md §2.9: four payloads with fixed paths, formats and
  save-policies. Added BR-17..BR-20 and decisions D-022..D-026.
- Updated the Trigger table with all four entry points and the deferred notification
  mechanism; updated the Stylize section and the repository map with the four
  payload directories.
- Raised §2.10 — three open payload questions (O1 save semantics, O2 timezone,
  O3 push branch) rather than resolving them by assumption.

**Errors hit:** none.

**Tests run:** none — G0 still closed pending Q5.

**Result:** Output side of the Data Schema is now determined except for the three
open items. Both halves of the schema can be drafted once Q5 lands.

**Next action:** Blueprint Q5 (Behavioral Rules) — the final discovery question.

## 2026-08-19 — O1–O3 ruled

**Done**
- O1: "saved automatically" = written + committed + pushed. Recorded as BR-21;
  §2.10 now states that a scheduled run failing to push has failed outright.
- O2: timezone US Eastern. Hour not given — 07:00 ET assumed and flagged.
  DST caveat documented: `0 11 * * 1,6` UTC is correct under EDT only.
- O3: dedicated branch for unattended runs, never the default branch. Recorded as
  BR-22; name `automation/scheduled-output` proposed for Phase T confirmation.
- Decisions D-027..D-029; §2.10 converted from open questions to rulings.

**Errors hit:** none.

**Result:** Q4's follow-ups are closed. **Q5 remains unanswered** — it is the last
item blocking G0 along with the Data Schema.

**Next action:** Q5 (Behavioral Rules), then draft the Data Schema for approval.

## 2026-08-19 — Blueprint Q5 answered; Data Schema drafted

**Done**
- Rebuilt CLAUDE.md §3 from Q5:
  - §3.0 the non-overridable verification hard stop, with the user's verbatim
    candidate-vs-support wording;
  - §3.1 fifteen prohibitions P1–P15, each mapped to the failure mode it guards;
  - §3.2 tone / uncertainty / verbosity (assistant-proposed, marked as such);
  - §3.3 refusal policy table with an explicit overridable/not column.
- Drafted §1 Data Schema: paper record (§1.1), nine validation rules (§1.2),
  digest history (§1.3), research profile (§1.4), task input envelope (§1.5),
  output payload table (§1.6).
- Decisions D-030..D-032.

**Tests run:** all three schema JSON blocks parsed with `json.loads` — 3/3 valid.
That is the only thing in this repo currently verifiable by execution, and it passes.

**Errors hit:** none.

**Result:** 🟡 **G0 is one step from closing.** Q1–Q5 all answered, schema drafted.
Remaining: the user's approval of the schema. Still zero files in `/execution/`.

**Next action:** present the schema for approval. On approval → G0 closes → Phase L,
which is itself blocked on §2.7 P1–P3 (egress allowlist, Zotero key, OpenAlex key).

## 2026-08-19 — P2 and P3 credentials received

**Done**
- Received Zotero userID + API key (P2) and OpenAlex API key (P3) from the user.
- Wrote them to `.env`. **Verified protected before anything else:**
  - `git check-ignore -v .env` → matched by `.gitignore:2`
  - not tracked by git; absent from `git status`
  - file mode set to `600`
- Values are **not** recorded in this file, in `.env.example`, or in any commit.

**Tests run:** live credential probes, both through the container egress proxy.

| Probe | Result |
|---|---|
| `GET api.zotero.org/users/{id}/items?limit=1` with `Zotero-API-Key` | ❌ `curl (56) CONNECT tunnel failed, 403` |
| `GET api.openalex.org/works?api_key=…` | ❌ `curl (56) CONNECT tunnel failed, 403` |

**Errors hit:** both 403s. Same organization egress policy denial as before — the
request never leaves the proxy, so **the credentials themselves remain untested**.
Neither key has been shown to be valid or invalid; only that the network path is shut.

**Result:** P2 ✅ and P3 ✅ supplied. **P1 (egress allowlist) is now the sole
remaining blocker** for the whole of Phase L. Nothing about the Zotero library —
including the full-text coverage measurement required by P4 and BR-8 — can be
determined until P1 lands and a new session is started.

**⚠ Operational security note:** the credentials were pasted into the chat transcript,
which persists independently of this repository. Rotating both keys once the pipeline
is confirmed working is the clean end state. Zotero keys are revocable at
<https://www.zotero.org/settings/keys>; OpenAlex keys at
<https://openalex.org/settings/api>.

## 2026-08-19 — G0 CLOSED; Phase A SOPs + Phase L tooling built

**Done**
- User confirmed the Data Schema → **G0 closed**. `/execution/` unlocked.
- Wrote SOPs **before** code (invariant 3):
  - `SOP-000-conventions.md` — exit codes, output contract, credential and file rules
  - `SOP-001-connection-probes.md` — probe logic, edge cases, the P4 coverage measurement
  - `SOP-002-registry-validation.md` — V1–V9, rejection vs non-citable distinction
- Built Layer T:
  - `execution/probes/_common.py` — env loading, error classification, output contract
  - five atomic probes: zotero, openalex, semantic_scholar, pubmed, crossref
  - `execution/probes/run_all.py` — status table, G1 gate check, evidence to `/.tmp/`
  - `execution/measure_zotero_coverage.py` — the BR-8 / P4 measurement
  - `execution/validate_registry.py` — V1–V9 enforcement
- Initialized `/state/`: empty registry, empty digest history, profile template.

**Tests run**

| Suite | Result |
|---|---|
| `execution/tests/test_validate_registry.py` | ✅ **21/21 passed** |
| `execution/tests/test_probe_classification.py` | ✅ **9/9 passed** |
| `execution/validate_registry.py` on the initialized registry | ✅ valid, 0 records |
| `execution/probes/run_all.py` | ⛔ **5/5 blocked**, exit 1 — correct report of a true state |

**Errors hit:** none in the tooling. The five probe blocks are the environment's
egress policy, correctly classified as `blocked` (exit 2) rather than `red`.

**Result:** Everything buildable without network access is built and verified. G1
cannot pass until §2.7 P1 lands. The probe suite is ready to run the moment it does.

**Design note.** The coverage measurement was split out of the Zotero probe into its
own tool: a probe answers "is the link up?", a coverage measurement answers "is the
content sufficient?" — different questions, different failure meanings (invariant 4).
SOP-001 amended accordingly.

## 2026-08-19 — Test review; skill packaging deferred; session handoff

**Tests run for user review**

| Suite | Result |
|---|---|
| `test_validate_registry.py` | ✅ 21/21 |
| `test_probe_classification.py` | ✅ 9/9 |
| Four realistic validator scenarios | ✅ 4/4 as specified |
| `run_all.py` | ⛔ 5/5 blocked, exit 1 — correct report of a true state |

The realistic scenarios demonstrated the load-bearing asymmetry: a paper with an
unverified DOI is **kept as a candidate**, while a verdict reached from keywords with
no anchor document is **rejected outright**. Information is never lost; only the claim
to have verified it is refused (§3.0).

**Stated plainly to the user:** there are no research results to evaluate yet. Nothing
has read a paper from the library. What exists is guardrails and plumbing. What can be
reviewed today is whether the *rules* match intent — a document review, not a demo.

**Decision:** skill packaging deferred (D-037) until one real screening run works.

**Handoff:** wrote a "NEXT SESSION — START HERE" block at the top of CLAUDE.md, which
loads automatically in a fresh session. It carries the six allowlist hosts, the two
first commands, the warning that `.env` does not survive the container, and the
coverage measurement that gates the screening design.

**Next action (user):** widen the egress policy, start a new session, re-create `.env`,
run `run_all.py`.

## 2026-08-19 — G1 CLOSED; coverage measured; three defects fixed

**Runtime moved to local execution** (D-039) after the cloud environment's Custom
network access would not persist across four attempts.

**G1 — CLOSED.** From the user's machine:

| Probe | Result |
|---|---|
| Zotero | ✅ green — key accepted, userID 17704981 |
| OpenAlex | ✅ green — key accepted |
| PubMed | ✅ green — 39 records |
| Crossref | ✅ green — DOI resolved |
| Semantic Scholar | ❌ 429 unauthenticated — downgraded to optional (D-038) |

**Three defects found by first live contact, all mine, all fixed:**
1. `measure_zotero_coverage` sent an unencoded `itemType=-attachment||note` → HTTP 400.
   Fixed with `/items/top`.
2. `load_env` did not strip quotes, so a valid `KEY="abc"` became `'"abc"'` and both
   Zotero and OpenAlex rejected it. **This was the cause of the 403/401 that looked
   like bad credentials.** Fixed; 12 regression tests added.
3. `probe_crossref` asserted a false attribution for its test DOI in a comment. The
   live probe resolved a different title. Removed.

Repair loop closed: SOP-000 and SOP-001 updated with the preventing rules.

**P4 — coverage measured (BR-8 satisfied):**

```
library_total (top-level): 267
sampled: 50
items_with_pdf: 35  (70%)
pdfs_with_indexed_text: 35 / 35  (100%)
pdfs_with_meaningful_text: 35 / 35  (100%)
```

The constraint is missing attachments, not bad indexing — every PDF present is fully
readable. No OCR problem. Recorded as D-041 (mixed-evidence screening) and D-042
(library is 267 items, not 1637).

**Tests:** 21/21 validator, 9/9 classification, 12/12 env parsing.

**Next:** BR-25 audit of the existing CAR-T project, then `SOP-003-screening`.

## 2026-08-19 — Phase S begun: screening report renderer

**Done**
- `SOP-004-payload-rendering.md` — written before the code, per invariant 3. Its
  binding constraint: a renderer holds **no domain logic**. It reads records and lays
  them out; it never computes a verdict, infers a category, or adds bibliographic
  detail. This makes every renderer a pure function from records to a file, testable
  with synthetic records alone.
- `execution/render_screening_report.py` — self-contained HTML, no external assets,
  light/dark aware, print-friendly.
- `execution/tests/test_render_screening_report.py` — **28 tests**.

**Three properties the tests defend**, because they are what would make the report
dishonest:
1. **Evidence strength is visible per record** (D-041). A verdict from
   `["title","abstract"]` is labelled *metadata only*; one from
   `["title","abstract","introduction","conclusion"]` is labelled *full text*. The
   reader can see which is weaker without being told.
2. **Rejections are retained with their reasons** (BR-20) — tested by asserting every
   record reaches the page and the irrelevant record's reason is present.
3. **Non-citable records are marked as candidates** (§3.0) — V5 and V6 flags reach the
   page with their reasons, and a conflicted record shows both disputed values rather
   than a resolved one.

Also tested: HTML escaping (a `<script>` title is escaped, not executed), empty batches,
missing optional fields rendering as `—` rather than being inferred, long author lists
truncated visually while the registry stays intact, and non-ASCII titles.

**Design note.** Tallies are counted from the same records the page displays, in one
pass. An earlier sketch computed them separately, which would have created a second
place where "how many are relevant" is decided — and two places can disagree.

**Tests:** 21 validator + 9 classification + 12 env + 28 renderer = **70 passing**.

**Next:** user sign-off on the report (G2 condition), then digest / brief / BUILD note.

## 2026-08-19 — Screening report: grouping, filters, and browser tests

**User feedback on the demo report:** grouping and filters needed; provenance block is
useful, keep it; do not collapse irrelevant papers.

**Done**
- SOP-004 amended **before** the code (invariant 3) with §6.1 (interactivity is a view
  control) and §6.2 (grouping vs filtering on multi-valued categories).
- Added group-by (verdict / first category / evidence strength / none), filters for
  verdict, category, evidence strength and citability, and full-text search.
- Provenance block kept as-is; nothing collapsed.
- `execution/tests/test_report_interactivity.py` — **32 headless-browser tests** that
  drive the real controls rather than asserting on markup strings.

**Three defects the browser tests caught that markup tests could not:**
1. **Records appended past the footer.** Grouping used `container.appendChild`, which
   moved cards after the footer. Now anchored to the empty-state node.
2. **Group order not restored.** Switching from category grouping back to verdict left
   records in category order under verdict headings. The document's original node
   sequence is now captured at load and restored before every regroup.
3. **Filter checkboxes were unreachable by keyboard.** `display:none` removed them from
   the tab order; Playwright could not click what a keyboard user could not reach
   either. Replaced with a focusable visually-hidden pattern (D-045).

**One product gap found by a failing test:** searching `novelty` returned nothing even
though `novelty_threat` was visible as a chip on the card. Categories and
`discovered_via` are now in the search index — anything visible on the card is
searchable.

**One test that was wrong, not the code:** the metadata-only filter expectation was
hardcoded to 4 when the demo contains 1 such record. Expectations are now derived from
the rendered data.

**Tests:** 12 env + 10 classification + 22 validator + 38 renderer markup + 32
interactivity = **112 passing**.

## 2026-08-19 — G2 CLOSED: all four payloads built

User signed off on the screening report ("its ok"). Built the remaining three.

| Payload | Tool | Tests target |
|---|---|---|
| BUILD notes (MD) | `render_build_note.py` | BR-1 / P4 |
| Monitoring digest (DOCX) | `render_digest.py` | BR-18 |
| Positioning brief (DOCX) | `render_positioning_brief.py` | BR-3 / P3 / F6, BR-5 |

**The BUILD note format was read from the `build-lit-review` skill, not invented.** It
already defines the five-stage note structure and already writes these files; a second
format would have split the same workflow across two incompatible layouts.

**Three refusals are the point of these tools, and each is tested:**
1. A BUILD stage supplied with no content → exit 3. The tool never writes stage content
   on the reader's behalf.
2. Zero qualifying papers → **no file**, exit 0, `outcome: no_qualifying_papers`.
   Verified by asserting the target path does not exist afterwards.
3. A positioning brief with no recorded coverage → exit 3. A brief that cannot state
   what it searched cannot bound the claims it makes.

**Design decision recorded (D-047):** `uncertain` records do not qualify for the
digest. A digest asserts something is worth attention this week; uncertainty cannot
support that. They remain visible in the screening report instead.

**Tests:** 12 env + 10 classification + 22 validator + 38 renderer markup +
32 interactivity + 46 payloads = **160 passing**.

**G2 CLOSED.** Next: G3 (Trigger) is the only gate left, and it is deferred — the
Mon/Sat digest cannot run unattended until either the cloud environment is fixed or a
local scheduler is configured (D-039).

## 2026-08-19 — Screening pipeline built (SOP-003)

**The architectural question this settled.** Relevance is a judgement, not a
computation, so it cannot live in a deterministic script — but the registry must not
inherit whatever a probabilistic layer produces. Resolved by splitting along A.N.T.:

| Layer | Does | Does not |
|---|---|---|
| Tools | fetch, extract, normalise, validate, write | judge relevance |
| Navigation | read anchor + paper, form verdict, state reason and evidence | write to `/state/` |

`record_screening.py` is the boundary. Every verdict is checked against V1–V9 plus
SOP-003's screening rules; failures are reported and **not stored**.

**Built**
- `fetch_zotero_corpus.py` — paged, resumable, atomic; records per item whether indexed
  full text ≥ 500 chars was available. Reports a discrepancy rather than silently
  screening a subset of the library.
- `extract_anchor.py` — `.docx` / `.md` / `.txt` / `.tex`. **Verified against the
  user's real formulation document: 20,134 characters, 158 paragraphs, 3 tables.**
- `record_screening.py` — validating merge into the registry, atomic write.
- `test_screening_pipeline.py` — 28 tests.

**The cap that matters (D-050):** a metadata-only record cannot be marked `relevant`.
Demonstrated live — a three-verdict batch returned 1 accepted and 2 rejected: one for
claiming `relevant` from an abstract, one for an empty reason.

**Tests:** 188 passing across seven suites.

**Still missing before a real run:** nothing in the code. The remaining inputs are the
user's — run the fetch against the live library, and confirm the anchor is current.
