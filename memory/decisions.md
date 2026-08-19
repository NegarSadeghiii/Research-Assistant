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
