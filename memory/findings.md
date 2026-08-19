# Findings — Research-Assistant

Research, discoveries, and constraints. Newest first.

---

## 2026-08-19 — Constraints implied by the Q1 North Star

Open questions the Blueprint must still resolve (do not answer these by guessing):

- **Zotero access path is undecided.** "Connected Zotero library" could mean the
  Zotero Web API (needs user ID + API key), the local `zotero.sqlite` database, a
  Better BibTeX export, or an MCP connector. Each has different credential needs,
  offline behavior, and PDF-attachment access. → Q2.
- **Screening at scale needs full text, not just metadata.** F5 forbids treating
  keyword similarity as relevance, and Q1 permits reading intros/conclusions during
  screening. So the pipeline needs access to PDF attachments, not only bibliographic
  records. Whether those PDFs are stored locally or in Zotero cloud storage affects
  the whole design. → Q2/Q3.
- **"Different terminology for similar ideas" defeats keyword search.** The
  positioning capability explicitly requires finding work that uses different
  vocabulary for the same concept. Keyword/BM25 retrieval alone cannot satisfy this;
  it implies semantic retrieval and/or citation-graph traversal (backward/forward
  snowballing from known-relevant papers).
- **The library is a closed set; novelty assessment is not.** Screening operates over
  Zotero. But "the strongest existing paper that could undermine my novelty claim"
  may not be in the library at all — that requires external discovery. These are two
  different retrieval problems and likely two different tools. → Q2.
- **Adjacent-literature coverage is the hard part of F6.** Refusing to declare a gap
  without evidence is easy; *demonstrating* adequate coverage of adjacent literatures
  is the real engineering problem. Needs an explicit, auditable coverage argument.
- **BUILD is an existing workflow, not a new one.** A `build-lit-review` skill is
  already available in this environment. Stage 1b should integrate with it rather
  than reimplement it. → verify its contract before designing 1b.
- **Digest requires persistent state.** "Do not miss important new work" implies
  remembering what was already shown, plus a durable profile of current research
  interests. The container is ephemeral, so that state must live in the repo or an
  external store. → Q3/Q4.

## 2026-08-19 — Repository baseline

- Repo `NegarSadeghiii/Research-Assistant` is **empty**: no commits on any branch,
  no remote heads. This is a greenfield build, not a modification of existing work.
- Working branch: `claude/system-pilot-blast-setup-gvl3uz`.
- Runtime: Linux container, Python 3 available, Chromium + Playwright pre-installed
  at `/opt/pw-browsers` (do not run `playwright install`).
- Outbound HTTPS is proxied; CA bundle at `/root/.ccr/ca-bundle.crt`. Any integration
  built in Phase L must work through the proxy — never disable TLS verification.
- Container is ephemeral. Anything not committed and pushed is lost.

## 2026-08-19 — Environment capabilities relevant to a research assistant

Available in-session and worth evaluating as building blocks once the Blueprint
names actual requirements. **Not yet chosen — listed as candidates only.**

- **Consensus MCP** (`mcp__Consensus__search`) — academic paper search with
  citation metadata. Requires inline numbered citations + verbatim usage message.
- **WebSearch / WebFetch** — general retrieval.
- **Document skills** — `pdf`, `docx`, `xlsx`, `pptx` for reading sources and
  producing payloads.
- **GitHub MCP** — repo scoped to `negarsadeghiii/research-assistant`.
- **Scheduling** — `create_trigger` / cron for Phase T firing mechanisms.
- **Artifact** — publishable HTML/Markdown pages, a candidate payload destination.

> ⚠️ Constraint: none of the above is a decision. The North Star and Delivery
> Payload answers determine which are used. No tool is adopted before Phase B closes.

## Prior art to research (after Blueprint approval)
- [ ] Existing open-source research-assistant pipelines worth borrowing from
- [ ] Citation/reference data formats (BibTeX, CSL-JSON) if references are in scope
