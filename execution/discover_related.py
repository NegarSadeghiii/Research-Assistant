#!/usr/bin/env python3
"""Find candidate papers outside the library. See SOP-005.

⛔ This tool emits CANDIDATES, never verdicts. A keyword match makes a paper worth
looking at; it is not evidence of relevance. Every candidate is screened against the
anchor document afterwards (SOP-003) exactly like a library paper. Scoring candidates
by query-match strength would be F5 with an API in front of it.

⛔ It does not assess novelty. Finding nothing is not evidence of a gap (BR-3, P3, F6).

Verify:
    python3 execution/tests/test_discovery.py
    python3 execution/discover_related.py --query "CAR-T supply chain scheduling" --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "execution" / "probes"))
from _common import GREEN, RED, classify_error, emit, get_json, load_env  # noqa: E402

TOOL = "discover_related"
PER_SOURCE = 25


# ───────────────────────── request construction ─────────────────────────
# Built separately from execution so --dry-run can show exactly what would be sent.

def openalex_search(query: str, env: dict, since: str | None, per_page: int) -> str:
    params = {"search": query, "per-page": per_page, "api_key": env.get("OPENALEX_API_KEY", "")}
    if since:
        params["filter"] = f"from_publication_date:{since}"
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(params)


def openalex_citations(doi: str, env: dict, direction: str, per_page: int) -> str:
    """Citation-graph expansion — the mechanism that is vocabulary-independent."""
    key = env.get("OPENALEX_API_KEY", "")
    clean = doi.replace("https://doi.org/", "")
    if direction == "forward":
        return ("https://api.openalex.org/works?"
                + urllib.parse.urlencode({"filter": f"cites:doi:{clean}",
                                          "per-page": per_page, "api_key": key}))
    return ("https://api.openalex.org/works?"
            + urllib.parse.urlencode({"filter": f"cited_by:doi:{clean}",
                                      "per-page": per_page, "api_key": key}))


def pubmed_search(query: str, env: dict, since: str | None, retmax: int) -> str:
    params = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json",
              "tool": env.get("NCBI_TOOL_NAME", "research-assistant")}
    if env.get("NCBI_EMAIL"):
        params["email"] = env["NCBI_EMAIL"]
    if env.get("NCBI_API_KEY"):
        params["api_key"] = env["NCBI_API_KEY"]
    if since:
        params["mindate"] = since.replace("-", "/")
        params["maxdate"] = "3000/01/01"
        params["datetype"] = "pdat"
    return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params)


def crossref_search(query: str, env: dict, since: str | None, rows: int) -> str:
    params = {"query.bibliographic": query, "rows": rows}
    if env.get("CROSSREF_MAILTO"):
        params["mailto"] = env["CROSSREF_MAILTO"]
    if since:
        params["filter"] = f"from-pub-date:{since}"
    return "https://api.crossref.org/works?" + urllib.parse.urlencode(params)


# ───────────────────────── response normalisation ─────────────────────────

def from_openalex(work: dict, query: str, how: str) -> dict:
    ids = work.get("ids") or {}
    doi = (ids.get("doi") or "").replace("https://doi.org/", "") or None
    authorships = work.get("authorships") or []
    return {
        "title": work.get("display_name") or "",
        "authors": [(a.get("author") or {}).get("display_name", "") for a in authorships][:12],
        "year": work.get("publication_year"),
        "venue": ((work.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
        "doi": doi,
        "openalex_id": (ids.get("openalex") or "").rsplit("/", 1)[-1] or None,
        "pmid": (ids.get("pmid") or "").rsplit("/", 1)[-1] or None,
        "abstract": "",
        "cited_by_count": work.get("cited_by_count"),
        "found_via": "openalex", "found_by": how, "query": query,
    }


def from_crossref(item: dict, query: str) -> dict:
    return {
        "title": (item.get("title") or [""])[0],
        "authors": [" ".join(filter(None, [a.get("given"), a.get("family")]))
                    for a in (item.get("author") or [])][:12],
        "year": ((item.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        "venue": (item.get("container-title") or [""])[0],
        "doi": item.get("DOI"), "openalex_id": None, "pmid": None,
        "abstract": item.get("abstract") or "",
        "cited_by_count": item.get("is-referenced-by-count"),
        "found_via": "crossref", "found_by": "search", "query": query,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", action="append", default=[],
                    help="a query formulation; repeat for different vocabularies")
    ap.add_argument("--seed-doi", action="append", default=[],
                    help="expand the citation graph around this DOI (both directions)")
    ap.add_argument("--since", default=None, help="YYYY-MM-DD, for monitoring runs")
    ap.add_argument("--out", default=str(REPO_ROOT / ".tmp" / "candidates.json"))
    ap.add_argument("--per-source", type=int, default=PER_SOURCE)
    ap.add_argument("--sources", default="openalex,pubmed,crossref")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the requests that would be issued, without issuing them")
    args = ap.parse_args()

    if not args.query and not args.seed_doi:
        return emit(TOOL, RED, "Nothing to search. Give --query and/or --seed-doi.", {})

    env = load_env()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    warnings = []
    # One vocabulary is not a search (SOP-005 section 3).
    if len(args.query) == 1 and not args.seed_doi:
        warnings.append(
            "Only one query formulation supplied. A single vocabulary returns a single "
            "vocabulary's literature; work using different terminology for the same idea "
            "will be missed. Add more --query formulations, or --seed-doi for "
            "citation-graph expansion, which is vocabulary-independent.")

    planned: list[tuple[str, str, str]] = []   # (source, how, url)
    for q in args.query:
        if "openalex" in sources:
            planned.append(("openalex", "search", openalex_search(q, env, args.since, args.per_source)))
        if "pubmed" in sources:
            planned.append(("pubmed", "search", pubmed_search(q, env, args.since, args.per_source)))
        if "crossref" in sources:
            planned.append(("crossref", "search", crossref_search(q, env, args.since, args.per_source)))
    for doi in args.seed_doi:
        if "openalex" in sources:
            planned.append(("openalex", f"cites:{doi}",
                            openalex_citations(doi, env, "forward", args.per_source)))
            planned.append(("openalex", f"referenced_by:{doi}",
                            openalex_citations(doi, env, "backward", args.per_source)))

    if args.dry_run:
        redacted = [(s, h, u.split("api_key=")[0] + ("api_key=…" if "api_key=" in u else ""))
                    for s, h, u in planned]
        return emit(TOOL, GREEN, f"{len(planned)} request(s) planned; none issued.",
                    {"dry_run": True, "requests": [{"source": s, "how": h, "url": u}
                                                   for s, h, u in redacted],
                     "warnings": warnings})

    candidates: list[dict] = []
    searched, not_searched = [], []

    for source, how, url in planned:
        try:
            _, body, _ = get_json(url, timeout=40)
        except BaseException as exc:  # noqa: BLE001
            code, detail, _ = classify_error(exc)
            # A source that failed is recorded as NOT searched, never silently dropped —
            # the coverage statement in a positioning brief is built from this.
            entry = f"{source} ({how}): {detail}"
            if entry not in not_searched:
                not_searched.append(entry)
            continue

        label = f"{source}:{how}"
        if label not in searched:
            searched.append(label)

        if source == "openalex":
            for w in (body or {}).get("results", []):
                candidates.append(from_openalex(w, how if how.startswith("cites") else url, how))
        elif source == "crossref":
            for it in ((body or {}).get("message") or {}).get("items", []):
                candidates.append(from_crossref(it, how))
        elif source == "pubmed":
            ids = ((body or {}).get("esearchresult") or {}).get("idlist", [])
            for pmid in ids:
                candidates.append({
                    "title": "", "authors": [], "year": None, "venue": "", "doi": None,
                    "openalex_id": None, "pmid": pmid, "abstract": "",
                    "cited_by_count": None, "found_via": "pubmed",
                    "found_by": "search", "query": how,
                    "needs_metadata_fetch": True})
        time.sleep(0.15)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema_version": "1.0.0",
        "searched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "queries": args.query, "seed_dois": args.seed_doi, "since": args.since,
        "sources_searched": searched, "sources_not_searched": not_searched,
        "candidates": candidates}, indent=1))

    detail = f"{len(candidates)} candidate(s) from {len(searched)} source-query pair(s)."
    if not candidates:
        detail += (" Zero results is a real finding — reported as such, not widened "
                   "silently to produce hits (SOP-005 section 6).")
    if not_searched:
        detail += f" ⚠ {len(not_searched)} source(s) failed and are recorded as NOT searched."

    return emit(TOOL, GREEN if not not_searched else RED, detail,
                {"path": str(out), "candidates": len(candidates),
                 "sources_searched": searched, "sources_not_searched": not_searched,
                 "warnings": warnings})


if __name__ == "__main__":
    sys.exit(main())
