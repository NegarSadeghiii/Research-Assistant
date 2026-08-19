# CLAUDE.md — Project Constitution: Research-Assistant

> This file is the single source of authority for this project. Code obeys this
> document; when logic changes, this document and the relevant `/architecture/` SOP
> are updated **before** the code.

**Build protocol:** B.L.A.S.T. (Blueprint → Link → Architect → Stylize → Trigger)
**Build layers:** A.N.T. (Architecture → Navigation → Tools)
**Current state:** 🔴 **HALTED — Protocol 0.** Awaiting Blueprint discovery answers.

---

## 0. Hard Gates

| Gate | Condition to pass | Status |
|---|---|---|
| **G0 — Blueprint** | Q1–Q5 answered, Data Schema below filled, user approves | ❌ OPEN |
| **G1 — Link** | Every credential probed green, logged in `progress.md` | ⏸ blocked by G0 |
| **G2 — Stylize** | Every output has a verify command; user signs off | ⏸ blocked by G1 |
| **G3 — Trigger** | Firing mechanism live and documented below | ⏸ blocked by G2 |

**While G0 is open, writing logic into `/execution/` is forbidden.**

---

## 1. Data Schema (Data-First Rule)

> ⛔ **NOT YET DEFINED.** Coding begins only once the Payload shape is confirmed.
> This section is filled from the answers to Q3 (Source of Truth) and Q4 (Delivery
> Payload), and must be confirmed by the user before any script is written.

### Input shape
```json
{ "_status": "undefined — pending Blueprint Q1–Q5" }
```

### Output shape (the Payload)
```json
{ "_status": "undefined — pending Blueprint Q1–Q5" }
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
| 1 | **North Star** — the singular outcome that means we won | *unanswered* |
| 2 | **Integrations** — external services + credential readiness | *unanswered* |
| 3 | **Source of Truth** — where the primary data lives | *unanswered* |
| 4 | **Delivery Payload** — how and where the result lands | *unanswered* |
| 5 | **Behavioral Rules** — tone, must-dos, must-nots, refusals | *unanswered* |

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
| — | — | — | — | not configured |

---

## 3. Behavioral Rules

*Pending Q5.* Until then, the operating principles below apply.

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
