# Progress Log — Research-Assistant

Append-only. What was done, errors hit, tests run, results.

---

## 2026-08-19 — Protocol 0: Initialization

**Done**
- Inspected repository: empty, zero commits, zero remote branches.
- Created directory scaffold: `/memory/`, `/architecture/`, `/execution/`, `/.tmp/`.
- Created `/memory/task_plan.md`, `findings.md`, `progress.md`, `decisions.md`.
- Created `CLAUDE.md` as the Project Constitution with unfilled B.L.A.S.T. sections.
- Created `.gitignore` (excludes `.env` and `.tmp/` contents) and an empty
  `.env.example` placeholder.

**Errors hit:** none.

**Tests run:** none — no logic exists yet, by design.

**Result:** 🔴 **EXECUTION HALTED** per Protocol 0. Awaiting Blueprint discovery
answers Q1–Q5. No file may be written to `/execution/` until `task_plan.md` shows
an approved Blueprint and CLAUDE.md contains a confirmed Data Schema.

**Next action:** ask Q1 (North Star), one question at a time.

### Phase L — Connection Verification Results
*(empty — no integrations declared yet)*

| Service | Credential | Probe script | Result | Date |
|---|---|---|---|---|
| — | — | — | — | — |

## 2026-08-19 — Blueprint Q2 answered + early reachability probe

**Done**
- Recorded Q2 into CLAUDE.md §2.5 (Integration Register) and BR-5..BR-8.
- Ran an early reachability probe **before** architecture decisions, as the user's Q2
  instruction requires ("stop and tell me what additional access is required rather
  than silently designing around missing content").

**Probe: connector inventory (`ListConnectors`)**
Result: Canva, Consensus, Gmail, Google Calendar, Google Drive.
**No Zotero connector in this session.** Consensus is the only one enabled in chat.

**Probe: discovery APIs via container egress (`curl`)**

| Target | Result |
|---|---|
| `api.openalex.org` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `api.semanticscholar.org` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `eutils.ncbi.nlm.nih.gov` | ❌ curl (56) CONNECT tunnel failed, 403 |
| `api.crossref.org` | ❌ curl (56) CONNECT tunnel failed, 403 |

Confirmed against `$HTTPS_PROXY/__agentproxy/status`: all four logged as
`connect_rejected` — "gateway answered 403 to CONNECT (policy denial)". `selective:
false`; the `noProxy` allowlist covers only Anthropic domains and package registries
(npm, PyPI, crates, Go). This is the environment's network egress policy, not a
transient failure and not a TLS problem.

**Probe: alternate network paths**

| Path | Result |
|---|---|
| `WebFetch` → api.openalex.org | ❌ `EGRESS_BLOCKED` — same policy governs WebFetch |
| `WebSearch` | ✅ working — separate path from container egress |
| `mcp__Consensus__search` | ✅ working — live query "CAR-T cell therapy supply chain optimization" returned 20 papers / top 10 shown, including the user's own 2025 WSC papers |

**Errors hit:** the four 403s above. Diagnosed, not worked around. TLS verification
was never disabled and `HTTPS_PROXY` was never unset.

**Tests run:** 4 curl probes, 1 proxy status read, 1 WebFetch, 1 WebSearch, 1 Consensus
query. No scripts written to `/execution/` — G0 is still closed.

**External fact verified (WebSearch):** OpenAlex made API keys mandatory on
2026-02-13; polite pool discontinued, `mailto` no longer accepted; free keys with
usage-based pricing above a daily allowance. The user's Q2 statement was correct.

**Result:** 🔴 **BLOCKED on a runtime-target decision.** Stage 1's primary source
(Zotero) and 4 of 5 discovery sources are unreachable from this container. Reported
to the user rather than designed around.

### Phase L — Connection Verification Results

| Service | Credential | Probe | Result | Date |
|---|---|---|---|---|
| Zotero (connector) | n/a — connector | `ListConnectors` | ❌ not present in this session | 2026-08-19 |
| Consensus | OAuth (org) | live search | ✅ green | 2026-08-19 |
| OpenAlex | key required | curl | ❌ egress blocked | 2026-08-19 |
| Semantic Scholar | none/optional | curl | ❌ egress blocked | 2026-08-19 |
| PubMed E-utilities | optional key | curl | ❌ egress blocked | 2026-08-19 |
| Crossref | polite mailto | curl | ❌ egress blocked | 2026-08-19 |
| WebSearch | n/a | live query | ✅ green | 2026-08-19 |
