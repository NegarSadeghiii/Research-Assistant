# CLAUDE.md — Project Constitution: Research-Assistant

> This file is the single source of authority for this project. Code obeys this
> document; when logic changes, this document and the relevant `/architecture/` SOP
> are updated **before** the code.

**Build protocol:** B.L.A.S.T. (Blueprint → Link → Architect → Stylize → Trigger)
**Build layers:** A.N.T. (Architecture → Navigation → Tools)
**Current state:** 🔴 **HALTED — Phase B.** Q1–Q3 answered. Q4–Q5 open.
**Runtime target:** ☁ **this cloud environment** (decided 2026-08-19, D-015).
**⚠ Two user actions are prerequisites for G1** — egress allowlist + Zotero Web API
credentials. See §2.7.

---

## 0. Hard Gates

| Gate | Condition to pass | Status |
|---|---|---|
| **G0 — Blueprint** | Q1–Q5 answered, Data Schema below filled, user approves | ❌ OPEN — 1/5 answered |
| **G1 — Link** | Every credential probed green, logged in `progress.md` | ⏸ blocked by G0 |
| **G2 — Stylize** | Every output has a verify command; user signs off | ⏸ blocked by G1 |
| **G3 — Trigger** | Firing mechanism live and documented below | ⏸ blocked by G2 |

**While G0 is open, writing logic into `/execution/` is forbidden.**

---

## 1. Data Schema (Data-First Rule)

> ⛔ **NOT YET DEFINED.** Coding begins only once the Payload shape is confirmed.
> Filled from Q3 (Source of Truth) and Q4 (Delivery Payload), and confirmed by the
> user before any script is written.

### Input shape
```json
{ "_status": "undefined — pending Blueprint Q3–Q4" }
```

### Output shape (the Payload)
```json
{ "_status": "undefined — pending Blueprint Q3–Q4" }
```

### Field contract
| Field | Type | Required | Source | Notes |
|---|---|---|---|---|
| — | — | — | — | pending |

---

## 2. B.L.A.S.T. Phase Outputs

### B — Blueprint
| # | Question | Answer |
|---|---|---|
| 1 | **North Star** | ✅ **ANSWERED** — see §2.1. End-to-end research assistant: literature → defensible methodology → reproducible computation → validated results → publication-quality manuscript. **Build order starts with Literature Intelligence.** |
| 2 | **Integrations** — external services + credential readiness | ✅ **ANSWERED** — see §2.5 register. Zotero via existing connector (preferred); discovery stack = Consensus + OpenAlex + Semantic Scholar + PubMed/PMC + Crossref. **Runtime blocker in §2.6.** |
| 3 | **Source of Truth** — where the primary data lives | ✅ **ANSWERED** — see §2.8. Research material is location-variable and must be *asked for*; operational state lives in `/state/`; Zotero is read-only in Stage 1 v1; discovered papers go to a staging area. |
| 4 | **Delivery Payload** — how and where the result lands | *unanswered* |
| 5 | **Behavioral Rules** — tone, must-dos, must-nots, refusals | *unanswered* |

---

### 2.1 — North Star (verbatim, Q1)

> **Long-term arc:** an end-to-end research assistant that helps me move from
> literature and research ideas to defensible methodology, reproducible
> computational work, validated results, and ultimately a publication-quality
> manuscript.
>
> **The first capability to build is the literature intelligence system.**

#### Working material
The assistant works with the papers in the **connected Zotero library**, together
with research ideas, methodology, drafts, and research questions.

#### Literature intelligence must determine
- which papers are genuinely relevant and worth my time;
- which papers are foundational, closest to my work, or important methodological precedents;
- which papers may challenge or threaten the novelty of my ideas;
- whether an idea or methodological choice I am considering has already been studied;
- where my work overlaps with or differs from the existing literature;
- what genuine research gaps may remain;
- which claims or methodological choices need literature support;
- which papers I should examine or cite;
- what assumptions I may be making that the literature challenges.

The goal is to **stop manually hunting and screening large numbers of papers**, and
to spend deep-reading time only on papers that actually matter.

#### BUILD deep reading
For papers selected for deep reading, the **BUILD active-reading workflow** applies.
The assistant must **not** replace intellectual work by summarizing those papers. It
guides, makes the user identify and articulate the ideas themselves, challenges
interpretation, and connects each paper to the user's own research.

#### Screening is NOT BUILD — hard distinction
Before a paper is selected for deep reading, the assistant **may** inspect titles,
abstracts, metadata, keywords, introductions, conclusions, and any other sections
needed to screen, classify, compare, and prioritize.
**The no-summary rule applies only when a BUILD session is explicitly begun.**

#### Monitoring digest
Eventually: monitor newly published research in areas of interest and deliver a
recurring, **highly filtered** digest. Each recommended paper must carry an
explanation of *why it may matter to current research*. Miss nothing important;
surface nothing irrelevant.

#### Positioning against the literature
When the user proposes an idea, model, assumption, or methodological choice, the
assistant actively hunts for the **strongest related and competing work — including
papers using different terminology for similar ideas** — and determines what has
already been done, what is actually different, who must be cited, and whether the
proposed contribution is strong enough.

It **challenges rather than validates**. It continually asks:
- Where should I change my perspective?
- Is the approach I have chosen actually the right way to solve this problem?
- What am I taking for granted that I should not be?
- What is the strongest existing paper that could undermine my novelty claim?

> ⛔ **Novelty rule:** never declare something novel or a research gap merely because
> no identical paper was found. Novelty assessment must consider **conceptual,
> methodological, contextual, and application-level** similarity across **adjacent**
> literatures.

#### Computational stage (later)
After positioning and methodology defense: translate approved methodology into
reproducible code, work with relevant GitHub repositories, design computational
experiments, extract and analyze results, validate them, identify unexpected
behavior, and connect findings back to the research question and literature.

> The user must understand and be able to defend **every** modeling and computational
> decision. The assistant explains formulations, assumptions, algorithms, code logic,
> experimental choices, and interpretations **before or while** implementing — never
> delivering finished code the user cannot explain.

#### Manuscript stage (final, separate)
Manuscript development is a **separate final research stage, not automatic prose
generation from raw results**. Before drafting, the system verifies that research
question, claimed contribution, literature positioning, methodology, experiments,
results, interpretation, and limitations are **internally consistent and supported
by evidence**.

Writing standard: the clarity, precision, scientific storytelling, evidence
discipline, and narrative coherence of top-tier publications such as *Nature*,
combined with the methodological rigor expected by leading **operations research**
journals. Structure, terminology, contribution framing, and formatting follow the
**target journal's** conventions rather than imitating *Nature*.

To be handled by a specialized role/subagent using approved research decisions,
literature findings, methodology, code outputs, experiments, figures, tables, and
validated results as its evidence base.

---

### 2.2 — Definition of Success (Q1)

- [ ] I no longer manually hunt for and screen large numbers of papers.
- [ ] I do not miss important new papers in my research area.
- [ ] I spend my deep-reading time on papers that are genuinely relevant.
- [ ] When I develop an idea or methodology, I can quickly understand how it is positioned relative to the literature.
- [ ] I know what has already been done, what remains genuinely different, who I should cite, and what I need to investigate next.
- [ ] Important assumptions and methodological choices are challenged before they become embedded in my models.
- [ ] My computational experiments are reproducible and traceable to explicit research decisions.
- [ ] Results are critically validated before conclusions are drawn.
- [ ] The final manuscript is built from an auditable chain of literature evidence, research decisions, methodology, computational results, and interpretation.

### 2.3 — Definition of Failure (Q1) — treat as blocking defects

| # | Failure mode |
|---|---|
| F1 | Misses key papers |
| F2 | Recommends large numbers of irrelevant papers |
| F3 | **Invents citations or bibliographic information** |
| F4 | **Makes claims about papers it has not actually inspected** |
| F5 | Treats keyword similarity as evidence of true relevance |
| F6 | Declares a research gap or novelty without sufficient evidence |
| F7 | Summarizes papers during BUILD sessions instead of making the user do the work |
| F8 | Fails to distinguish what a paper explicitly states from what the assistant is inferring |
| F9 | Agrees with research ideas without sufficiently challenging them |
| F10 | Introduces modeling assumptions or code logic without making them explicit |
| F11 | Produces computational results that cannot be reproduced or traced |
| F12 | Drafts polished manuscript text before the underlying science is sufficiently validated |

> These are not style preferences. Each failure mode must map to an explicit guard in
> an `/architecture/` SOP and, where mechanizable, a check in `/execution/`.

---

### 2.4 — Capability Roadmap

Derived from Q1. **Only Stage 1 is in scope for the current build.**

| Stage | Capability | Status |
|---|---|---|
| **1** | **Literature Intelligence** | 🟡 **CURRENT BUILD TARGET** |
| 1a | Zotero-backed screening, classification, prioritization | pending Blueprint |
| 1b | BUILD-guided deep reading (no-summary discipline) | pending Blueprint |
| 1c | Positioning + adversarial novelty assessment | pending Blueprint |
| 1d | New-publication monitoring digest | pending Blueprint |
| **2** | Methodology development & defense | ⏸ future |
| **3** | Reproducible computational research (GitHub, experiments, validation) | ⏸ future |
| **4** | Manuscript development (specialized subagent) | ⏸ future |

Stages 2–4 are recorded so the architecture does not foreclose them. **No code is
written for them until Stage 1 has landed its payload.**

---

### 2.5 — Integration Register (Q2)

**Primary literature library**

| Service | Role | Access path | Credential | Stage |
|---|---|---|---|---|
| **Zotero** | Existing personal library — the primary source for screening | **Zotero Web API** (`api.zotero.org`) — fallback path, now active | ⚠ **NOT YET CREATED** — see §2.7 | 1 |

> **Path changed 2026-08-19.** Q2 preferred the existing Claude Desktop connector and
> permitted the Web API *only if the connector proved insufficient during Phase L*.
> **That condition has fired.** The connector is a Desktop-local MCP server; the
> runtime target chosen in D-015 is this cloud container, which has no path to it.
> The connector is not "insufficient" in coverage — it is **unreachable from the
> chosen runtime**. The Web API is therefore the user's own stated fallback, not a
> deviation from the instruction. (D-009 amended, D-015.)
>
> ⚠ **Coverage remains unverified and is a live BR-8 risk.** The Web API returns
> attachment full text only for files synced to Zotero cloud storage and indexed by
> Zotero. If the library's PDFs are stored only on the local disk, or exceed the
> storage tier, the API will expose **metadata without full text** — which cannot
> satisfy the Q1 requirement to read intros and conclusions during screening.
> **This must be measured in Phase L before any screening tool is designed.**

**External discovery stack** — multiple complementary sources; no single database is
treated as complete.

| # | Service | Role | Credential status | Stage |
|---|---|---|---|---|
| 1 | **Consensus** | Finding + evaluating relevant research | ✅ connected & enabled in session | 1 |
| 2 | **OpenAlex** | Broad discovery, citation relationships, related works, author/venue metadata, snowballing | ⚠ API key required (obtainable) — see §2.6 | 1 |
| 3 | **Semantic Scholar** | Paper search, citation graph, related papers, recommendations API (positive/negative seed examples) | obtainable | 1 |
| 4 | **PubMed / PMC** | Clinical, biomedical, cell-therapy, CAR-T, survival, patient-outcome literature (NCBI E-utilities) | obtainable | 1 |
| 5 | **Crossref** | Metadata + DOI validation layer; verifying bibliographic records, resolving papers across sources | public REST API | 1 |

**Excluded / deferred**

| Service | Decision | Reason (user, Q2) |
|---|---|---|
| Google Scholar | ❌ **excluded** | No official API; scraping rejected — system must rely on stable, reproducible access paths |
| Scopus | ⏸ optional future | No institutional API credentials currently |
| Web of Science | ⏸ optional future | No institutional API credentials currently |

**GitHub**

| Repo | Role | Stage |
|---|---|---|
| `NegarSadeghiii/CAR-T-Supply-Chain` | Computational research (~10 branches; the relevant branch varies by research question/experiment) | **3** |

> **Recorded now, not built now.** GitHub is **not** an active Stage 1 dependency. Do
> not build or probe GitHub workflows unless required to understand a research idea or
> methodology document. See BR-5 and BR-6 below.

---

### 2.6 — ⚠ Runtime Reachability Findings (Phase L, run early)

Probed 2026-08-19 from the Claude Code remote container. **These are measured, not assumed.**

| Target | Result | Evidence |
|---|---|---|
| **Zotero connector** | ❌ **NOT REACHABLE** | Absent from this session's connector set (`ListConnectors` → Canva, Consensus, Gmail, Google Calendar, Google Drive). A Claude **Desktop**-local MCP server runs on the user's machine and has no network path from this cloud container. |
| OpenAlex API | ❌ blocked | `CONNECT tunnel failed, 403` — egress policy denial |
| Semantic Scholar API | ❌ blocked | `CONNECT tunnel failed, 403` |
| PubMed E-utilities | ❌ blocked | `CONNECT tunnel failed, 403` |
| Crossref API | ❌ blocked | `CONNECT tunnel failed, 403` |
| WebFetch (any of the above) | ❌ blocked | `EGRESS_BLOCKED` — same policy governs WebFetch |
| **Consensus MCP** | ✅ **working** | Live query returned real domain results, incl. the user's own 2025 WSC papers |
| **WebSearch** | ✅ **working** | Uses a separate path from container egress |

Extended probe, same session:

| Target | Result |
|---|---|
| `api.zotero.org` | ❌ blocked — 403 on CONNECT |
| `doi.org` | ❌ blocked — 403 on CONNECT |
| `export.arxiv.org` | ❌ blocked — 403 on CONNECT |
| `www.ebi.ac.uk` (Europe PMC) | ❌ blocked — 403 on CONNECT |

**Root cause, confirmed at source.** `/root/.ccr/README.md`: *"403 / 407 from the
proxy — The destination host is not allowed by your organization's egress policy for
this session. Do not retry or route around it — report the blocked host."* The
`noProxy` allowlist covers only Anthropic domains and package registries. This is the
environment's **network access policy**, not a defect.

**Consequence:** deterministic `/execution/` scripts that call OpenAlex, Semantic
Scholar, PubMed, Crossref **or Zotero** cannot run in this environment **until the
egress policy is widened**. ✅ Runtime decided (D-015); ⛔ **the policy change is now
a hard prerequisite for G1.**

**Verified external fact:** OpenAlex made API keys mandatory on **2026-02-13**;
the polite pool was discontinued and the `mailto` parameter is no longer accepted.
Free keys available at `openalex.org/settings/api`, with usage-based pricing above a
daily free allowance. (Confirms the user's Q2 statement.)

---

### 2.7 — ⛔ Prerequisites for Gate G1 (user actions — I cannot do these)

The runtime target is **this cloud environment** (D-015). That makes the following
blocking. Until both land, every Layer-T tool is unrunnable and G1 cannot be probed.

#### P1 — Widen the environment's network egress policy

The environment must allow outbound HTTPS to these hosts. All are currently denied.

| Host | Why it is needed |
|---|---|
| `api.zotero.org` | **Primary library** — the entire Stage 1 input |
| `api.openalex.org` | Discovery, citation graph, snowballing |
| `api.semanticscholar.org` | Paper search, citation graph, recommendations |
| `eutils.ncbi.nlm.nih.gov` | PubMed / PMC — clinical + CAR-T literature |
| `api.crossref.org` | DOI validation layer (the mechanical guard for F3) |
| `doi.org` | DOI resolution |
| `export.arxiv.org` | Preprints *(optional — add if arXiv coverage is wanted)* |
| `www.ebi.ac.uk` | Europe PMC *(optional — open-access full text)* |

Set on the environment, not in this session. See
<https://code.claude.com/docs/en/claude-code-on-the-web>. **A new session must be
started after the change** — policy is bound at session start.

#### P2 — Create Zotero Web API credentials

From <https://www.zotero.org/settings/keys>: create a private key (read access is
sufficient for Stage 1) and note the **userID** shown on the same page. Store as
`ZOTERO_API_KEY` and `ZOTERO_USER_ID` in `.env` — never committed.

#### P3 — Obtain an OpenAlex API key

<https://openalex.org/settings/api> — mandatory since 2026-02-13. Free tier with a
daily allowance. Store as `OPENALEX_API_KEY`.

#### P4 — Phase L must measure Zotero full-text coverage (BR-8)

Before any screening tool is designed, measure — do not assume:
- how many library items have a synced PDF attachment;
- for how many of those the API returns indexed full text;
- whether that text is real text or an empty index (scanned/unOCR'd PDFs).

If full text is unavailable at scale, **halt and report** what further access is
required. Do not design screening around metadata-only input.

---

### 2.8 — Source of Truth (Q3)

#### 2.8.1 — The user's own research material — **authoritative, location-variable**

Research ideas, methodology drafts, research questions, notes and manuscript drafts
are **the authoritative statement of what the user is currently working on**. They may
live in Google Drive, local project files, Overleaf exports, or the relevant research
Git repository — **it varies by project.**

> ⛔ **Never assume a location is authoritative.** At the start of a research task,
> **ask which document, folder, repository, or branch is the current version** unless
> it is already unambiguous. (BR-9)

> ⛔ **Positioning is anchored on the actual document, not on keywords.** Read the
> current research idea or methodology **first**, and judge relevance against *that*.
> Ranking papers from broad terms like "CAR-T", "healthcare" or "supply chain" is
> precisely failure mode **F5**. (BR-10)

#### 2.8.2 — Operational state vs intellectual output — **the BR-5 boundary**

| | **Operational system state** | **Intellectual output** |
|---|---|---|
| **Examples** | screening status; relevant/irrelevant/uncertain verdict; reason for the decision; papers already shown in a digest; date last screened; research-interest profile; identifiers (DOI, Zotero key, OpenAlex ID, PMID, S2 ID) | BUILD notes; literature review notes; gap analyses; methodology comparisons; research interpretations; manuscript drafts; argument/positioning documents |
| **Auto-update** | ✅ **allowed** — this is operational memory | ❌ **never** |
| **Lives in** | `/state/` in this repo, machine-readable | nowhere by default; saved only on approval |
| **Rule** | write freely | **BR-5** — review → confirm → *ask* whether to save → confirm path + branch |

> **BR-5 is hereby scoped:** it governs **intellectual output only**. Operational
> state is explicitly exempt. (User ruling, Q3.)

State area, kept separate from research notes and manuscript content:

```
/state/
    paper-registry.json     # screening verdicts, reasons, identifiers, dates
    digest-history.json     # what has already been shown
    research-profile.md     # active questions, methods, concepts, exclusions, priorities
```

#### 2.8.3 — Zotero write-back — **read-only in Stage 1 v1**

Zotero is the source of truth for the literature library and its bibliographic
organization. **In the first version of Stage 1, do not automatically modify Zotero.**

Reading is free. **Ask for approval before** adding a newly discovered paper, changing
tags, adding notes, moving papers between collections, or modifying metadata. (BR-12)

> Limited automatic actions — e.g. a screening tag or a dedicated machine-managed
> field — may be authorized **later, once screening is proven reliable**. That is a
> **separate explicit decision**, not an assumption this build may make.

#### 2.8.4 — Newly discovered papers — **staging, not auto-import**

Externally discovered papers are held in a staging area. **Only after approval** is a
paper added to Zotero. (BR-13) Each staging record carries:

| Field | Meaning |
|---|---|
| title, authors, year | bibliographic core |
| DOI / persistent identifier | reconciliation key |
| source | where it was discovered |
| relevance score or category | screening result |
| short reason it may matter | **required** — justification, not a score alone |
| screened? | whether screening has run |
| accepted / rejected for Zotero | the user's decision |

#### 2.8.5 — Authority when bibliographic sources conflict

1. **No discovery database automatically overrides another.**
2. **Reconcile on persistent identifiers, DOI first.**
3. For bibliographic metadata, **prefer the final publisher / Crossref record** for the
   published version when available.
4. **Zotero is authoritative for personal organization** — collections, tags, notes,
   reading status. OpenAlex, Semantic Scholar, PubMed and Consensus are **discovery
   and enrichment sources, never replacements** for the library.
5. A **preprint and its published article are versions of one research item**, not two
   independent papers, wherever that can be established.
6. ⛔ **On meaningful uncertainty — differing years, titles, versions, author lists —
   flag the conflict. Never silently choose.** (BR-14)

#### 2.8.6 — Research-interest profile

Describes active research questions, current methodological interests, important
concepts, **excluded topics**, and priority areas. The assistant **may suggest**
updates as the research evolves, but **substantive changes require approval** — the
profile directly determines future screening and digest decisions. (BR-15)

#### 2.8.7 — Provenance requirement

For every important literature judgment, it must eventually be answerable:

- where the paper came from;
- why it was considered relevant or irrelevant;
- what evidence was actually inspected;
- whether the user personally read it;
- whether BUILD was completed;
- whether it has already appeared in a digest;
- whether it has been accepted into Zotero.

> This is the operational form of invariant 11. These fields are **required columns of
> `paper-registry.json`**, not optional metadata. (BR-16)

---

### L — Link
Verified connections: *none yet.* See `/memory/progress.md` for the probe table.

### A — Architect
| Layer | Location | Contents |
|---|---|---|
| **A — Architecture** | `/architecture/` | SOPs: goal, inputs, tool logic, edge cases |
| **N — Navigation** | routing layer | reasoning + ordering; calls tools, does no heavy work itself |
| **T — Tools** | `/execution/` | atomic, deterministic, individually testable scripts |

*No SOPs or tools authored yet.*

### S — Stylize
Payload formatting rules: *pending Q4.*

### T — Trigger
| Trigger | Type | Schedule / Event | Entry point | Status |
|---|---|---|---|---|
| Monitoring digest | recurring | pending Q4 | not built | not configured |

---

## 3. Behavioral Rules

*Formally set by Q5.* These four are already binding, stated explicitly in Q1:

- **BR-1 — Screening ≠ BUILD.** Free inspection of titles, abstracts, metadata,
  keywords, intros, conclusions and other sections during screening. The no-summary
  rule activates **only** when the user explicitly begins a BUILD session.
- **BR-2 — Evidence discipline.** Never claim anything about a paper that was not
  actually inspected. Always separate *what the paper states* from *what the
  assistant infers*.
- **BR-3 — No manufactured novelty.** Absence of an identical paper is never
  evidence of a gap. Assess conceptual, methodological, contextual, and
  application-level similarity across adjacent literatures.
- **BR-4 — Challenge, don't validate.** Actively seek the strongest work that could
  undermine the user's claim. Agreement without challenge is a defect (F9).

Set by Q2, binding from now:

- **BR-5 — Nothing is committed without explicit approval.** Stage 1 working material
  (screening decisions, BUILD notes, literature comparisons, gap analyses, citation
  candidates, literature-review drafts) is **never** automatically committed or saved
  to a Git repository. After content is reviewed and confirmed, **ask** whether to save
  it. If yes, **ask which repository, branch, and destination path** unless already
  unambiguous. Never assume a draft, intermediate note, or unreviewed literature
  assessment should be committed. Save only after explicit approval of **both** the
  content **and** the destination.
- **BR-6 — Never assume `main` is authoritative.** In the computational stage, ask
  which branch is authoritative **before** reading code, extracting results, or making
  changes to `CAR-T-Supply-Chain`. `main` is not presumed to hold the current research
  version.
- **BR-7 — Stable access paths only.** No scraping of sources that lack an official
  API (explicitly: Google Scholar). Reproducibility of access is a requirement, not a
  preference.
- **BR-8 — Report missing access, don't route around it.** If a source exposes less
  content than the task needs (e.g. metadata only where full text is required), halt
  and state what additional access is required rather than silently designing around
  the gap.

Set by Q3, binding from now:

- **BR-9 — Ask which version is current.** Research material lives in different places
  per project. At the start of a research task, ask which document, folder, repository
  or branch is the current version unless it is already unambiguous.
- **BR-10 — Anchor relevance on the document, not the keyword.** Read the current
  research idea or methodology first and judge relevance against it. Broad-term
  ranking ("CAR-T", "supply chain") is failure mode F5.
- **BR-11 — Operational state auto-updates; intellectual output does not.** `/state/`
  may be written freely. BR-5 governs intellectual output only (§2.8.2).
- **BR-12 — Zotero is read-only in Stage 1 v1.** Ask before adding papers, changing
  tags, adding notes, moving collections, or editing metadata. Automatic write-back is
  a separate, later, explicit decision.
- **BR-13 — Stage discovered papers; never auto-import.** New papers wait in staging
  with a stated reason until the user accepts them into Zotero.
- **BR-14 — Reconcile by identifier; flag conflicts.** DOI first; publisher/Crossref
  record preferred for published metadata; Zotero authoritative for personal
  organization; preprint + published article are one item in two versions. On
  meaningful uncertainty, flag — never silently choose.
- **BR-15 — Profile changes need approval.** The assistant may propose updates to the
  research-interest profile; substantive changes require the user's approval because
  they steer all future screening.
- **BR-16 — Provenance is a schema requirement.** The seven provenance questions in
  §2.8.7 are required fields of the paper registry, not optional metadata.

---

## 4. Architectural Invariants

These hold regardless of what the Blueprint decides:

1. **Data-First** — input/output shape is defined and confirmed before code runs.
2. **Deterministic core** — business logic lives in plain scripts under
   `/execution/`, not in model reasoning. The model routes; the scripts decide.
3. **SOP before code** — a logic change updates the `/architecture/` SOP first.
4. **Atomic tools** — each script does one thing and is testable on its own.
5. **Credentials in `.env`** — never hardcoded, never committed. `.env.example`
   documents key names only.
6. **Intermediates through `/.tmp/`** — scraped data, drafts, and logs are
   ephemeral and gitignored. They are never the deliverable.
7. **Complete = payload landed** — the project is done when the output reaches its
   real destination, not when a script exits 0.
8. **Verify or don't ship** — every output carries a test, screenshot, or one-line
   verify command.
9. **Surgical changes** — touch only what was asked; no speculative abstractions.
10. **Never guess business logic** — ask instead.
11. **Provenance or silence** — every assertion about a paper carries a traceable
    pointer to the inspected source. Unverifiable bibliographic data is never
    emitted. (Guards F3, F4, F8.)

---

## 5. Repository Map

```
CLAUDE.md          # this file — constitution + state
.env               # credentials (gitignored; see .env.example)
/memory/           # living project memory
  task_plan.md     #   phases, goals, checklists
  findings.md      #   research, discoveries, constraints
  progress.md      #   work done, errors, tests, results
  decisions.md     #   architectural choices + reasoning
/state/            # operational memory — machine-readable, auto-updatable (BR-11)
  paper-registry.json
  digest-history.json
  research-profile.md
/architecture/     # Layer A — SOPs (the "how-to")
/execution/        # Layer T — scripts (the "engines")
/.tmp/             # ephemeral workbench (contents gitignored)
```

---

## 6. Self-Annealing Repair Loop

When anything fails:
1. **Analyze** — read the actual error and stack trace. Do not guess.
2. **Patch** — fix the script in `/execution/`.
3. **Test** — verify the fix, and record the run in `/memory/progress.md`.
4. **Update Architecture** — write the lesson into the matching `/architecture/`
   SOP so the same failure cannot recur.

---

## 7. Maintenance Log

*Finalized in Phase T.*

| Date | Event | Action taken | SOP updated |
|---|---|---|---|
| 2026-08-19 | Project initialized (Protocol 0) | Scaffold + memory + constitution | n/a |
| 2026-08-19 | Blueprint Q1 answered | North Star, success/failure criteria, capability roadmap recorded | n/a |
| 2026-08-19 | Blueprint Q2 answered | Integration register §2.5; rules BR-5..BR-8 | n/a |
| 2026-08-19 | Early reachability probe | §2.6 — Zotero + 4 discovery APIs unreachable from remote container; Consensus + WebSearch green | n/a |
| 2026-08-19 | Blueprint Q3 answered | §2.8 source-of-truth model; `/state/` defined; BR-9..BR-16; BR-5 scoped to intellectual output | n/a |
| 2026-08-19 | Runtime target decided | ☁ cloud environment (D-015); Zotero Web API activated as the user's stated fallback; §2.7 prerequisites raised | n/a |
