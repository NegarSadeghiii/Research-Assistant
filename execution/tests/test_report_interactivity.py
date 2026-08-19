#!/usr/bin/env python3
"""Browser tests for the screening report's view controls (SOP-004 section 6.1).

Markup assertions prove the controls are present. These prove they WORK, and — more
importantly — that they never remove a record from the file. A filter that silently
dropped papers from an archived report would be BR-20's failure with a nicer interface.

Verify: python3 execution/tests/test_report_interactivity.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'✅' if condition else '❌'} {name}{'' if condition else '  ' + detail}")
    if not condition:
        FAILURES.append(name)


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⏭  playwright not installed — skipping browser tests")
        return 0

    # Use the browser the image already ships. The pip package's pinned build may not
    # match what is installed, and re-downloading is both unnecessary and blocked in
    # sandboxed environments.
    chrome = None
    for candidate in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")):
        chrome = str(candidate)
    if chrome is None and not Path("/opt/pw-browsers").exists():
        print("  ⏭  no chromium available — skipping browser tests")
        return 0

    out = Path(tempfile.mkdtemp()) / "report.html"
    subprocess.run([sys.executable, str(REPO_ROOT / "execution" / "render_screening_report.py"),
                    "--demo", "--out", str(out)], check=True, capture_output=True)

    print("\n  Screening report — view controls (headless Chromium)\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
        page = browser.new_page()
        page.goto(out.as_uri())

        total = page.locator(".rec").count()
        vis = lambda: page.locator(".rec:not([hidden])").count()

        def toggle(kind: str, value: str) -> None:
            """Click the label, as a person would — the input is visually hidden."""
            page.click(f'label.tog:has(input[data-f="{kind}"][value="{value}"])')

        print("  Baseline")
        check("all records present in the DOM", total == 6, f"found {total}")
        check("all records visible before filtering", vis() == 6, f"visible {vis()}")
        check("counter shows the total", "6 records" in page.locator("#showing").inner_text())

        print("\n  Filtering hides, never removes")
        toggle("verdict", "irrelevant")
        after = vis()
        check("unchecking a verdict hides its records", after == 5, f"visible {after}")
        check("hidden records remain in the DOM", page.locator(".rec").count() == 6,
              "a record was removed from the file")
        check("counter announces the filtered view",
              "showing 5 of 6" in page.locator("#showing").inner_text(),
              page.locator("#showing").inner_text())
        check("counter is styled as filtered",
              "filtered" in (page.locator("#showing").get_attribute("class") or ""))
        check("print note warns that the screen was filtered",
              "filter was active" in page.locator("#printNote").inner_text())

        toggle("verdict", "irrelevant")
        check("re-checking restores every record", vis() == 6, f"visible {vis()}")
        check("print note clears when unfiltered", page.locator("#printNote").inner_text() == "")

        print("\n  Evidence and citability filters")
        n_meta = page.locator('.rec[data-evidence="meta"]').count()
        toggle("evidence", "meta")
        check(f"filtering out the {n_meta} metadata-only record(s) works",
              vis() == total - n_meta, f"visible {vis()}, expected {total - n_meta}")
        toggle("evidence", "meta")

        toggle("citable", "no")
        n_citable = vis()
        check("filtering to citable-only excludes candidates", n_citable < 6, f"visible {n_citable}")
        toggle("citable", "no")

        print("\n  Search")
        page.fill("#q", "novelty")
        check("search finds a term shown only as a category chip", 0 < vis() < 6,
              f"visible {vis()} — categories may be missing from the search index")
        page.fill("#q", "consensus")
        check("search finds a term from the provenance block", 0 < vis() < 6, f"visible {vis()}")
        page.fill("#q", "NOVELTY")
        check("search is case-insensitive", 0 < vis() < 6, f"visible {vis()}")
        page.fill("#q", "zzzznotpresent")
        check("a search with no matches hides all records", vis() == 0, f"visible {vis()}")
        check("the empty state explains records are still in the file",
              page.locator("#emptyFilter").is_visible()
              and "still in this file" in page.locator("#emptyFilter").inner_text())
        page.fill("#q", "")
        check("clearing the search restores everything", vis() == 6, f"visible {vis()}")

        print("\n  Grouping")
        page.select_option("#groupBy", "cat-primary")
        dyn = page.locator("h2.dyn").count()
        check("grouping by category creates headings", dyn > 0, f"{dyn} headings")
        check("no record is lost when regrouping", vis() == 6, f"visible {vis()}")
        check("static verdict headings are hidden in this mode",
              page.locator("h2[data-group]:not([hidden])").count() == 0)

        page.select_option("#groupBy", "evidence")
        check("grouping by evidence creates headings", page.locator("h2.dyn").count() > 0)
        check("still no record lost", vis() == 6, f"visible {vis()}")

        page.select_option("#groupBy", "verdict")
        check("returning to verdict restores the static headings",
              page.locator("h2[data-group]:not([hidden])").count() > 0)
        check("no leftover dynamic headings", page.locator("h2.dyn").count() == 0)
        check("record order is restored, relevant first",
              page.locator(".rec").first.get_attribute("data-verdict") == "relevant",
              page.locator(".rec").first.get_attribute("data-verdict") or "")

        page.select_option("#groupBy", "none")
        check("'no grouping' hides all headings",
              page.locator("h2:not([hidden])").count() == 0)
        check("all records still shown", vis() == 6, f"visible {vis()}")

        print("\n  Grouping vs filtering on multi-valued categories (SOP-004 6.2)")
        page.select_option("#groupBy", "verdict")
        multi = page.locator('.rec[data-cats*=" "]').count()
        check("the demo contains a multi-category record", multi > 0, f"{multi} found")

        print("\n  Print reveals everything")
        toggle("verdict", "irrelevant")
        page.emulate_media(media="print")
        printed = page.evaluate("""() => {
            let n = 0;
            document.querySelectorAll('.rec').forEach(r => {
                if (getComputedStyle(r).display !== 'none') n++;
            });
            return n;
        }""")
        check("printing shows every record regardless of filter", printed == 6, f"printed {printed}")
        check("a visually hidden checkbox is still focusable",
              page.evaluate("""() => {
                  const i = document.querySelector('.tog input');
                  return getComputedStyle(i).display !== 'none';
              }"""))
        check("controls are hidden when printing",
              page.evaluate("() => getComputedStyle(document.querySelector('.controls')).display") == "none")

        browser.close()

    print()
    if FAILURES:
        print(f"  ❌ {len(FAILURES)} failed: {FAILURES}\n")
        return 1
    print("  ✅ All interactivity tests passed.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
