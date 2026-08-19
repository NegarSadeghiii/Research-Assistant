#!/usr/bin/env python3
"""Tests for the screening report renderer (SOP-004 section 7).

The renderer's job is to show what the registry holds and nothing else. These tests
check the three things that would make it dishonest: hiding weak evidence, dropping
rejected papers, and letting a non-citable record read as support.

Verify: python3 execution/tests/test_render_screening_report.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_screening_report import (demo_records, esc, evidence_class,  # noqa: E402
                                     render, authors_display)

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'✅' if condition else '❌'} {name}{'' if condition else '  ' + detail}")
    if not condition:
        FAILURES.append(name)


records = demo_records()
page = render(records, "2026-08-19T00:00:00+00:00", "demo://anchor.docx")

print("\n  Screening report renderer\n")
print("  Structure")
check("renders a complete HTML document", page.startswith("<!doctype html>") and page.rstrip().endswith("</html>"))
check("declares UTF-8", 'charset="utf-8"' in page)
check("is self-contained — no external asset fetches",
      "http://" not in page.replace("http://www.w3.org", "") and "<script" not in page)
check("defines colours on bare :root, not only in a media query",
      page.index(":root{") < page.index("@media(prefers-color-scheme:dark)"))

print("\n  BR-20 — rejections are retained")
check("irrelevant papers appear in the report", "Irrelevant</h2>" in page or 'class="rec irrelevant"' in page)
check("the reason for an irrelevant verdict is shown",
      "different decision problem entirely" in page)
check("every record reaches the page",
      all(esc(r["bibliographic"]["title"]) in page for r in records),
      "a record was dropped")

print("\n  D-041 — evidence strength is visible per record")
check("a full-text record is labelled 'full text'", ">full text</span>" in page)
check("a metadata-only record is labelled 'metadata only'", ">metadata only</span>" in page)
check("body-text evidence chips are distinguishable from metadata chips",
      'class="chip body"' in page)
check("evidence_inspected values are rendered verbatim",
      ">introduction</span>" in page and ">abstract</span>" in page)

print("\n  §3.0 — candidate vs support")
check("an unverified identifier is marked candidate-only",
      "Candidate only — not citable as evidence." in page)
check("V5's reason is shown, not just the flag", "verified against its source" in page)
check("an unresolved conflict is surfaced with both values",
      "Sources disagree on" in page and "2021" in page and "2020" in page)
check("a conflicted record is not silently resolved", "Surfaced, not resolved." in page)

print("\n  Tallies agree with the page")
for verdict, label in [("relevant", "Relevant"), ("uncertain", "Uncertain"),
                       ("irrelevant", "Irrelevant"), ("unscreened", "Not screened")]:
    expected = sum(1 for r in records if r["screening"]["verdict"] == verdict)
    shown = re.search(rf'<span class="n">(\d+)</span><span class="l">{label}</span>', page)
    check(f"{label} tally reads {expected}", shown and int(shown.group(1)) == expected,
          f"page says {shown.group(1) if shown else 'nothing'}")

print("\n  Escaping — registry text is data, not markup")
evil = demo_records()[0]
evil["bibliographic"]["title"] = '<script>alert(1)</script>'
evil["screening"]["reason"] = 'a & b < c > d "quoted"'
out = render([evil], "2026-08-19T00:00:00+00:00")
check("a script tag in a title is escaped", "<script>alert" not in out and "&lt;script&gt;" in out)
check("ampersands and angle brackets in a reason are escaped", "a &amp; b &lt; c &gt; d" in out)

print("\n  Edge cases")
empty = render([], "2026-08-19T00:00:00+00:00")
check("an empty batch renders a report, not a blank page", "No papers screened in this batch" in empty)
check("an empty batch still emits valid HTML", empty.startswith("<!doctype html>"))

missing = demo_records()[0]
missing["bibliographic"]["venue"] = None
missing["bibliographic"]["year"] = None
out = render([missing], "2026-08-19T00:00:00+00:00")
check("missing optional fields render as em dash, never inferred", "—" in out)

check("no-evidence records are flagged rather than shown as adequate",
      evidence_class({"provenance": {"evidence_inspected": []}}) == ("none", "nothing inspected"))
check("a long author list is truncated visually", authors_display([f"A{i}" for i in range(9)])[0].endswith("more)"))
check("the full author list is preserved for the title attribute",
      authors_display([f"A{i}" for i in range(9)])[1].count(";") == 8)

unicode_rec = demo_records()[0]
unicode_rec["bibliographic"]["title"] = "Optimisation à la française — 日本語"
out = render([unicode_rec], "2026-08-19T00:00:00+00:00")
check("non-ASCII titles survive intact", "à la française" in out and "日本語" in out)

print()
if FAILURES:
    print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
    sys.exit(1)
print("  ✅ All renderer tests passed.\n")
