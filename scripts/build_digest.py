#!/usr/bin/env python3
"""Build a dated HTML digest from a JSON list of scanned articles.

Usage:
    python scripts/build_digest.py articles.json
    cat articles.json | python scripts/build_digest.py -

Input JSON shape:
    {
      "date": "2026-07-10",            # optional; defaults to today (UTC)
      "articles": [
        {
          "title": "...",
          "source": "Quanta Magazine",
          "url": "https://...",
          "published": "2026-07-08",   # optional, free-form
          "topic": "Theoretical physics",
          "abstract": "One-paragraph summary of the article.",
          "why": "Why it made the top 15."   # optional
        },
        ...
      ]
    }

Writes: scans/<date>/index.html  (a self-contained, theme-aware page)
The articles are rendered in the order given and capped at the top 15.
"""
import html
import json
import os
import sys
from datetime import datetime, timezone

TOP_N = 15
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(value):
    return html.escape(str(value or "").strip())


def load_payload(arg):
    if arg in ("-", None):
        raw = sys.stdin.read()
    else:
        with open(arg, "r", encoding="utf-8") as fh:
            raw = fh.read()
    return json.loads(raw)


def card(article, rank):
    title = esc(article.get("title", "Untitled"))
    url = esc(article.get("url", ""))
    source = esc(article.get("source", ""))
    topic = esc(article.get("topic", ""))
    published = esc(article.get("published", ""))
    abstract = esc(article.get("abstract", ""))
    why = esc(article.get("why", ""))

    meta_bits = "".join(
        f'<span class="chip">{bit}</span>'
        for bit in (source, topic, published)
        if bit
    )
    title_html = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title
    why_html = f'<p class="why"><span>Why it made the cut</span>{why}</p>' if why else ""
    read_label = f"Read at {source}" if source else "Read the full article"
    read_html = (
        f'<a class="read" href="{url}" target="_blank" rel="noopener">{read_label} &rarr;</a>'
        if url else ""
    )

    return f"""      <article class="card">
        <div class="rank">{rank:02d}</div>
        <div class="body">
          <h2>{title_html}</h2>
          <div class="meta">{meta_bits}</div>
          <p class="abstract">{abstract}</p>
          {why_html}
          {read_html}
        </div>
      </article>"""


def build_html(date_str, articles, generated_at):
    cards = "\n".join(card(a, i + 1) for i, a in enumerate(articles[:TOP_N]))
    sources = sorted({esc(a.get("source", "")) for a in articles[:TOP_N] if a.get("source")})
    source_line = " · ".join(sources)
    pretty_date = date_str
    try:
        pretty_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %-d, %Y")
    except ValueError:
        pass

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Science Digest — {esc(date_str)}</title>
<style>
  :root {{
    --bg: #f7f6f3; --panel: #ffffff; --ink: #1a1a1a; --muted: #6b6b6b;
    --line: #e6e3dc; --accent: #7a5cff; --chip: #f0eef8; --chip-ink: #4a3fb0;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14131a; --panel: #1d1b26; --ink: #ece9f5; --muted: #a09cb0;
      --line: #2c2937; --accent: #a794ff; --chip: #262233; --chip-ink: #c9beff;
    }}
  }}
  :root[data-theme="light"] {{
    --bg: #f7f6f3; --panel: #ffffff; --ink: #1a1a1a; --muted: #6b6b6b;
    --line: #e6e3dc; --accent: #7a5cff; --chip: #f0eef8; --chip-ink: #4a3fb0;
  }}
  :root[data-theme="dark"] {{
    --bg: #14131a; --panel: #1d1b26; --ink: #ece9f5; --muted: #a09cb0;
    --line: #2c2937; --accent: #a794ff; --chip: #262233; --chip-ink: #c9beff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  .wrap {{ max-width: 820px; margin: 0 auto; padding: 48px 20px 80px; }}
  header {{ border-bottom: 2px solid var(--line); padding-bottom: 24px; margin-bottom: 8px; }}
  .kicker {{ letter-spacing: .18em; text-transform: uppercase; font-size: 12px; color: var(--accent); font-weight: 700; }}
  h1 {{ font-size: clamp(28px, 5vw, 40px); line-height: 1.15; margin: 10px 0 6px; }}
  .sub {{ color: var(--muted); font-size: 15px; }}
  .sources {{ color: var(--muted); font-size: 13px; margin-top: 10px; }}
  .card {{
    display: flex; gap: 18px; padding: 26px 0; border-bottom: 1px solid var(--line);
  }}
  .rank {{
    font-variant-numeric: tabular-nums; font-weight: 800; font-size: 20px;
    color: var(--accent); min-width: 34px; padding-top: 2px;
  }}
  .body {{ flex: 1; min-width: 0; }}
  h2 {{ font-size: 20px; line-height: 1.3; margin: 0 0 8px; }}
  h2 a {{ color: var(--ink); text-decoration: none; }}
  h2 a:hover {{ color: var(--accent); text-decoration: underline; }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
  .chip {{
    background: var(--chip); color: var(--chip-ink); font-size: 12px; font-weight: 600;
    padding: 3px 9px; border-radius: 999px;
  }}
  .abstract {{ margin: 0; color: var(--ink); }}
  .why {{
    margin: 12px 0 0; padding: 10px 14px; border-left: 3px solid var(--accent);
    background: var(--chip); border-radius: 0 8px 8px 0; font-size: 14px; color: var(--muted);
  }}
  .why span {{ display: block; text-transform: uppercase; letter-spacing: .1em; font-size: 10px; font-weight: 700; color: var(--accent); margin-bottom: 3px; }}
  .read {{
    display: inline-block; margin-top: 12px; font-size: 14px; font-weight: 600;
    color: var(--accent); text-decoration: none;
  }}
  .read:hover {{ text-decoration: underline; }}
  footer {{ margin-top: 40px; color: var(--muted); font-size: 13px; text-align: center; }}
  .toggle {{
    position: fixed; top: 16px; right: 16px; background: var(--panel); color: var(--ink);
    border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; cursor: pointer; font-size: 13px;
  }}
</style>
</head>
<body>
<button class="toggle" onclick="var r=document.documentElement;r.dataset.theme=(r.dataset.theme==='dark'?'light':'dark');">◐ theme</button>
<div class="wrap">
  <header>
    <div class="kicker">Agentic Science Digest</div>
    <h1>The week in fundamental science</h1>
    <div class="sub">Top {min(len(articles), TOP_N)} articles · {esc(pretty_date)}</div>
    <div class="sources">Scanned: {source_line}</div>
  </header>
  <main>
{cards}
  </main>
  <footer>
    Generated {esc(generated_at)} by the <code>/scan-journals</code> agent · abstracts are AI summaries; follow the links for the originals.
  </footer>
</div>
</body>
</html>
"""


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "-"
    payload = load_payload(arg)
    articles = payload.get("articles", [])
    if not articles:
        sys.exit("No articles in payload.")

    now = datetime.now(timezone.utc)
    date_str = payload.get("date") or now.strftime("%Y-%m-%d")
    generated_at = now.strftime("%Y-%m-%d %H:%M UTC")

    out_dir = os.path.join(ROOT, "scans", date_str)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(build_html(date_str, articles, generated_at))

    # Persist the raw data next to the page for reproducibility.
    with open(os.path.join(out_dir, "articles.json"), "w", encoding="utf-8") as fh:
        json.dump({"date": date_str, "generated_at": generated_at,
                   "articles": articles[:TOP_N]}, fh, indent=2, ensure_ascii=False)

    print(f"Wrote {len(articles[:TOP_N])} articles -> {os.path.relpath(out_path, ROOT)}")


if __name__ == "__main__":
    main()
