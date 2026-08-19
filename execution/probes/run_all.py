#!/usr/bin/env python3
"""Run every Phase L probe and report a status table.

Exit 0 only if every REQUIRED probe is green — this is the G1 gate condition.

Verify: python3 execution/probes/run_all.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

# (script, required for G1?) — Semantic Scholar and PubMed are required by the Q2
# discovery stack; Consensus and WebSearch are MCP/tool paths, probed separately.
PROBES = [
    ("probe_zotero.py", True),
    ("probe_openalex.py", True),
    ("probe_semantic_scholar.py", True),
    ("probe_pubmed.py", True),
    ("probe_crossref.py", True),
]


def run(script: str) -> dict:
    proc = subprocess.run([sys.executable, str(HERE / script)],
                          capture_output=True, text=True, timeout=120)
    line = (proc.stdout or "").strip().splitlines()
    try:
        payload = json.loads(line[-1]) if line else {}
    except json.JSONDecodeError:
        payload = {}
    payload.setdefault("tool", script.removesuffix(".py"))
    payload.setdefault("status", "red")
    payload.setdefault("detail", (proc.stderr or "no output").strip()[:200])
    payload["exit_code"] = proc.returncode
    return payload


def main() -> int:
    results = [dict(run(script), required=required) for script, required in PROBES]

    width = max(len(r["tool"]) for r in results)
    print(f"\n  Phase L — connection probes   {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}\n")
    for r in results:
        mark = {"green": "✅", "red": "❌", "blocked": "⛔",
                "missing": "🔑", "invalid": "⚠️"}.get(r["status"], "?")
        req = "" if r["required"] else "  (optional)"
        print(f"  {mark} {r['tool']:<{width}}  {r['status']:<8} {r['detail']}{req}")

    out = REPO_ROOT / ".tmp" / "probe-results.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\n  Evidence written to {out.relative_to(REPO_ROOT)}")

    blocked = [r for r in results if r["status"] == "blocked"]
    failed = [r for r in results if r["required"] and r["status"] != "green"]

    if blocked:
        hosts = sorted({r.get("evidence", {}).get("host", "?") for r in blocked})
        print("\n  ⛔ EGRESS POLICY BLOCK — these hosts are denied by the organization")
        print("     network policy for this session. Reporting, not retrying (BR-8):")
        for h in hosts:
            print(f"       - {h}")
        print("     Fix: widen the environment's egress policy (CLAUDE.md 2.7 P1),")
        print("     then start a NEW session — policy binds at session start.")

    if failed:
        print(f"\n  G1 NOT PASSED — {len(failed)} of {sum(1 for _, r in PROBES if r)} "
              f"required probes are not green.\n")
        return 1

    print("\n  ✅ G1 CONDITION MET — every required probe is green.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
