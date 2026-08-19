# Findings — Research-Assistant

Research, discoveries, and constraints. Newest first.

---

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
