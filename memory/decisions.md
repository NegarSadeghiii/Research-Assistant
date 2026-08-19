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
