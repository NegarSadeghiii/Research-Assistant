# Decisions — Research-Assistant

Architectural choices and the reason behind each. Append-only.

---

### D-001 — Adopt B.L.A.S.T. + A.N.T. as the build protocol
**Date:** 2026-08-19
**Decision:** Structure the project as `/memory/`, `/architecture/` (SOPs),
`/execution/` (deterministic tools), `/.tmp/` (ephemeral), governed by `CLAUDE.md`.
**Reason:** Requested operating protocol. Separating probabilistic reasoning
(Navigation) from deterministic scripts (Tools) keeps business logic reproducible
and testable, and keeps SOPs as the source of truth ahead of code.

### D-002 — Halt before writing any logic
**Date:** 2026-08-19
**Decision:** No file in `/execution/` until Q1–Q5 are answered and the Data Schema
is confirmed in CLAUDE.md.
**Reason:** Protocol 0 gate, and the "never guess at business logic" principle. The
repo is empty, so there is no existing behavior to infer requirements from — the
name "Research-Assistant" is suggestive but not a specification. Guessing here would
cost more than asking.

### D-003 — Credentials in `.env`, never committed
**Date:** 2026-08-19
**Decision:** `.env` is gitignored; `.env.example` is committed and documents the
required keys by name only.
**Reason:** The container is ephemeral and the repo is remote. Committed secrets are
unrecoverable once pushed.

### D-004 — `.tmp/` tracked as a directory, contents ignored
**Date:** 2026-08-19
**Decision:** `.gitignore` uses `.tmp/*` + `!.tmp/.gitkeep`.
**Reason:** The workbench directory must exist on a fresh clone (scripts route
intermediate file operations through it), but its contents are ephemeral by rule.

### D-005 — Scope the build to Stage 1 (Literature Intelligence)
**Date:** 2026-08-19
**Decision:** The Q1 North Star spans four stages (literature → methodology →
computation → manuscript). Record all four in CLAUDE.md §2.4 so the architecture
does not foreclose them, but build **only Stage 1** until its payload lands.
**Reason:** The user stated it directly: "The first capability I want to build is the
literature intelligence system." Invariant 7 also defines completion as a landed
payload — a four-stage build has no landable payload until the first stage ships.

### D-006 — Failure modes F1–F12 are engineering requirements, not preferences
**Date:** 2026-08-19
**Decision:** Each of the twelve Q1 failure modes must map to an explicit guard in an
`/architecture/` SOP, and to a mechanical check in `/execution/` wherever the failure
is detectable by a script (e.g. F3 invented citations, F4 uninspected claims).
**Reason:** These describe conditions under which the user abandons the system. In a
deterministic-core architecture, a hallucinated citation is a correctness bug — it
belongs in the scripts and their tests, not in a prompt asking the model to behave.

### D-007 — Invariant 11 added: provenance or silence
**Date:** 2026-08-19
**Decision:** Added architectural invariant 11 — every assertion about a paper
carries a traceable pointer to the inspected source; unverifiable bibliographic data
is never emitted.
**Reason:** Failure modes F3, F4, and F8 all reduce to one root cause: output that
is not traceable to inspected text. A single structural invariant is cheaper to
enforce than three separate behavioral reminders.

### D-008 — BR-1: screening and BUILD are separate modes with different rules
**Date:** 2026-08-19
**Decision:** Recorded the screening/BUILD distinction as binding rule BR-1 ahead of
Q5. Screening may read any part of a paper freely; the no-summary discipline
activates only on explicit entry to a BUILD session.
**Reason:** Stated unambiguously in Q1, and it is load-bearing — a system that
applied the no-summary rule during screening could not screen at all, and one that
ignored it during BUILD would destroy the workflow's purpose (F7). The mode boundary
must therefore be an explicit, inspectable state in the design, not a matter of tone.

### D-009 — Zotero connector is the preferred path; Web API is a fallback, not a default
**Date:** 2026-08-19
**Decision:** Do not set up a Zotero Web API integration unless the existing connector
is proven insufficient during Phase L.
**Reason:** User instruction (Q2). Avoids a second credential surface and a second
sync path for the same library. Fallback remains open if connector coverage of PDF
full text turns out to be inadequate.

### D-010 — Multi-source discovery; no single database treated as complete
**Date:** 2026-08-19
**Decision:** Stage 1 discovery uses Consensus + OpenAlex + Semantic Scholar +
PubMed/PMC + Crossref, with Crossref as the DOI/metadata validation layer.
**Reason:** User instruction (Q2), and it directly serves F1 (missing key papers) and
the Q1 requirement to find work that uses *different terminology* for similar ideas —
a single index's vocabulary and coverage biases would reproduce exactly that blind
spot. Crossref as a validation layer is the mechanical guard for F3 (invented
bibliographic data): a DOI that does not resolve is not emitted.

### D-011 — No scraping; stable access paths only
**Date:** 2026-08-19
**Decision:** Google Scholar is excluded. Scopus and Web of Science are deferred as
optional future integrations, not Stage 1 requirements.
**Reason:** User instruction (Q2) — reproducible access. A scraper is also a
permanent maintenance liability whose breakage is silent, which would surface as F1.

### D-012 — Stage 1 output is never auto-committed (BR-5)
**Date:** 2026-08-19
**Decision:** Screening decisions, BUILD notes, comparisons, gap analyses, citation
candidates and review drafts are not written to Git automatically. After review and
confirmation, ask whether to save; if yes, ask repo/branch/path unless unambiguous.
**Reason:** User instruction (Q2). Consistent with invariant 6 — these are
intermediates until the user promotes them. It also protects the audit chain: an
unreviewed literature assessment in Git would later be indistinguishable from an
approved one, which is how F4 and F6 become permanent.

### D-013 — Branch must be confirmed before reading computational work (BR-6)
**Date:** 2026-08-19
**Decision:** For `NegarSadeghiii/CAR-T-Supply-Chain` (~10 branches), always ask which
branch is authoritative before reading code, extracting results, or making changes.
Never assume `main`.
**Reason:** User instruction (Q2). Reading the wrong branch produces results that
cannot be traced to a research decision — F11 — and would silently corrupt the
evidence chain the manuscript stage depends on.

### D-014 — Runtime target is an open, blocking decision
**Date:** 2026-08-19
**Decision:** Do not write any `/execution/` tool until it is decided *where the tools
run*: this remote container, the user's local machine, or a split.
**Reason:** Measured in §2.6 — the Zotero connector is absent from this session and
all four HTTP discovery APIs are blocked by the environment's egress policy (403 on
CONNECT; `WebFetch` blocked identically). Only Consensus and WebSearch work here.
A deterministic Layer-T script stack targeting OpenAlex/S2/PubMed/Crossref cannot
execute in this environment as configured. Choosing the runtime after writing the
tools would mean rewriting them; invariant 1 (Data-First) and the G0 gate both
require settling this first.

### D-015 — Runtime target: this cloud environment
**Date:** 2026-08-19
**Decision:** Layer-T tools execute in the Claude Code cloud environment, not on the
user's local machine. User's choice, made against the measured evidence in §2.6.
**Reason:** The user selected it after being shown that it requires two configuration
changes (egress allowlist, Zotero Web API). The payoff is a single reproducible
execution context: one runtime, one credential store, one set of probes, and a
monitoring digest (capability 1d) that can fire on a schedule without the user's
laptop being awake. A split runtime would have meant two sets of assumptions and a
weaker reproducibility story — which invariant 7 and F11 both penalise.
**Consequences accepted:**
- The Claude Desktop Zotero connector is out of scope; `api.zotero.org` replaces it.
- Nothing can be probed until the egress policy is widened (§2.7 P1).
- A new session is required after the policy change — policy binds at session start.

### D-009 (AMENDED 2026-08-19) — Zotero access path
**Original:** Prefer the existing Claude Desktop connector; do not set up the Zotero
Web API unless the connector proves insufficient during Phase L.
**Amendment:** The Web API is now the active path.
**Reason:** The user's own fallback condition fired, though not for the reason it
anticipated. The connector was expected to fail on *coverage* (metadata vs full
text); it instead fails on *reachability* — it is a Desktop-local MCP server and
D-015 puts the runtime in a cloud container with no path to it. The instruction's
intent (do not build a second access path unnecessarily) is preserved: the connector
cannot serve the chosen runtime at all, so the Web API is not redundant.
**Unchanged:** BR-8 still governs. The coverage question the original instruction
worried about is now *more* pressing, because the Web API exposes attachment full
text only for files synced to Zotero storage and indexed. §2.7 P4 makes measuring
this a precondition for designing any screening tool.

### D-016 — BR-5 scoped: operational state auto-updates, intellectual output does not
**Date:** 2026-08-19
**Decision:** `/state/` (paper registry, digest history, research profile) may be
written automatically. BUILD notes, gap analyses, methodology comparisons,
interpretations, positioning documents and manuscript drafts may not.
**Reason:** User ruling (Q3), and it resolves a real contradiction. BR-5 as written in
Q2 would have made the monitoring digest impossible — it cannot avoid re-showing
papers without remembering what it showed. The distinction that makes both work is
*operational memory vs intellectual product*, not *automatic vs manual*. The
boundary is now explicit in §2.8.2 so a future tool cannot quietly file a gap analysis
under "state".

### D-017 — Research material location is asked for, never assumed (BR-9)
**Date:** 2026-08-19
**Decision:** At the start of a research task, ask which document, folder, repository
or branch is the current version, unless unambiguous.
**Reason:** User instruction (Q3) — material lives in Drive, local files, Overleaf
exports or a research repo depending on the project. This is the Stage 1 analogue of
BR-6 (never assume `main`): reading a superseded methodology draft would silently
poison every downstream relevance judgment, and the error would be invisible because
the output would still look well-formed.

### D-018 — Relevance is judged against the document, not keywords (BR-10)
**Date:** 2026-08-19
**Decision:** Positioning and screening read the current research idea/methodology
first and rank against it. Broad-term ranking is prohibited.
**Reason:** User instruction (Q3), and it is the direct mechanical guard for F5
(keyword similarity treated as relevance). This constrains the Layer-T design: the
screening tool's input contract must include the anchor document, so a call without
one is a schema error rather than a silently degraded ranking.

### D-019 — Zotero is read-only in Stage 1 v1 (BR-12), with a staging area (BR-13)
**Date:** 2026-08-19
**Decision:** No automatic Zotero writes. Discovered papers accumulate in a staging
area with a stated reason and await acceptance. Automatic write-back (e.g. a screening
tag) is deferred to a separate explicit decision once screening is proven reliable.
**Reason:** User instruction (Q3). Also the safer engineering order: the library is
the one artifact in this system that is expensive to repair by hand, and an
unreliable screener writing tags into it would be difficult to unwind. Read-only
means every Stage 1 bug is recoverable by deleting a file in `/state/`.

### D-020 — Bibliographic reconciliation rules (BR-14)
**Date:** 2026-08-19
**Decision:** Reconcile on persistent identifiers, DOI first. Prefer the publisher /
Crossref record for published metadata. Zotero stays authoritative for personal
organization. Preprint and published article are one item in two versions. Flag
meaningful conflicts rather than choosing.
**Reason:** User instruction (Q3). "Flag, never silently choose" is what separates
this from a merge heuristic: a silent pick would manufacture a bibliographic record
that no source actually asserts, which is F3 arriving through the back door.

### D-021 — Provenance fields are schema, not documentation (BR-16)
**Date:** 2026-08-19
**Decision:** The seven provenance questions in §2.8.7 become required fields of
`paper-registry.json`.
**Reason:** User instruction (Q3) elevated to a schema constraint. Invariant 11 says
provenance or silence; a required field makes that enforceable by a validator instead
of relying on the model to remember. A record that cannot answer "what evidence was
inspected" fails validation rather than shipping.

### D-022 — Four payloads, four directories, three formats
**Date:** 2026-08-19
**Decision:** BUILD notes → `/literature-notes/*.md`; screening reports →
`/screening-results/YYYY-MM-DD.html`; positioning briefs →
`/positioning-briefs/idea-short-name-YYYY-MM-DD.docx`; monitoring digests →
`/literature-digests/YYYY-MM-DD.docx`. Git repo is canonical; no delivery channel
assumed before Phase T.
**Reason:** User specification (Q4). Format follows use: Markdown for notes because
they must open in Obsidian, HTML for screening because it is a scannable batch review,
DOCX for briefs and digests because they are read as documents.

### D-023 — Rejected papers are retained in screening reports (BR-20)
**Date:** 2026-08-19
**Decision:** Screening reports keep irrelevant and uncertain papers with their
reasons. Never pruned.
**Reason:** User instruction (Q4). The rejection record is what lets the system
explain a past decision and skip re-screening — it is the audit trail, not clutter.
Pruning it would also destroy the evidence needed to answer provenance question 2
(§2.8.7) for anything not accepted.

### D-024 — An empty digest is a correct result (BR-18)
**Date:** 2026-08-19
**Decision:** Zero qualifying papers ⇒ no file is written, only a short status
message. No minimum paper count.
**Reason:** User instruction (Q4). This is the structural defense against F2: a
system obliged to produce N papers per run will find N papers whether or not they
merit attention. Making emptiness a legitimate outcome removes the incentive to pad.
Writing no file at all (rather than an empty one) also keeps `/literature-digests/`
a list of periods that actually mattered.

### D-025 — Two explicit exceptions to BR-5 (BR-19)
**Date:** 2026-08-19
**Decision:** Screening reports and monitoring digests may be saved automatically;
positioning briefs may not. Authorization is the user's, given explicitly in Q4.
**Reason:** The user drew the line by degree of intellectual commitment. A screening
report records verdicts already reached mechanically; a digest is a filtered alert. A
positioning brief argues a case about the novelty of the user's own work — it must be
challenged before it is fixed in the record, or F6 becomes durable.

### D-026 — Three payload questions raised, not assumed (O1–O3)
**Date:** 2026-08-19
**Decision:** Recorded in §2.10 rather than resolved: (O1) whether "saved" means a
working-tree write or a commit + push; (O2) the timezone and hour of "Monday/Saturday
morning"; (O3) which branch unattended runs push to.
**Reason:** All three are load-bearing and none was determined by Q4. O1 is the
sharpest: the container is ephemeral, so an unattended digest that writes without
committing produces nothing that survives the session — the payload would never land,
violating invariant 7. Guessing any of the three would embed an assumption into the
Trigger design that is expensive to unwind later. Invariant 10 applies.

### D-027 — "Saved automatically" means written, committed and pushed (O1, BR-21)
**Date:** 2026-08-19
**Decision:** For screening reports and monitoring digests, the operation is not
complete until the file is committed and pushed. A run that writes without pushing
has failed and must report failure.
**Reason:** User ruling. On the cloud runtime chosen in D-015 the container is
destroyed after the session, so an uncommitted file does not exist in any durable
sense. This makes invariant 7 ("complete = payload landed") mechanically checkable:
the tool's success condition is the push, not the file write.

### D-028 — Digest schedule: Mon + Sat, 07:00 US Eastern (O2)
**Date:** 2026-08-19
**Decision:** Timezone US Eastern, per the user. Hour not specified by the user;
**07:00 assumed** and flagged as adjustable.
**Reason:** User ruling on timezone. The hour is an assumption chosen so the digest is
waiting before the working day, recorded openly rather than silently.
**Caveat carried into Phase T:** cron runs in UTC and does not observe US DST.
07:00 ET is 11:00 UTC under EDT and 12:00 UTC under EST, so one fixed expression
drifts an hour across the changeover. Phase T must accept the drift or adjust twice
yearly. Recorded now so it is not discovered as a bug later.

### D-029 — Unattended runs push to a dedicated branch (O3, BR-22)
**Date:** 2026-08-19
**Decision:** Scheduled output pushes to a dedicated branch, never the default branch.
Proposed name `automation/scheduled-output`, to be confirmed in Phase T.
**Reason:** User ruling. It keeps machine-generated output off the user's main line
until reviewed, and it means an automation bug that produces a bad digest can be
discarded by deleting a branch. Consistent with BR-6's instinct: automation does not
get to assume the default branch.

### D-030 — The verification hard stop is not overridable by user instruction
**Date:** 2026-08-19
**Decision:** If a source cannot be verified to exist, its content cannot be accessed,
or the claim cannot be supported from it, the system does not cite it as evidence —
**even on an explicit instruction to "cite it anyway."** It offers the item as an
unverified candidate for manual checking instead.
**Reason:** User ruling (Q5), stated verbatim in §3.0. This is the only rule in the
constitution that a direct instruction does not unlock, and the asymmetry is
deliberate: F3/F4 damage is silent and compounding. A fabricated citation propagates
into a positioning brief, then a manuscript, then a submission, and by the time it
surfaces the audit chain the architecture exists to protect is already broken. The
labeled-candidate escape hatch means the user loses no information — only the
false assurance that something was verified.

### D-031 — Fifteen prohibitions recorded verbatim; P15 governs
**Date:** 2026-08-19
**Decision:** P1–P15 recorded verbatim in §3.1 and mapped to the failure modes they
guard. Where any behavior appears to conflict with P15 ("never optimize for agreement
with the user; optimize for whether the research claim survives serious scrutiny"),
P15 wins.
**Reason:** User specification (Q5). Several prohibitions extend beyond Stage 1 —
manuscript claims (P7), code and scope changes (P13), causal overreach (P11) — so they
are recorded as project-wide rules rather than Stage 1 rules. Five cover ground the
F-list did not: contradiction-smoothing (P8), prestige bias (P9), causal inflation
(P11), voice-collapsing (P12), and unjustified methodological complexity (P6).

### D-032 — Data Schema drafted: one record type, nine validation rules
**Date:** 2026-08-19
**Decision:** A single paper-record type serves both library items and externally
discovered papers, distinguished by `provenance.zotero_status`. Nine validation rules
(V1–V9) reject non-conforming records at write time.
**Reason:** Data-First (invariant 1) and the G0 gate. Two design choices are load-
bearing:
1. **One record type, not two.** A staged paper and a library paper are the same
   research item at different points in a lifecycle. Two types would duplicate the
   identifier and provenance logic and let the two copies diverge — precisely the
   condition BR-14 exists to prevent.
2. **Validation, not instruction.** V1–V9 convert behavioral rules into write-time
   failures. V3 in particular makes a screening verdict without a user-confirmed
   anchor document a *schema error*, so F5 becomes structurally unreachable rather
   than merely discouraged. This is invariant 2 applied to the failure modes: the
   scripts decide, the model routes.

### D-033 — Probes classify BLOCKED separately from RED
**Date:** 2026-08-19
**Decision:** Exit code 2 (blocked by egress policy) is distinct from exit code 1
(service reached but refused). `classify_error()` separates them by whether the
failure occurred at CONNECT or in an HTTP response.
**Reason:** Both surface as "403". Conflating them would send the user to regenerate
a perfectly good API key when the real problem is a network policy — a diagnosis that
already cost real effort during the pre-probe. `/root/.ccr/README.md` also requires
policy denials be reported rather than retried, which is only possible if the tool can
recognise one. Nine tests hold the distinction in place.

### D-034 — Validation distinguishes "rejected" from "not usable as evidence"
**Date:** 2026-08-19
**Decision:** V1–V4, V7 and V9 reject a record outright. V5 and V6 instead mark it
`usable_as_evidence: false` while keeping it in the registry.
**Reason:** This is §3.0's candidate-vs-support distinction made mechanical. A paper
with an unverified identifier, or with an unresolved bibliographic conflict, is still
something the user may want to see — discarding it would lose information. What it may
not do is enter the evidence base. Rejecting it entirely would violate the spirit of
§3.0 as much as citing it would.

### D-035 — Coverage measurement is a separate tool from the connection probe
**Date:** 2026-08-19
**Decision:** `measure_zotero_coverage.py` is its own script, not a `--coverage` flag
on `probe_zotero.py`. SOP-001 amended before the code was written.
**Reason:** Invariant 4 — one job per tool. "Is the link up?" and "is the content
sufficient?" are different questions whose failures mean different things: the first
blocks G1, the second triggers the BR-8 halt-and-report. Merging them would make the
exit code ambiguous.

### D-036 — The nine-stage lifecycle is gated, not advisory (BR-23, BR-24)
**Date:** 2026-08-19
**Decision:** Recorded the user's end-to-end sequence — literature → research idea →
methodology → mathematical formulation → code → computational experiments → results →
interpretation → manuscript — in CLAUDE.md §2.4b, with three binding rules: no skipping
a stage holding an unresolved research decision, each stage consumes the *approved*
outputs of the previous one, and the manuscript stage cannot begin until methodology,
results and interpretation are all approved.
**Reason:** User specification. Recorded as architecture rather than process guidance
because every arrow between stages is an approval boundary, and an approval boundary is
precisely where an unverified claim would otherwise be laundered into an established
one. Skipping the formulation stage produces code implementing a model nobody wrote
down (F10 + F11); starting the manuscript early is F12 by definition and P7 already
forbids it. The gates are what keep the final manuscript's evidence chain traceable
back to a literature record.
**Note on axes:** §2.4b is the *research process*; §2.4 is the *build order*. They are
different axes and the mapping between them is recorded in §2.4b so neither is mistaken
for the other. The current build target remains lifecycle stage 1.

### D-037 — Skill packaging deferred until one real run has worked
**Date:** 2026-08-19
**Decision:** Do not package the literature pipeline, the research discipline, or the
B.L.A.S.T. build process as a reusable skill yet. Revisit after the egress allowlist
lands and a screening run has completed end to end against the real library.
**Reason:** User's decision, and the right one. The system has never touched real data.
The open question that matters most — whether the Zotero library exposes indexed full
text or only metadata — decides whether screening reads introductions and conclusions
or is confined to abstracts. Those are different systems with different SOPs. A skill
built now would freeze that guess and carry it into every future project, which is the
expensive kind of wrong: invisible, reusable, and inherited.
**What is genuinely ready when the time comes:** the behavioral core (BR-1..BR-24,
P1..P15, §3.0, the nine-stage gating) is complete, coherent and approval-backed, and
depends on no network access. That is the natural first skill to extract — but after
proof, not before.
