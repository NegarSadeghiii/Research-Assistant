#!/usr/bin/env python3
"""Tests for discovery and reconciliation (SOP-005 §8).

Offline: request construction and response normalisation are tested against fixtures,
so query shape and dedup logic are verified without a network call. The live behaviour
is verified by running the tool for real.

Verify: python3 execution/tests/test_discovery.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXEC = REPO_ROOT / "execution"
sys.path.insert(0, str(EXEC))

from discover_related import (crossref_search, from_crossref, from_openalex,  # noqa: E402
                              openalex_citations, openalex_search, pubmed_search)
from reconcile_candidates import key_for, merge_group  # noqa: E402

FAILURES: list[str] = []
TMP = Path(tempfile.mkdtemp())
ENV = {"OPENALEX_API_KEY": "KEY123", "NCBI_EMAIL": "a@b.c", "CROSSREF_MAILTO": "a@b.c"}


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'✅' if cond else '❌'} {name}{'' if cond else '  ' + detail}")
    if not cond:
        FAILURES.append(name)


print("\n  Request construction\n")

u = openalex_search("CAR-T scheduling", ENV, None, 25)
check("OpenAlex sends the key as a query parameter", "api_key=KEY123" in u)
check("OpenAlex search encodes the query", "search=CAR-T+scheduling" in u)
u = openalex_search("x", ENV, "2026-08-01", 25)
check("--since becomes an OpenAlex publication-date filter",
      "from_publication_date%3A2026-08-01" in u, u)

u = openalex_citations("10.1016/j.x", ENV, "forward", 25)
check("forward citation expansion filters on cites:", "cites%3Adoi%3A10.1016%2Fj.x" in u, u)
u = openalex_citations("https://doi.org/10.1016/j.x", ENV, "backward", 25)
check("a full DOI URL is normalised before use", "doi.org" not in u.split("filter=")[1], u)
check("backward expansion filters on cited_by:", "cited_by" in u, u)

u = pubmed_search("q", ENV, "2026-08-01", 10)
check("PubMed identifies the tool per NCBI policy", "tool=research-assistant" in u)
check("--since becomes a PubMed date range", "mindate=2026%2F08%2F01" in u and "datetype=pdat" in u, u)

u = crossref_search("q", ENV, "2026-08-01", 10)
check("Crossref joins the polite pool when a mailto is set", "mailto=a%40b.c" in u)
check("--since becomes a Crossref from-pub-date filter", "from-pub-date%3A2026-08-01" in u, u)

print("\n  Response normalisation\n")

oa = from_openalex({
    "display_name": "A paper", "publication_year": 2021, "cited_by_count": 7,
    "ids": {"doi": "https://doi.org/10.1000/x", "openalex": "https://openalex.org/W123",
            "pmid": "https://pubmed.ncbi.nlm.nih.gov/999"},
    "authorships": [{"author": {"display_name": "Lam, C."}}],
    "primary_location": {"source": {"display_name": "Cytotherapy"}},
}, "q", "search")
check("OpenAlex DOI is stripped to a bare DOI", oa["doi"] == "10.1000/x", oa["doi"])
check("OpenAlex work id is stripped to W-form", oa["openalex_id"] == "W123", str(oa["openalex_id"]))
check("PMID is extracted from its URL", oa["pmid"] == "999", str(oa["pmid"]))
check("venue is read from primary_location", oa["venue"] == "Cytotherapy")
check("provenance records which source found it", oa["found_via"] == "openalex")

cr = from_crossref({"title": ["B paper"], "DOI": "10.1000/y",
                    "issued": {"date-parts": [[2020, 5]]},
                    "container-title": ["J"], "is-referenced-by-count": 3,
                    "author": [{"given": "A", "family": "Smith"}]}, "q")
check("Crossref title unwraps its list", cr["title"] == "B paper")
check("Crossref year is read from date-parts", cr["year"] == 2020, str(cr["year"]))
check("Crossref author names are joined", cr["authors"] == ["A Smith"], str(cr["authors"]))

print("\n  Deduplication — DOI first (BR-14)\n")

check("DOI is the primary key", key_for({"doi": "10.1000/X"})[0] == "doi")
check("DOI matching is case- and prefix-insensitive",
      key_for({"doi": "https://doi.org/10.1000/x"}) == key_for({"doi": "10.1000/X"}))
check("title+year is the fallback when no DOI exists",
      key_for({"title": "A Paper!", "year": 2020})[0] == "title")
check("title matching ignores punctuation and case",
      key_for({"title": "A Paper!", "year": 2020}) == key_for({"title": "a paper", "year": 2020}))
check("different years are different works",
      key_for({"title": "A", "year": 2020}) != key_for({"title": "A", "year": 2021}))

print("\n  Merging — conflicts are surfaced, never resolved\n")

merged = merge_group([
    {"title": "Same paper", "year": 2021, "doi": "10.1/x", "found_via": "crossref",
     "found_by": "search", "query": "q1", "venue": "J", "authors": ["A"]},
    {"title": "Same paper", "year": 2020, "doi": "10.1/x", "found_via": "openalex",
     "found_by": "search", "query": "q2", "venue": "", "authors": []},
])
check("a year disagreement becomes an unresolved conflict",
      any(c["field"] == "year" and c["status"] == "unresolved" for c in merged["conflicts"]),
      str(merged["conflicts"]))
check("both disputed values are kept",
      set(merged["conflicts"][0]["values"].values()) == {2021, 2020},
      str(merged["conflicts"][0]["values"]))
check("the conflict names which source said what",
      set(merged["conflicts"][0]["values"].keys()) == {"crossref", "openalex"},
      str(merged["conflicts"][0]["values"].keys()))
check("every source that found the work is recorded",
      merged["found_via"] == ["crossref", "openalex"], str(merged["found_via"]))
check("every query that found it is recorded",
      merged["queries"] == ["q1", "q2"], str(merged["queries"]))
check("a missing field is filled from the other hit", merged["authors"] == ["A"])

agree = merge_group([
    {"title": "T", "year": 2021, "doi": "10.1/x", "found_via": "crossref"},
    {"title": "T", "year": 2021, "doi": "10.1/x", "found_via": "openalex"},
])
check("agreeing sources produce no conflict", agree["conflicts"] == [], str(agree["conflicts"]))

print("\n  Guardrails\n")

proc = subprocess.run([sys.executable, str(EXEC / "discover_related.py"),
                       "--query", "one only", "--dry-run"], capture_output=True, text=True)
out = json.loads(proc.stdout.strip().splitlines()[-1])
check("a single query formulation triggers a warning",
      any("one query formulation" in w.lower() or "single vocabulary" in w.lower()
          for w in out["evidence"]["warnings"]), str(out["evidence"].get("warnings")))
check("dry-run issues no requests", out["evidence"]["dry_run"] is True)
check("dry-run redacts the API key",
      all("KEY" not in r["url"] and "api_key=…" in r["url"] or "api_key" not in r["url"]
          for r in out["evidence"]["requests"]),
      str(out["evidence"]["requests"]))

proc = subprocess.run([sys.executable, str(EXEC / "discover_related.py"),
                       "--query", "a", "--query", "b", "--dry-run"],
                      capture_output=True, text=True)
out = json.loads(proc.stdout.strip().splitlines()[-1])
check("two formulations produce no warning", out["evidence"]["warnings"] == [])
check("each query hits every configured source", len(out["evidence"]["requests"]) == 6,
      str(len(out["evidence"]["requests"])))

proc = subprocess.run([sys.executable, str(EXEC / "discover_related.py"),
                       "--seed-doi", "10.1/x", "--dry-run"], capture_output=True, text=True)
out = json.loads(proc.stdout.strip().splitlines()[-1])
check("a seed DOI plans both citation directions",
      len(out["evidence"]["requests"]) == 2
      and {r["how"].split(":")[0] for r in out["evidence"]["requests"]} == {"cites", "referenced_by"},
      str([r["how"] for r in out["evidence"]["requests"]]))

proc = subprocess.run([sys.executable, str(EXEC / "discover_related.py")],
                      capture_output=True, text=True)
check("no query and no seed is refused", proc.returncode != 0, str(proc.returncode))

print("\n  Classification against library and registry\n")

cands = TMP / "c.json"
cands.write_text(json.dumps({"candidates": [
    {"title": "In the library", "year": 2020, "doi": "10.1/lib", "found_via": "openalex"},
    {"title": "Brand new", "year": 2024, "doi": "10.1/new", "found_via": "openalex"},
    {"title": "Already screened", "year": 2022, "doi": "10.1/seen", "found_via": "crossref"},
], "sources_searched": ["openalex:search"], "sources_not_searched": []}))
corpus = TMP / "corpus.json"
corpus.write_text(json.dumps({"papers": [
    {"zotero_key": "K1", "title": "In the library", "year": "2020", "doi": "10.1/lib"}]}))
registry = TMP / "reg.json"
registry.write_text(json.dumps({"records": [
    {"identifiers": {"doi": "10.1/seen"},
     "bibliographic": {"title": "Already screened", "year": 2022},
     "screening": {"verdict": "irrelevant", "anchor_document": "anchor.docx"}}]}))

recon = TMP / "out.json"
subprocess.run([sys.executable, str(EXEC / "reconcile_candidates.py"),
                "--candidates", str(cands), "--corpus", str(corpus),
                "--registry", str(registry), "--anchor", "anchor.docx",
                "--out", str(recon)], capture_output=True, text=True)
res = json.loads(recon.read_text())
check("a library paper is classified in_library", res["counts"]["in_library"] == 1)
check("a previously screened paper is classified already_screened",
      res["counts"]["already_screened"] == 1)
check("its prior verdict is carried through, not recomputed",
      res["already_screened"][0]["prior_verdict"] == "irrelevant")
check("an unseen paper is classified new", res["counts"]["new"] == 1)
check("new candidates are STAGED, never auto-imported (BR-13)",
      res["new"][0]["staging_state"] == "staged")
check("coverage is carried through for the positioning brief",
      res["sources_searched"] == ["openalex:search"])

subprocess.run([sys.executable, str(EXEC / "reconcile_candidates.py"),
                "--candidates", str(cands), "--corpus", str(corpus),
                "--registry", str(registry), "--anchor", "DIFFERENT.docx",
                "--out", str(recon)], capture_output=True, text=True)
res2 = json.loads(recon.read_text())
check("a verdict against a DIFFERENT anchor does not settle this one",
      res2["counts"]["new"] == 2 and res2["counts"]["already_screened"] == 0,
      str(res2["counts"]))

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All discovery tests passed.\n")
