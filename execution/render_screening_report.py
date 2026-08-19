#!/usr/bin/env python3
"""Render a screening batch to a self-contained HTML report.

See /architecture/SOP-004-payload-rendering.md.

This renderer holds NO domain logic. It reads records and lays them out. It never
computes a verdict, infers a category, softens a reason, or supplies bibliographic
detail. If a fact is not in the registry, it does not reach the page.

Verify:
    python3 execution/tests/test_render_screening_report.py
    python3 execution/render_screening_report.py --demo --out .tmp/demo.html
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "execution"))
from validate_registry import validate_record  # noqa: E402

# Evidence kinds that mean the paper's own body text was read, as opposed to
# metadata only. Drives the "full text" vs "metadata only" badge (D-041).
BODY_EVIDENCE = {"introduction", "conclusion", "methods", "results", "full_text"}

VERDICT_ORDER = ["relevant", "uncertain", "irrelevant", "unscreened"]
VERDICT_LABEL = {"relevant": "Relevant", "uncertain": "Uncertain",
                 "irrelevant": "Irrelevant", "unscreened": "Not screened"}


def esc(value) -> str:
    """Registry text is data, not markup (SOP-004 section 5)."""
    return html.escape("" if value is None else str(value), quote=True)


def authors_display(authors: list[str] | None) -> tuple[str, str]:
    """Return (visible, full). Truncation is visual only; the registry is unchanged."""
    if not authors:
        return "—", ""
    full = "; ".join(authors)
    if len(authors) <= 3:
        return full, full
    return f"{authors[0]} … (+{len(authors) - 1} more)", full


def evidence_class(record: dict) -> tuple[str, str]:
    """Classify the strength of evidence actually inspected. Shown, never disclaimed."""
    inspected = set((record.get("provenance") or {}).get("evidence_inspected") or [])
    if inspected & BODY_EVIDENCE:
        return "full", "full text"
    if inspected:
        return "meta", "metadata only"
    return "none", "nothing inspected"


def render_record(record: dict) -> str:
    screening = record.get("screening") or {}
    bib = record.get("bibliographic") or {}
    prov = record.get("provenance") or {}
    ids = record.get("identifiers") or {}

    _, blocks = validate_record(record)
    citable = not blocks

    verdict = screening.get("verdict") or "unscreened"
    ev_cls, ev_label = evidence_class(record)
    visible_authors, full_authors = authors_display(bib.get("authors"))
    inspected = (prov.get("evidence_inspected") or [])

    doi = ids.get("doi")
    doi_html = (f'<a href="https://doi.org/{esc(doi)}">{esc(doi)}</a>' if doi
                else '<span class="muted">no DOI</span>')

    cats = "".join(f'<span class="cat">{esc(c)}</span>'
                   for c in (screening.get("categories") or []))

    flags = ""
    if not citable:
        reasons = "".join(f"<li>{esc(b)}</li>" for b in blocks)
        flags = (f'<div class="flag"><strong>Candidate only — not citable as '
                 f'evidence.</strong><ul>{reasons}</ul></div>')

    conflicts = ""
    for c in record.get("conflicts") or []:
        if c.get("status") == "unresolved":
            vals = ", ".join(f"{esc(k)}: {esc(v)}" for k, v in (c.get("values") or {}).items())
            conflicts += (f'<div class="conflict">Sources disagree on '
                          f'<strong>{esc(c.get("field"))}</strong> — {vals}. '
                          f'Surfaced, not resolved.</div>')

    reason = screening.get("reason")
    reason_html = (f'<p class="reason">{esc(reason)}</p>' if reason
                   else '<p class="reason muted">No reason recorded.</p>')

    chips = "".join(f'<span class="chip {"body" if i in BODY_EVIDENCE else ""}">{esc(i)}</span>'
                    for i in inspected) or '<span class="chip none">none</span>'

    return f"""
    <article class="rec {esc(verdict)}">
      <header>
        <h3 title="{esc(full_authors)}">{esc(bib.get('title') or '—')}</h3>
        <p class="meta">{esc(visible_authors)} · {esc(bib.get('year') or '—')} ·
           <em>{esc(bib.get('venue') or '—')}</em></p>
      </header>
      {reason_html}
      {conflicts}
      {flags}
      <div class="cats">{cats}</div>
      <dl class="prov">
        <div><dt>Evidence inspected</dt><dd><span class="ev {ev_cls}">{esc(ev_label)}</span> {chips}</dd></div>
        <div><dt>Identifier</dt><dd>{doi_html}</dd></div>
        <div><dt>Authority</dt><dd>{esc(bib.get('authority') or '—')}</dd></div>
        <div><dt>Discovered via</dt><dd>{esc(prov.get('discovered_via') or '—')}</dd></div>
        <div><dt>In Zotero</dt><dd>{esc(prov.get('zotero_status') or '—')}</dd></div>
        <div><dt>Screened against</dt><dd>{esc(screening.get('anchor_document') or '—')}</dd></div>
      </dl>
    </article>"""


CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#6b7280;--line:#e5e7eb;--card:#fff;
--rel:#047857;--relbg:#ecfdf5;--unc:#b45309;--uncbg:#fffbeb;
--irr:#6b7280;--irrbg:#f9fafb;--uns:#4338ca;--unsbg:#eef2ff;--warn:#b91c1c;--warnbg:#fef2f2;}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#0f1115;--fg:#e8eaed;--muted:#9aa0a6;--line:#2a2f3a;--card:#161a22;
--relbg:#052e23;--uncbg:#2e2205;--irrbg:#1a1d24;--unsbg:#1a1a3a;--warnbg:#2e0b0b;
--rel:#34d399;--unc:#fbbf24;--irr:#9aa0a6;--uns:#a5b4fc;--warn:#fca5a5;}}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.25rem 4rem;background:var(--bg);color:var(--fg);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
.wrap{max-width:60rem;margin:0 auto}
h1{font-size:1.5rem;margin:0 0 .25rem}
.sub{color:var(--muted);margin:0 0 2rem;font-size:.9rem}
.tallies{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:2rem}
.tally{border:1px solid var(--line);border-radius:.5rem;padding:.6rem .9rem;min-width:7rem}
.tally .n{font-size:1.5rem;font-weight:600;display:block;line-height:1.2}
.tally .l{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
h2{font-size:1.05rem;margin:2.5rem 0 .75rem;padding-bottom:.4rem;border-bottom:2px solid var(--line)}
h2 .count{color:var(--muted);font-weight:400}
.rec{border:1px solid var(--line);border-left:4px solid var(--line);border-radius:.5rem;
background:var(--card);padding:1rem 1.1rem;margin-bottom:.9rem}
.rec.relevant{border-left-color:var(--rel);background:var(--relbg)}
.rec.uncertain{border-left-color:var(--unc);background:var(--uncbg)}
.rec.irrelevant{border-left-color:var(--irr);background:var(--irrbg)}
.rec.unscreened{border-left-color:var(--uns);background:var(--unsbg)}
.rec h3{margin:0 0 .3rem;font-size:1rem;line-height:1.35}
.meta{margin:0 0 .7rem;color:var(--muted);font-size:.85rem}
.reason{margin:0 0 .7rem}
.muted{color:var(--muted)}
.cats{margin-bottom:.7rem;display:flex;gap:.35rem;flex-wrap:wrap}
.cat{font-size:.7rem;border:1px solid var(--line);border-radius:1rem;padding:.15rem .55rem;color:var(--muted)}
.prov{margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.4rem 1.5rem;
font-size:.8rem;border-top:1px solid var(--line);padding-top:.7rem}
.prov div{display:flex;gap:.5rem}
.prov dt{color:var(--muted);white-space:nowrap;margin:0}
.prov dd{margin:0}
.chip{display:inline-block;font-size:.7rem;border:1px solid var(--line);border-radius:.25rem;
padding:.05rem .35rem;margin-right:.2rem;color:var(--muted)}
.chip.body{border-color:var(--rel);color:var(--rel)}
.chip.none{border-color:var(--warn);color:var(--warn)}
.ev{font-weight:600;margin-right:.35rem}
.ev.full{color:var(--rel)} .ev.meta{color:var(--unc)} .ev.none{color:var(--warn)}
.flag,.conflict{background:var(--warnbg);border:1px solid var(--warn);border-radius:.4rem;
padding:.5rem .7rem;margin:0 0 .7rem;font-size:.85rem}
.flag ul{margin:.3rem 0 0 1rem;padding:0}
.note{border:1px solid var(--line);border-radius:.5rem;padding:1rem;color:var(--muted);font-size:.9rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);
color:var(--muted);font-size:.8rem}
a{color:inherit}
@media print{body{padding:0}.rec{break-inside:avoid}}
"""


def render(records: list[dict], generated_at: str, anchor: str | None = None) -> str:
    buckets = {v: [] for v in VERDICT_ORDER}
    for r in records:
        v = ((r.get("screening") or {}).get("verdict")) or "unscreened"
        buckets.setdefault(v, []).append(r)

    # Tallies are counted from the same records the page displays, in one pass, so the
    # summary cannot disagree with the table beneath it (SOP-004 section 8).
    tallies = "".join(
        f'<div class="tally"><span class="n">{len(buckets[v])}</span>'
        f'<span class="l">{esc(VERDICT_LABEL[v])}</span></div>'
        for v in VERDICT_ORDER)

    meta_only = sum(1 for r in records if evidence_class(r)[0] == "meta")
    noncitable = sum(1 for r in records if validate_record(r)[1])
    tallies += (f'<div class="tally"><span class="n">{meta_only}</span>'
                f'<span class="l">Metadata only</span></div>'
                f'<div class="tally"><span class="n">{noncitable}</span>'
                f'<span class="l">Candidate only</span></div>')

    if not records:
        body = ('<div class="note"><strong>No papers screened in this batch.</strong> '
                'A screening run that examined nothing is recorded rather than omitted '
                '— unlike an empty digest, which produces no file at all (BR-18).</div>')
    else:
        body = ""
        for v in VERDICT_ORDER:
            if not buckets[v]:
                continue
            body += (f'<h2>{esc(VERDICT_LABEL[v])} '
                     f'<span class="count">({len(buckets[v])})</span></h2>')
            body += "".join(render_record(r) for r in buckets[v])

    anchor_line = (f"Screened against <code>{esc(anchor)}</code> · " if anchor else "")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Screening report — {esc(generated_at[:10])}</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>Screening report</h1>
<p class="sub">{anchor_line}{len(records)} record(s) · generated {esc(generated_at)}</p>
<div class="tallies">{tallies}</div>
{body}
<footer>
Generated from <code>state/paper-registry.json</code>. Every statement on this page is a
registry field — this report computes no verdicts and adds no bibliographic detail.
Irrelevant and uncertain papers are retained deliberately (BR-20): the rejection record
is what explains a past decision and prevents re-screening. Records marked
<em>candidate only</em> failed V5 or V6 and may not be cited as supporting evidence.
</footer>
</div></body></html>"""


def demo_records() -> list[dict]:
    """A synthetic batch covering every state the renderer must handle.

    Bibliographic values are deliberately fictional placeholders. This file asserts
    nothing about any real paper (SOP-001 lesson, 2026-08-19).
    """
    def rec(**kw):
        base = {
            "record_id": kw.get("rid", "0" * 40),
            "identifiers": {"doi": kw.get("doi"), "zotero_key": "DEMO0001",
                            "openalex_id": None, "pmid": None, "s2_id": None,
                            "arxiv_id": None},
            "identifier_verified_against_source": kw.get("verified", True),
            "bibliographic": {"title": kw["title"], "authors": kw.get("authors", ["Example, A."]),
                              "year": kw.get("year", 2024), "venue": kw.get("venue", "Example Journal"),
                              "authority": "crossref"},
            "versions": [], "conflicts": kw.get("conflicts", []),
            "provenance": {"discovered_via": kw.get("via", "zotero"),
                           "discovery_query": "demo", "first_seen": "2026-08-19",
                           "evidence_inspected": kw.get("evidence", ["title", "abstract"]),
                           "full_text_available": True, "user_read": False,
                           "build_completed": False, "appeared_in_digest": [],
                           "zotero_status": kw.get("zstatus", "in_library")},
            "screening": {"verdict": kw["verdict"], "reason": kw.get("reason", ""),
                          "categories": kw.get("cats", []),
                          "anchor_document": kw.get("anchor", "demo://anchor.docx"),
                          "anchor_document_confirmed_by_user": True,
                          "screened_at": "2026-08-19", "screener_version": "0.1.0"},
            "staging": {"state": "accepted", "reason_it_may_matter": "demo",
                        "decided_at": "2026-08-19"},
        }
        return base

    return [
        rec(rid="a" * 40, title="A full-text screened paper with a verified identifier",
            doi="10.1000/demo.full", verdict="relevant",
            evidence=["title", "abstract", "introduction", "conclusion"],
            reason="Body text was read; the formulation matches the anchor document's "
                   "core assumption but omits one constraint.",
            cats=["methodological_precedent", "closest_to_work"]),
        rec(rid="b" * 40, title="A paper judged from metadata alone",
            doi="10.1000/demo.meta", verdict="uncertain",
            evidence=["title", "abstract", "metadata"],
            reason="No PDF attached, so only the abstract was available. Cannot tell "
                   "whether it formulates a model or reviews the area.",
            cats=["needs_citation_support"]),
        rec(rid="c" * 40, title="A paper whose identifier was never verified",
            doi="10.1000/demo.unverified", verdict="relevant", verified=False,
            evidence=["title", "abstract", "introduction"],
            reason="Appears directly relevant, but the DOI was never resolved against "
                   "its source.",
            cats=["novelty_threat"], via="openalex", zstatus="not_submitted"),
        rec(rid="d" * 40, title="A paper on which two sources disagree",
            doi="10.1000/demo.conflict", verdict="relevant",
            evidence=["title", "abstract", "methods"],
            reason="Directly comparable method, but the publication year is disputed.",
            conflicts=[{"field": "year", "values": {"crossref": 2021, "openalex": 2020},
                        "status": "unresolved", "flagged_at": "2026-08-19"}],
            cats=["closest_to_work"]),
        rec(rid="e" * 40, title="A paper screened out, retained with its reason",
            doi="10.1000/demo.irrelevant", verdict="irrelevant",
            evidence=["title", "abstract", "introduction"],
            reason="Shares vocabulary with the anchor document but addresses a "
                   "different decision problem entirely — retained so it is not "
                   "re-screened.",
            cats=[]),
        rec(rid="f" * 40, title="A discovered paper not yet screened",
            doi=None, verdict="unscreened", verified=False, evidence=[],
            reason="", anchor="", via="consensus", zstatus="not_submitted"),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=str(REPO_ROOT / "state" / "paper-registry.json"))
    ap.add_argument("--out", default=None,
                    help="output path; defaults to /screening-results/<today>.html")
    ap.add_argument("--anchor", default=None, help="anchor document the batch was screened against")
    ap.add_argument("--demo", action="store_true", help="render a synthetic batch covering every state")
    args = ap.parse_args()

    if args.demo:
        records, anchor = demo_records(), "demo://anchor.docx"
    else:
        path = Path(args.registry)
        if not path.exists():
            print(json.dumps({"tool": "render_screening_report", "status": "invalid",
                              "detail": f"{path} not found"}))
            return 4
        records = json.loads(path.read_text()).get("records", [])
        anchor = args.anchor

    out = Path(args.out) if args.out else (
        REPO_ROOT / "screening-results" / f"{date.today().isoformat()}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out.write_text(render(records, generated, anchor), encoding="utf-8")

    print(json.dumps({"tool": "render_screening_report", "status": "green",
                      "detail": f"Rendered {len(records)} record(s).",
                      "evidence": {"path": str(out), "records": len(records),
                                   "bytes": out.stat().st_size},
                      "checked_at": generated}))
    print(f"[OK] wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
