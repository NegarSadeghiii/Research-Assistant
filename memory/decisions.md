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
