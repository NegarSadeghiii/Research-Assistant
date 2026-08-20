# Research-Assistant

An end-to-end research assistant for computational research — literature → defensible
methodology → reproducible computation → validated results → publication-quality
manuscript.

Built under the **B.L.A.S.T.** protocol (Blueprint → Link → Architect → Stylize →
Trigger) with a deterministic core: business logic lives in plain scripts, not in model
reasoning. [`CLAUDE.md`](CLAUDE.md) is the project constitution and the single source of
authority — code obeys it, and a logic change updates it *before* the code.

---

## ⚠ Status: foundations built, capabilities not

**This is honest, not modest.** Nothing here has screened a paper yet.

| | |
|---|---|
| ✅ **G0 — Blueprint** | closed 2026-08-19. Requirements, data schema, and 25 behavioural rules confirmed |
| ✅ **G1 — Link** | closed 2026-08-19. Zotero, OpenAlex, PubMed, Crossref verified live |
| ✅ **G2 — Stylize** | all four payloads built and tested; screening report signed off |
| ⬜ **G3 — Trigger** | not started. No scheduled runs |

### What works today

- **Connection probes** for all five external sources, distinguishing a network-policy
  block from a rejected credential — the two look identical to a naive probe and send
  you to opposite remedies.
- **Zotero full-text coverage measurement**, which decides whether screening can read
  introductions and conclusions or is confined to metadata.
- **A registry validator** enforcing nine rules that reject unsupportable records at
  write time.
- **All four payload renderers** — screening report (HTML, grouped and filterable),
  monitoring digest (DOCX), positioning brief (DOCX), BUILD session notes (Markdown).
  The screening report shows, per record, which sections were actually read, so a
  metadata-only verdict *looks* weaker than a full-text one without any disclaimer.
- **188 passing tests**, including headless-browser tests that drive the report's
  filters and confirm no record is ever removed from the file.

- **A screening pipeline** — fetch the library, extract an anchor document, and record
  model-formed verdicts through a validating boundary that refuses anything
  unsupportable.

### What does not exist yet

External discovery and novelty assessment · anything for code, experiments, results,
or manuscripts · unattended scheduled runs.

The literature capability is the current build target. The computational and manuscript
stages are specified in `CLAUDE.md` §2.4b but deliberately unbuilt.

---

## The problem it is designed around

The failure modes that make a research assistant worse than useless all fail *silently*:

| | |
|---|---|
| **F3** | invents citations or bibliographic details |
| **F4** | claims to have read papers it only saw the abstract of |
| **F5** | treats keyword similarity as evidence of relevance |
| **F6** | declares a gap or novelty from a shallow search |

A screening tool that is 90% right is worse than none if you cannot tell which 10% —
you must re-check everything, which is the manual work it was meant to remove. And the
damage compounds forward: a fabricated citation enters a positioning brief, becomes a
premise in a methodology, and is defended in a manuscript before anyone notices.

So the design goal is not *good screening*. It is **screening whose mistakes are
visible.**

### How that is enforced

Not by instructions to the model. By structure:

- **Schema before code** — nothing is written that has no defined, auditable shape.
- **Write-time rejection** — a record that cannot substantiate itself never enters the
  registry, so it cannot be trusted later.
- **Provenance as required fields** — "what evidence was actually inspected?" is a
  column, not an aspiration.
- **A non-overridable verification stop** — an unverifiable source is never cited as
  evidence, *even on explicit instruction*. It is offered as a labelled candidate
  instead. This is the one rule a direct user instruction does not unlock.

The validator's two outcomes make the last point concrete:

| Outcome | Meaning |
|---|---|
| **Rejected** | malformed — never written at all |
| **Not usable as evidence** | valid and kept as a *candidate*, but may not enter the evidence base |

A verdict reached from keywords with no anchor document is destroyed. A real paper with
an unverified DOI is kept, flagged, and never cited as support. Nothing is lost; only
the claim to have verified it is refused.

---

## Running it

Requires Python 3.11+ and a `.env` (see [`.env.example`](.env.example)).
**Runs locally** — see `CLAUDE.md` §2.6 for why the cloud path is currently unavailable.

```bash
python3 execution/probes/run_all.py                       # G1 gate check
python3 execution/measure_zotero_coverage.py --sample 50   # full-text coverage
python3 execution/validate_registry.py                     # validate the registry
python3 execution/render_digest.py --demo --out .tmp/d.docx           # digest (BR-18)
python3 execution/render_positioning_brief.py --idea x --demo         --searched "Zotero, OpenAlex" --out .tmp/b.docx               # brief (draft only)
python3 execution/render_build_note.py --title "Paper" --stage B         --content "my purposes"                                       # BUILD note

python3 execution/tests/test_validate_registry.py          # 21 tests
python3 execution/tests/test_probe_classification.py       #  9 tests
python3 execution/tests/test_env_loading.py                # 12 tests
python3 execution/tests/test_render_screening_report.py    # 38 tests
python3 execution/tests/test_report_interactivity.py       # 32 tests (headless Chromium)
python3 execution/tests/test_render_payloads.py            # 46 tests
python3 execution/tests/test_screening_pipeline.py         # 28 tests
python3 execution/tests/test_discovery.py                  # 44 tests
python3 execution/tests/test_screening_pipeline.py         # 28 tests

python3 execution/render_screening_report.py --demo --out .tmp/demo.html   # see a report
```

Every tool prints one line of JSON to stdout and human narration to stderr, and exits
`0` green · `1` reached-but-failed · `2` blocked by network policy · `3` missing
credential · `4` invalid data.

---

## Layout

```
CLAUDE.md              the constitution — rules, schema, gates, decisions
/architecture/         Layer A — SOPs. Written before the code they govern
/execution/            Layer T — deterministic, individually testable scripts
/state/                operational memory (auto-updated)
  paper-registry.json    screening verdicts, reasons, identifiers, provenance
  digest-history.json    what has already been shown
  research-profile.md    what screening filters against
/memory/               task_plan · findings · progress · decisions
/.tmp/                 ephemeral workbench (gitignored)
```

Payload directories (`/literature-notes/`, `/screening-results/`,
`/positioning-briefs/`, `/literature-digests/`) are created when the tools that write
them exist.

---

## The nine-stage lifecycle

`literature → research idea → methodology → mathematical formulation → code →
computational experiments → results → interpretation → manuscript`

Three rules govern it (`CLAUDE.md` §2.4b, §2.4c):

1. Never skip a stage that still holds an unresolved research decision.
2. Each stage consumes the **approved** outputs of the previous one — not its drafts.
3. An existing project is entered by **audit**, not restart: establish which stages are
   complete, audit their outputs, and do not redo work that holds up.

Every arrow is an approval boundary, and an approval boundary is where an unverified
claim would otherwise be laundered into an established one.

---

## Roadmap

| Stage | Capability | Status |
|---|---|---|
| 1 | Literature intelligence | ✅ **complete** — discovery, screening, positioning, digest |
| 2 | Methodology development & defence | ⏸ specified, unbuilt |
| 3 | Reproducible computational research | ⏸ specified, unbuilt |
| 4 | Manuscript development | ⏸ specified, unbuilt |

Next: G3 (Trigger) — scheduling the twice-weekly digest. Blocked on the runtime
question (D-039), not on any missing capability.

---

*Not a general-purpose literature tool. Built for one researcher's workflow, and
opinionated accordingly — see `CLAUDE.md` for every rule and the reasoning behind it.*
