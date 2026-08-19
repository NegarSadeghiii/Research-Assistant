#!/usr/bin/env python3
"""Verify the probe exit-code classifier (SOP-000 section 2, SOP-001 section 3).

The classifier's whole job is telling a network policy denial apart from a rejected
credential. Both look like "403". Sending the user to regenerate a working key
because the proxy blocked the request is the specific mistake this suite prevents.

Verify: python3 execution/tests/test_probe_classification.py
"""
from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
from _common import BLOCKED, MISSING, RED, classify_error, require  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'✅' if condition else '❌'} {name}{'' if condition else '  ' + detail}")
    if not condition:
        FAILURES.append(name)


def http_error(status: int, body: bytes = b"") -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.test", status, "err", {}, io.BytesIO(body))


print("\n  Probe exit-code classification\n")

code, _, _ = classify_error(urllib.error.URLError("CONNECT tunnel failed, response 403"))
check("proxy 403 on CONNECT -> BLOCKED (exit 2)", code == BLOCKED, f"got {code}")

code, _, _ = classify_error(urllib.error.URLError("CONNECT tunnel failed, response 407"))
check("proxy 407 on CONNECT -> BLOCKED (exit 2)", code == BLOCKED, f"got {code}")

code, detail, _ = classify_error(http_error(403, b"Invalid key"))
check("service HTTP 403 -> RED (exit 1), not BLOCKED", code == RED, f"got {code}")
check("  ...and blames the credential, not the network", "credential" in detail.lower(), detail)

code, _, _ = classify_error(http_error(401))
check("service HTTP 401 -> RED (exit 1)", code == RED, f"got {code}")

code, _, evidence = classify_error(http_error(429))
check("HTTP 429 -> RED, never green", code == RED, f"got {code}")
check("  ...and records retry_after as evidence", "retry_after" in evidence, str(evidence))

code, _, _ = classify_error(urllib.error.URLError("timed out"))
check("bare timeout -> RED, does not masquerade as BLOCKED", code == RED, f"got {code}")

code, _, _ = classify_error(http_error(500))
check("HTTP 500 -> RED (exit 1)", code == RED, f"got {code}")

missing = require({"ZOTERO_USER_ID": "x", "ZOTERO_API_KEY": ""},
                  "ZOTERO_USER_ID", "ZOTERO_API_KEY")
check("require() names only the absent key", missing == ["ZOTERO_API_KEY"], str(missing))

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All classification tests passed.\n")
