# SOP-001 — Phase L connection probes

**Status:** active · **Owner:** Layer T · **Created:** 2026-08-19
**Gate:** G1 closes only when every required probe reports `green`.

## 1. Goal

Prove, with evidence, that each external service in CLAUDE.md §2.5 is reachable **and**
that our credential is accepted. Until a probe is green, no tool may depend on that
service and no claim may be made about its data.

## 2. Inputs

`.env` (see `.env.example`), plus the environment's proxy and CA settings.

| Probe | Requires | Host |
|---|---|---|
| `probe_zotero.py` | `ZOTERO_USER_ID`, `ZOTERO_API_KEY` | `api.zotero.org` |
| `probe_openalex.py` | `OPENALEX_API_KEY` | `api.openalex.org` |
| `probe_semantic_scholar.py` | none (key optional) | `api.semanticscholar.org` |
| `probe_pubmed.py` | none (key optional) | `eutils.ncbi.nlm.nih.gov` |
| `probe_crossref.py` | none (`CROSSREF_MAILTO` polite) | `api.crossref.org` |

## 3. Tool logic

Each probe performs the **smallest possible authenticated read** — one item, one work,
one record. It must never page, never bulk-fetch, and never write.

1. Load `.env`. Missing required key → exit `3`, naming the key only.
2. Issue one GET through the proxy.
3. Classify:
   - transport failure whose cause is a proxy `403`/`407` on CONNECT → **blocked**, exit `2`
   - HTTP `401`/`403` *from the service itself* → **red**, exit `1` (credential rejected)
   - HTTP `2xx` with a parseable body → **green**, exit `0`
   - anything else → **red**, exit `1`
4. Emit the JSON line from SOP-000 §3.

> **The critical distinction.** A proxy denial and a rejected API key both surface as
> "403" to a careless implementation. `_common.classify_error()` separates them by
> inspecting whether the failure occurred at CONNECT (tunnel) or in the HTTP response.
> Getting this wrong sends the user to regenerate a perfectly good credential.

## 4. Edge cases

| Case | Handling |
|---|---|
| Proxy port differs from a previous session | Read `HTTPS_PROXY` at runtime; never cache it |
| Service is up but rate-limits (`429`) | **red**, exit `1`, with `Retry-After` in `evidence` — not green |
| OpenAlex key valid but daily allowance exhausted | **red**, exit `1`; the message must say *allowance*, not *invalid key* |
| Zotero key valid but scoped to the wrong library | **red**, exit `1`; report the userID actually reachable |
| Network timeout with no proxy error | **red**, exit `1` — do not report as blocked without proxy evidence |

## 5. Zotero full-text coverage — the BR-8 measurement (P4)

`execution/measure_zotero_coverage.py` measures, over a bounded sample:

- items with a PDF attachment;
- attachments for which `/items/{key}/fulltext` returns indexed content;
- whether that content is non-trivial (a scanned, un-OCR'd PDF indexes as near-empty).

⛔ **If indexed full text is unavailable at scale, halt and report** what further
access is required (BR-8). Do **not** design screening around metadata-only input —
Q1 requires reading introductions and conclusions during screening.

## 6. Verify

```
python3 execution/probes/run_all.py                    # all five links
python3 execution/measure_zotero_coverage.py --sample 25   # the P4 / BR-8 measurement
```

Prints a status table and exits non-zero if any required probe is not green.
Expected result **before** §2.7 P1 lands: every HTTP probe `blocked` (exit 2).
That is a correct run reporting a true environment state, not a tool failure.

## 7. Lessons recorded

- **2026-08-19** — Coverage measurement was split into its own script rather than a
  `--coverage` flag on the Zotero probe. A probe answers "is the link up?"; a coverage
  measurement answers "is the content sufficient?" Those are different questions with
  different failure meanings, and invariant 4 wants one job per tool.
- **2026-08-19** — Pre-probe found all five hosts denied at CONNECT. Cause was the
  organization egress policy, not credentials or TLS. `/root/.ccr/README.md` instructs
  reporting such denials rather than retrying. Probes therefore treat `blocked` as a
  terminal, reportable state with its own exit code, never as a retryable error.
