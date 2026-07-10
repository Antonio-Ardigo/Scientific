# Scientific — Agentic Journal Scanner

An on-demand agent that scans a curated list of top science journals and
magazines and produces a **dated HTML digest of the 15 best articles** worth
reading right now.

## Use it

In Claude Code, run the slash command:

```
/scan-journals
```

The agent will:

1. Fetch the latest articles from every source in [`sources.json`](sources.json).
2. Rank the whole pool and pick the **top 15** (depth, freshness, substance,
   spread across fields).
3. Build `scans/<YYYY-MM-DD>/index.html` — a self-contained, theme-aware page
   with each article's title, source, topic, link, an abstract, and a one-line
   note on why it made the cut.
4. Show it inline as an artifact and commit the new dated folder.

The raw picks are also saved as `scans/<date>/articles.json` for reproducibility.

## Sources scanned

Quanta Magazine · Aeon (+ Psyche) · Nautilus · American Scientist · Symmetry ·
Nature (news) · Science (news) · Scientific American · New Scientist ·
MIT Technology Review · Undark.

Edit [`sources.json`](sources.json) to add, remove, or re-weight sources — the
command reads it as the source of truth.

## Layout

```
sources.json                     # curated journal list (the source of truth)
.claude/commands/scan-journals.md # the on-demand agent command
scripts/build_digest.py          # deterministic JSON -> HTML renderer
scans/<date>/index.html          # a generated digest
scans/<date>/articles.json       # the data behind that digest
```

## Rebuild a digest from data

The HTML is generated deterministically from a JSON payload, so you can rebuild
or tweak a run without re-scanning:

```bash
python scripts/build_digest.py scans/2026-07-10/articles.json
```
