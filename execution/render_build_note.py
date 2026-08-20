#!/usr/bin/env python3
"""Create or incrementally update a BUILD session notes file.

Format matches the `build-lit-review` skill's own notes structure exactly. This tool
does NOT run BUILD and does not generate content: it writes the user's words into the
right file, one stage at a time, so the notes exist on disk before the session ends.

⛔ P4 / BR-1: nothing here may summarise a paper. Every stage's content comes from the
user. A stage with no user content is written as an explicit placeholder, never filled
in on their behalf.

Verify: python3 execution/tests/test_render_build_note.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = REPO_ROOT / "literature-notes"

# The five BUILD stages, in the skill's own order and wording.
STAGES = [
    ("B", "Reading purposes"),
    ("U", "Knowledge gaps to research"),
    ("I", "Core idea (her words)"),
    ("L", "Alignment"),
    ("D", "What I learned (her words, mapped to purposes)"),
]
STAGE_KEYS = [s[0] for s in STAGES]
PLACEHOLDER = "_(not yet completed)_"
L_HINT = "Aligned / Diverges / Unresolved — reasoning …"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or "untitled"


def note_path(title: str, on: date | None = None) -> Path:
    return NOTES_DIR / f"{(on or date.today()).isoformat()}-{slugify(title)}.md"


def build_note(title: str, stages: dict[str, str], created: str) -> str:
    """Render the whole note. Stages absent from `stages` stay explicit placeholders."""
    out = [f"# BUILD notes — {title} — {created[:10]}", ""]
    for key, heading in STAGES:
        out.append(f"## {key}: {heading}")
        content = (stages.get(key) or "").strip()
        if content:
            out.append(content)
        elif key == "L":
            out.append(f"{PLACEHOLDER}  {L_HINT}")
        else:
            out.append(PLACEHOLDER)
        out.append("")
    out += ["---", "",
            f"_Session notes written incrementally as each stage completed. "
            f"Last updated {created}._",
            "_Content is the reader's own work — this file contains no summary of the "
            "paper (BR-1, P4)._", ""]
    return "\n".join(out)


def parse_note(text: str) -> tuple[str, dict[str, str]]:
    """Read an existing note back into (title, stages) so updates preserve prior work."""
    title = ""
    m = re.match(r"# BUILD notes — (.+?) — \d{4}-\d{2}-\d{2}", text)
    if m:
        title = m.group(1)
    stages: dict[str, str] = {}
    parts = re.split(r"^## ([BUILD]): .*$", text, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        key, body = parts[i], parts[i + 1]
        body = body.split("\n---\n")[0].strip()
        if body and not body.startswith(PLACEHOLDER):
            stages[key] = body
    return title, stages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help="paper short title")
    ap.add_argument("--stage", choices=STAGE_KEYS, help="stage to write")
    ap.add_argument("--content", help="the user's own words for that stage")
    ap.add_argument("--content-file", help="read the stage content from a file")
    ap.add_argument("--out", help="explicit output path")
    args = ap.parse_args()

    if args.stage and not (args.content or args.content_file):
        print(json.dumps({"tool": "render_build_note", "status": "missing",
                          "detail": f"Stage {args.stage} given with no content. This tool "
                                    f"never writes stage content on the reader's behalf "
                                    f"(BR-1, P4)."}))
        return 3

    path = Path(args.out) if args.out else note_path(args.title)
    path.parent.mkdir(parents=True, exist_ok=True)

    title, stages = (args.title, {})
    if path.exists():
        existing_title, stages = parse_note(path.read_text(encoding="utf-8"))
        title = existing_title or args.title

    if args.stage:
        content = (Path(args.content_file).read_text(encoding="utf-8")
                   if args.content_file else args.content)
        stages[args.stage] = content

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(build_note(title, stages, now), encoding="utf-8")

    done = [k for k in STAGE_KEYS if stages.get(k)]
    print(json.dumps({"tool": "render_build_note", "status": "green",
                      "detail": f"Wrote note with {len(done)}/5 stages complete.",
                      "evidence": {"path": str(path), "stages_complete": done,
                                   "stages_pending": [k for k in STAGE_KEYS if k not in done]},
                      "checked_at": now}))
    print(f"[OK] {path}  ({len(done)}/5 stages)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
