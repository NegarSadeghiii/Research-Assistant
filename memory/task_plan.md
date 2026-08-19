# Task Plan — Research-Assistant

**Status:** 🔴 HALTED in Phase B (Blueprint) discovery. Q1 answered, Q2–Q5 open.
**Build target:** Stage 1 — Literature Intelligence (see CLAUDE.md §2.4).
**Blueprint approved:** NO — logic is forbidden in `/execution/` until this flips to YES.

---

## Phase B — Blueprint (Vision & Logic)
- [x] Project memory initialized (`/memory/`)
- [x] CLAUDE.md created as Project Constitution
- [x] Directory scaffold created (`/architecture/`, `/execution/`, `/.tmp/`)
- [x] **Q1 — North Star:** ✅ answered — recorded verbatim in CLAUDE.md §2.1–2.3
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

## Stage 1 — Literature Intelligence: sub-capabilities
Scoped from Q1. Not planned in detail until G0 closes.

| ID | Capability | Depends on |
|---|---|---|
| 1a | Zotero-backed screening / classification / prioritization | Q2, Q3 |
| 1b | BUILD-guided deep reading (no-summary discipline) | Q5 |
| 1c | Positioning + adversarial novelty assessment | Q2, Q4 |
| 1d | New-publication monitoring digest | Q2, Q4, Phase T |

## Open Questions Blocking Progress
1. **Q2 — Integrations:** Zotero access method + credentials; discovery sources
   beyond the library; where BUILD sessions and drafts live; GitHub repos (Stage 3).
2. **Q3 — Source of Truth:** is Zotero authoritative, and where do the user's own
   ideas / methodology / drafts / research questions live?
3. **Q4 — Delivery Payload:** shape and destination of screening reports,
   positioning briefs, and the monitoring digest.
4. **Q5 — Behavioral Rules:** BUILD session boundary, challenge intensity, refusal
   triggers, evidence-citation format.
