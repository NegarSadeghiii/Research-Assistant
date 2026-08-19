# Task Plan — Research-Assistant

**Status:** 🔴 HALTED at Protocol 0 → Phase B (Blueprint) discovery.
**Blueprint approved:** NO — logic is forbidden in `/execution/` until this flips to YES.

---

## Phase B — Blueprint (Vision & Logic)
- [x] Project memory initialized (`/memory/`)
- [x] CLAUDE.md created as Project Constitution
- [x] Directory scaffold created (`/architecture/`, `/execution/`, `/.tmp/`)
- [ ] **Q1 — North Star:** the singular outcome that means we won
- [ ] **Q2 — Integrations:** external services + credential readiness
- [ ] **Q3 — Source of Truth:** where the primary data lives
- [ ] **Q4 — Delivery Payload:** how and where the final result lands
- [ ] **Q5 — Behavioral Rules:** tone, must-dos, must-nots, refusal triggers
- [ ] Data Schema (Input → Output) written into CLAUDE.md
- [ ] Research prior art → log in `findings.md`
- [ ] **GATE: user approves Blueprint**

## Phase L — Link (Connectivity)
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

## Open Questions Blocking Progress
1. All five Blueprint discovery questions (Q1–Q5) — unanswered.
