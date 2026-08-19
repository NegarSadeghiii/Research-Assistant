# SOP-000 — Shared conventions for `/execution/`

**Status:** active · **Owner:** Layer T · **Created:** 2026-08-19

Every script in `/execution/` obeys this document. A change here is a change to every
tool, so it is amended before any tool departs from it (invariant 3).

## 1. Goal

Make Layer T deterministic and individually testable, so Navigation can call tools in
any order and interpret results without reading their source.

## 2. Exit codes — the machine contract

| Code | Meaning | Navigation should |
|---|---|---|
| `0` | **GREEN** — the operation succeeded and the result is trustworthy | proceed |
| `1` | **RED** — reached the service, but it refused or returned something invalid (bad credential, 4xx/5xx, malformed payload) | halt; the credential or request is wrong |
| `2` | **BLOCKED** — never reached the service; the egress proxy denied the CONNECT | halt; report the blocked host (BR-8). **Do not retry, do not route around.** |
| `3` | **MISSING INPUT** — a required credential or argument is absent | halt; ask the user |
| `4` | **INVALID DATA** — input parsed but violated the schema in CLAUDE.md §1 | halt; the record is rejected, not written |

> Codes `1` and `2` are deliberately distinct. "Blocked" and "wrong key" look
> identical in a naive probe, and conflating them wasted real diagnostic effort
> during the Phase L pre-probe. A tool that cannot tell them apart is not finished.

## 3. Output contract

- **stdout** — exactly one line of JSON. Machine-readable, parseable by Navigation.
- **stderr** — human-readable narration. Never parsed.

Every stdout payload carries at minimum:

```json
{"tool": "probe_zotero", "status": "green|red|blocked|missing|invalid",
 "detail": "one sentence", "evidence": {}, "checked_at": "ISO-8601"}
```

`evidence` holds what was actually observed — HTTP status, counts, error strings.
Claims without evidence violate invariant 11.

## 4. Credentials

- Read from `.env` only, via `_common.load_env()`. Never hardcoded, never logged.
- `load_env()` strips a matching pair of surrounding quotes. `.env` convention permits
  them, and a quoted credential is silently the wrong credential otherwise.
- ⚠ **Before concluding a credential is invalid, check the loaded length.** A service
  rejecting a key proves the bytes sent were wrong, not that the key on file is wrong.
- A tool that needs a missing key exits `3` and **names the key**, never the value.
- No credential value is ever written to stdout, stderr, `/state/`, or `/.tmp/`.

## 5. Network

- Always honour `HTTPS_PROXY` and `SSL_CERT_FILE` from the environment. The proxy port
  **changes between sessions** — never hardcode it.
- Never disable TLS verification. Never unset `HTTPS_PROXY`.
- A `403` on CONNECT is an organization policy denial: exit `2` and report the host.

## 6. Files

- Intermediates go to `/.tmp/` and are gitignored (invariant 6).
- `/state/` writes are atomic: write to a temp file, then `os.replace()`. A crash
  mid-write must never leave a truncated registry.
- Payloads go only to the four directories in CLAUDE.md §2.9 (BR-17).

## 7. Verification

Every tool ships with a one-line verify command in its own SOP (invariant 8).
A tool with no verify command is not shippable.
