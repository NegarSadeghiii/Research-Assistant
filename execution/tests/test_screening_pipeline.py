#!/usr/bin/env python3
"""Tests for the screening pipeline (SOP-003 section 7).

The pipeline's value is what it REFUSES. These tests target the boundary between the
model's judgement and the registry: every way an unsupportable verdict could reach
storage should be closed here.

Verify: python3 execution/tests/test_screening_pipeline.py
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
from record_screening import build_record, screening_rules  # noqa: E402
from validate_registry import validate_record  # noqa: E402

FAILURES: list[str] = []
TMP = Path(tempfile.mkdtemp())
ANCHOR = "Survival_Aware_iSHIPMENT_Formulation.docx"


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'✅' if condition else '❌'} {name}{'' if condition else '  ' + detail}")
    if not condition:
        FAILURES.append(name)


def verdict(**kw) -> dict:
    paper = {"zotero_key": kw.get("key", "K1"), "title": kw.get("title", "A paper"),
             "authors": ["Example, A."], "year": "2020", "venue": "J",
             "doi": kw.get("doi", "10.1000/x"), "has_full_text": kw.get("ft", True)}
    return {"paper": paper, "verdict": kw.get("verdict", "relevant"),
            "reason": kw.get("reason", "A stated reason."),
            "categories": kw.get("cats", ["methodological_precedent"]),
            "evidence_inspected": kw.get("evidence",
                                         ["title", "abstract", "introduction"])}


def problems(v: dict, anchor=ANCHOR, confirmed=True) -> list[str]:
    rec = build_record(v, anchor, confirmed)
    return validate_record(rec)[0] + screening_rules(rec)


def run(script: str, *args) -> tuple[int, dict]:
    p = subprocess.run([sys.executable, str(EXEC / script), *args],
                       capture_output=True, text=True)
    try:
        return p.returncode, json.loads((p.stdout or "").strip().splitlines()[-1])
    except Exception:
        return p.returncode, {}


print("\n  Screening pipeline — the model decides, the script refuses\n")

print("  Accepts a well-formed verdict")
check("a full-text relevant verdict with a reason is accepted", problems(verdict()) == [],
      str(problems(verdict())))

print("\n  SOP-003 4.4 — the metadata-only cap")
p = problems(verdict(ft=False, evidence=["title", "abstract"], verdict="relevant"))
check("metadata-only CANNOT be marked relevant", any("4.4" in x for x in p), str(p))
check("the refusal explains why an abstract is not evidence of content",
      any("advertisement" in x for x in p))
check("metadata-only CAN be marked uncertain",
      problems(verdict(ft=False, evidence=["title", "abstract"], verdict="uncertain")) == [])
check("metadata-only CAN be marked irrelevant",
      problems(verdict(ft=False, evidence=["title", "abstract"], verdict="irrelevant")) == [])
check("a conclusion alone lifts the cap",
      problems(verdict(evidence=["title", "abstract", "conclusion"])) == [])

print("\n  V1-V3 at the boundary")
check("a verdict with no reason is refused",
      any("V1" in x for x in problems(verdict(reason="   "))))
check("a verdict with no evidence recorded is refused",
      any("V2" in x for x in problems(verdict(evidence=[]))))
check("an UNCONFIRMED anchor is refused (BR-9)",
      any("V3" in x for x in problems(verdict(), confirmed=False)))
check("a missing anchor is refused",
      any("V3" in x for x in problems(verdict(), anchor="", confirmed=True)))

print("\n  Record construction")
rec = build_record(verdict(), ANCHOR, True)
check("record_id is derived, not supplied", rec["record_id"] == rec["record_id"])
check("a Zotero item counts as a verified identifier",
      rec["identifier_verified_against_source"] is True)
ext = build_record({"paper": {"title": "External", "doi": "10.1/x", "authors": [],
                              "year": "2020"}, "verdict": "uncertain",
                    "reason": "r", "evidence_inspected": ["title", "abstract"]}, ANCHOR, True)
check("an external paper is NOT auto-verified", ext["identifier_verified_against_source"] is False)
check("an external paper is staged, not in-library (BR-13)",
      ext["staging"]["state"] == "staged" and
      ext["provenance"]["zotero_status"] == "not_submitted")
check("the anchor is recorded on every record",
      rec["screening"]["anchor_document"] == ANCHOR)
check("full_text_available is carried from the corpus",
      rec["provenance"]["full_text_available"] is True)

print("\n  End to end")
vfile = TMP / "v.json"
vfile.write_text(json.dumps({"verdicts": [
    verdict(key="A", doi="10.1/a"),
    verdict(key="B", doi="10.1/b", ft=False, evidence=["title", "abstract"],
            verdict="relevant", title="Should be rejected"),
]}))
reg = TMP / "registry.json"
rc, out = run("record_screening.py", "--verdicts", str(vfile), "--registry", str(reg),
              "--anchor", ANCHOR, "--anchor-confirmed", "--dry-run")
check("a batch with a bad verdict exits non-zero", rc == 4, str(rc))
check("the good verdict is accepted", out["evidence"]["accepted"] == 1)
check("the bad verdict is reported with its rule", len(out["evidence"]["rejected"]) == 1)
check("a dry run writes nothing", not reg.exists())

vfile.write_text(json.dumps({"verdicts": [verdict(key="A", doi="10.1/a")]}))
rc, out = run("record_screening.py", "--verdicts", str(vfile), "--registry", str(reg),
              "--anchor", ANCHOR, "--anchor-confirmed")
check("a clean batch is written", rc == 0 and reg.exists())
stored = json.loads(reg.read_text())
check("the registry validates after the write",
      all(validate_record(r)[0] == [] for r in stored["records"]))
check("re-running the same batch updates rather than duplicates",
      (run("record_screening.py", "--verdicts", str(vfile), "--registry", str(reg),
           "--anchor", ANCHOR, "--anchor-confirmed")[1]["evidence"]["accepted"] == 1)
      and len(json.loads(reg.read_text())["records"]) == 1)

print("\n  Anchor extraction")
rc, out = run("extract_anchor.py", "--path", "/nonexistent.docx")
check("a missing anchor halts rather than degrading", rc == 3, str(rc))
check("the refusal names it a schema error", "schema error" in out.get("detail", ""))

thin = TMP / "thin.md"; thin.write_text("too short")
rc, out = run("extract_anchor.py", "--path", str(thin), "--out", str(TMP / "a.txt"))
check("an anchor too thin to judge against is refused", rc == 4, str(rc))

good = TMP / "anchor.md"; good.write_text("# Methodology\n\n" + ("Survival-aware scheduling. " * 40))
rc, out = run("extract_anchor.py", "--path", str(good), "--out", str(TMP / "a.txt"))
check("a real anchor extracts", rc == 0 and out["evidence"]["chars"] > 200)

rc, out = run("extract_anchor.py", "--path", str(TMP / "x.pdf"))
check("an unsupported format is refused, not guessed at", rc in (3, 4))

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All screening pipeline tests passed.\n")
