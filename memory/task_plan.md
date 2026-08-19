# Task Plan — Research-Assistant

**Status:** 🔴 HALTED in Phase B (Blueprint) discovery. Q1–Q4 answered, Q5 open.
**Runtime target:** ☁ cloud environment (D-015, decided 2026-08-19).
**⚠ Blocked on user actions:** CLAUDE.md §2.7 P1–P3 — egress allowlist, Zotero
credentials, OpenAlex key. Blueprint Q3–Q5 can proceed in parallel.
**Build target:** Stage 1 — Literature Intelligence (see CLAUDE.md §2.4).
**Blueprint approved:** NO — logic is forbidden in `/execution/` until this flips to YES.

---

## Phase B — Blueprint (Vision & Logic)
- [x] Project memory initialized (`/memory/`)
- [x] CLAUDE.md created as Project Constitution
- [x] Directory scaffold created (`/architecture/`, `/execution/`, `/.tmp/`)
- [x] **Q1 — North Star:** ✅ answered — recorded verbatim in CLAUDE.md §2.1–2.3
- [x] **Q2 — Integrations:** ✅ answered — CLAUDE.md §2.5 register; BR-5..BR-8 recorded
- [x] **Q3 — Source of Truth:** ✅ answered — CLAUDE.md §2.8; `/state/` defined; BR-9..BR-16
- [x] **Q4 — Delivery Payload:** ✅ answered — CLAUDE.md §2.9; open items O1–O3 in §2.10
- [ ] **Q5 — Behavioral Rules:** tone, must-dos, must-nots, refusal triggers
- [ ] Data Schema (Input → Output) written into CLAUDE.md
- [ ] Research prior art → log in `findings.md`
- [ ] **GATE: user approves Blueprint**

## Phase L — Link (Connectivity)
- [ ] **P1 (user)** — egress policy widened for the 6 required hosts (§2.7), new session started
- [ ] **P2 (user)** — Zotero API key + userID created
- [ ] **P3 (user)** — OpenAlex API key created
- [ ] **P4** — measure Zotero full-text coverage; halt and report if inadequate (BR-8)
- [ ] `.env` populated with every credential from Q2
- [ ] Probe script per external service in `/execution/probes/`
- [ ] Every probe green, results logged in `progress.md`
- [ ] **GATE: no red links**

## Phase A — Architect (A.N.T. 3-layer)
- [ ] **A** — SOP markdown per capability in `/architecture/`
- [ ] **N** — Navigation/routing layer defined
- [ ] **T** — Atomic, testable scripts in `/execution/`

## Phase S — Stylize (Refinement & Delivery)
- [ ] Payload formatted for its destination
- [ ] UI/UX pass (if a frontend exists)
- [ ] Every output has a test / screenshot / one-line verify command
- [ ] **GATE: user signs off on the stylized result**

## Phase T — Trigger (Deployment & Self-Healing)
- [ ] Logic moved to production
- [ ] Firing mechanism configured + documented in CLAUDE.md
- [ ] Maintenance log finalized
- [ ] Self-annealing repair loop documented

---

## Stage 1 — Literature Intelligence: sub-capabilities
Scoped from Q1. Not planned in detail until G0 closes.

| ID | Capability | Depends on |
|---|---|---|
| 1a | Zotero-backed screening / classification / prioritization | Q2, Q3 |
| 1b | BUILD-guided deep reading (no-summary discipline) | Q5 |
| 1c | Positioning + adversarial novelty assessment | Q2, Q4 |
| 1d | New-publication monitoring digest | Q2, Q4, Phase T |

## Open Questions Blocking Progress
1. ✅ ~~Runtime target~~ — resolved: cloud environment (D-015). Superseded by the
   §2.7 prerequisites, which are user actions rather than open questions.
2. ✅ ~~Q3~~ — answered.
3. ✅ ~~Q4~~ — answered. Three follow-ups remain open as O1–O3 (§2.10):
   save semantics, digest timezone, and the branch unattended runs push to.
4. **Q5 — Behavioral Rules:** BUILD session boundary, challenge intensity, refusal
   triggers, evidence-citation format.
