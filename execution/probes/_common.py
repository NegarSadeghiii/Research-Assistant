"""Shared helpers for Phase L probes. See /architecture/SOP-000-conventions.md."""
from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Exit codes — SOP-000 section 2.
GREEN, RED, BLOCKED, MISSING, INVALID = 0, 1, 2, 3, 4
_STATUS = {GREEN: "green", RED: "red", BLOCKED: "blocked",
           MISSING: "missing", INVALID: "invalid"}


def load_env(path: Path | None = None) -> dict[str, str]:
    """Parse .env into a dict. Values are never logged (SOP-000 section 4)."""
    env_path = path or REPO_ROOT / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        # .env convention allows quoted values. Without this, a perfectly valid
        # KEY="abc" yields the 24-character string '"abc"' and the service rejects
        # it as a wrong credential - which reads as "your key is bad", not "your
        # file is quoted". Cost a debugging round on 2026-08-19.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def require(env: dict[str, str], *keys: str) -> list[str]:
    """Return the names — never the values — of required keys that are absent."""
    return [k for k in keys if not env.get(k)]


def classify_error(exc: BaseException) -> tuple[int, str, dict]:
    """Separate an egress-policy denial from a service-level rejection.

    This distinction is the whole point of the probe: a proxy 403 on CONNECT and an
    API rejecting our key both read as "403" to a naive implementation, but they send
    the user to completely different remedies. See SOP-001 section 3.
    """
    if isinstance(exc, urllib.error.HTTPError):
        # A real HTTP response: the request reached the service.
        body = ""
        try:
            body = exc.read(300).decode("utf-8", "replace")
        except Exception:
            pass
        evidence = {"http_status": exc.code, "body_head": body}
        if exc.code in (401, 403):
            return RED, f"Service rejected the request (HTTP {exc.code}) — credential or scope problem.", evidence
        if exc.code == 429:
            retry = exc.headers.get("Retry-After") if exc.headers else None
            evidence["retry_after"] = retry
            return RED, "Rate limited (HTTP 429) — reachable but not usable right now.", evidence
        return RED, f"Service returned HTTP {exc.code}.", evidence

    if isinstance(exc, urllib.error.URLError):
        reason = str(getattr(exc, "reason", exc))
        # Proxy denials surface as a failed CONNECT tunnel, not an HTTP response.
        if "403" in reason or "407" in reason or "tunnel" in reason.lower():
            return BLOCKED, ("Egress proxy denied CONNECT — host not allowed by the "
                             "organization network policy. Report it; do not retry (BR-8)."), {"reason": reason}
        return RED, f"Transport failure: {reason}", {"reason": reason}

    return RED, f"Unexpected error: {exc!r}", {"reason": repr(exc)}


def get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 25):
    """One GET through the environment proxy, honouring SSL_CERT_FILE.

    urllib reads HTTPS_PROXY from the environment on its own, so the proxy port is
    never hardcoded — it changes between sessions (SOP-000 section 5).
    """
    request = urllib.request.Request(url, headers=headers or {})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        raw = response.read()
        parsed = json.loads(raw) if raw else None
        return response.status, parsed, dict(response.headers)


def emit(tool: str, code: int, detail: str, evidence: dict | None = None) -> int:
    """Write the SOP-000 output contract: JSON on stdout, narration on stderr."""
    payload = {
        "tool": tool,
        "status": _STATUS[code],
        "detail": detail,
        "evidence": evidence or {},
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    print(json.dumps(payload), flush=True)
    mark = {"green": "OK", "red": "FAIL", "blocked": "BLOCKED",
            "missing": "MISSING", "invalid": "INVALID"}[payload["status"]]
    print(f"[{mark}] {tool}: {detail}", file=sys.stderr)
    return code
