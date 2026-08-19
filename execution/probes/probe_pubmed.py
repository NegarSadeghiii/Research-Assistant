#!/usr/bin/env python3
"""Probe: PubMed via NCBI E-utilities. Key optional; raises 3/s to 10/s.

Verify: python3 execution/probes/probe_pubmed.py
"""
from __future__ import annotations

import sys
import urllib.parse

from _common import GREEN, classify_error, emit, get_json, load_env

TOOL = "probe_pubmed"


def main() -> int:
    env = load_env()
    params = {"db": "pubmed", "term": "CAR-T cell therapy supply chain",
              "retmax": "1", "retmode": "json",
              "tool": env.get("NCBI_TOOL_NAME", "research-assistant")}
    if env.get("NCBI_EMAIL"):
        params["email"] = env["NCBI_EMAIL"]
    if env.get("NCBI_API_KEY"):
        params["api_key"] = env["NCBI_API_KEY"]

    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
           + urllib.parse.urlencode(params))
    try:
        status, body, _ = get_json(url)
    except BaseException as exc:  # noqa: BLE001
        code, detail, evidence = classify_error(exc)
        evidence["host"] = "eutils.ncbi.nlm.nih.gov"
        return emit(TOOL, code, detail, evidence)

    count = (body or {}).get("esearchresult", {}).get("count")
    return emit(TOOL, GREEN, f"PubMed E-utilities reachable; query matched {count} records.",
                {"http_status": status, "count": count,
                 "authenticated": bool(env.get("NCBI_API_KEY"))})


if __name__ == "__main__":
    sys.exit(main())
