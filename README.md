# Scientific — Agentic Journal Scanner

An on-demand agent that scans a curated list of top science journals and
magazines and produces a **dated HTML digest of the 15 best articles** worth
reading right now.

---

## Instructions

### 1. Run a scan

In Claude Code (from the repo root), type the slash command:

```
/scan-journals
```

That's the whole trigger. The agent then works end to end and needs no further
input. Behind the scenes it:

1. **Reads** the source list in [`sources.json`](sources.json).
2. **Fetches** the latest front-page articles from each journal (title, link,
   date, topic, and dek) and builds a candidate pool.
3. **Ranks** the whole pool and keeps the **top 15** — judged on depth,
   freshness, scientific substance, and spread across fields and outlets.
4. **Renders** the winners into a dated page by calling
   [`scripts/build_digest.py`](scripts/build_digest.py).
5. **Shows** you the digest inline and **commits** the new dated folder.

The result lands in:

```
scans/<YYYY-MM-DD>/index.html     # the digest you read
scans/<YYYY-MM-DD>/articles.json  # the data behind it (reproducible)
```

Open `index.html` in any browser. It's self-contained, responsive, and adapts
to light/dark theme (with a manual toggle top-right). Each card links to the
original article.

### 2. Choose which journals get scanned

[`sources.json`](sources.json) is the single source of truth. Add, remove, or
re-order entries and the next `/scan-journals` run honors them:

```json
{
  "sources": [
    { "name": "Quanta Magazine", "url": "https://www.quantamagazine.org/",
      "beat": "Math, physics, CS", "note": "The gold standard for depth." }
  ]
}
```

Currently scanned: Quanta Magazine · Aeon (+ Psyche) · Nautilus ·
American Scientist · Symmetry · Nature (news) · Science (news) ·
Scientific American · New Scientist · MIT Technology Review · Undark.

### 3. Rebuild a digest without re-scanning

The HTML is generated deterministically from the saved JSON, so you can tweak
the data (or the template) and regenerate the page offline:

```bash
python scripts/build_digest.py scans/2026-07-10/articles.json
```

You can also feed it a hand-authored payload:

```bash
python scripts/build_digest.py my-articles.json   # or:  cat my-articles.json | python scripts/build_digest.py -
```

**Payload shape** (the agent writes this automatically; `date` defaults to
today, and only the first 15 articles are rendered):

```json
{
  "date": "2026-07-10",
  "articles": [
    {
      "title": "...",
      "source": "Quanta Magazine",
      "url": "https://...",
      "published": "Jul 1, 2026",
      "topic": "Synthetic biology",
      "abstract": "Two-to-four sentence summary in plain language.",
      "why": "One line on why it made the top 15."
    }
  ]
}
```

---

## How it works

The scan is split into a fuzzy half and a deterministic half:

- **The agent** ([`.claude/commands/scan-journals.md`](.claude/commands/scan-journals.md))
  handles the judgment calls — fetching pages, writing abstracts, ranking, and
  picking 15.
- **The script** ([`scripts/build_digest.py`](scripts/build_digest.py)) handles
  rendering — turning the chosen JSON into a styled page. Because rendering is
  deterministic, any digest can be reproduced from its `articles.json`.

If a source can't be reached (rate limit, login wall, crawler block), the run
skips it, notes the gap, and still produces a digest rather than failing.

## Layout

```
sources.json                      # curated journal list (the source of truth)
.claude/commands/scan-journals.md # the on-demand agent command
scripts/build_digest.py           # deterministic JSON -> HTML renderer
scans/<date>/index.html           # a generated digest
scans/<date>/articles.json        # the data behind that digest
```

## Example

See [`scans/2026-07-10/`](scans/2026-07-10/) for a real run — 15 articles across
Quanta, Nature, Science, Scientific American, Nautilus, MIT Technology Review,
and Symmetry. Today's top pick:

> **01 · For the First Time, a Cell Built From Scratch Grows and Divides** —
> *Quanta Magazine, synthetic biology.* Researchers assembled a synthetic cell
> that both grows and divides — two hallmarks of life never before achieved
> together in a built-from-scratch system — pushing the boundary of what counts
> as living. → https://www.quantamagazine.org/for-the-first-time-a-cell-built-from-scratch-grows-and-divides-20260701/
