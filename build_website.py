"""
Build the Top Spin Collection static website from top400_data.json.

Generates docs/index.html for GitHub Pages hosting.
Design matches NBA TAP Rankings site: black background, white text,
Courier New monospace, Georgia serif headings, compact tables.

Usage: python build_website.py
"""
import json, os, sys, io
from html import escape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "top400_data.json")
DOCS_DIR = os.path.join(SCRIPT_DIR, "docs")

def main():
    # Load data
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    snapshot = data["snapshot"]
    total_unique = data["total_unique"]
    total_entries = data["total_entries"]
    generated = data["generated"][:10]  # Just the date
    genres = data["genres"]

    print(f"Building website from {JSON_PATH}")
    print(f"Snapshot: {snapshot}, {total_unique} unique releases, {len(genres)} genres")

    # Build genre nav
    nav_items = []
    for g in genres:
        slug = g["name"].lower().replace(" ", "-")
        nav_items.append(f'<a href="#{slug}">{escape(g["name"])} ({g["count"]})</a>')
    nav_html = "\n        ".join(nav_items)

    # Build genre sections
    sections_html = []
    for g in genres:
        slug = g["name"].lower().replace(" ", "-")
        rows_html = []
        genre_rank = 1
        for r in g["releases"]:
            title_escaped = escape(r["title"])
            artist_escaped = escape(r["artist"])
            link = r.get("link", "")

            if link:
                title_cell = f'<a href="{escape(link)}" target="_blank" rel="noopener">{title_escaped}</a>'
            else:
                title_cell = title_escaped

            rating = f'{r["rating"]:.2f}' if r["rating"] is not None else "\u2014"
            have = f'{r["have"]}' if r["have"] is not None else "\u2014"
            want = f'{r["want"]}' if r["want"] is not None else "\u2014"
            pr = f'{r["power_rank"]:,.0f}' if r["power_rank"] is not None else "\u2014"

            rows_html.append(f"""            <tr>
              <td class="rank">{genre_rank}</td>
              <td class="artist"><div class="clamp"><span>{artist_escaped}</span></div></td>
              <td class="album"><div class="clamp">{title_cell}</div></td>
              <td class="num rating-col">{rating}</td>
              <td class="num have-col">{have}</td>
              <td class="num want-col">{want}</td>
              <td class="num">{pr}</td>
            </tr>""")
            genre_rank += 1

        rows_joined = "\n".join(rows_html)
        sections_html.append(f"""      <div class="table-section" id="{slug}">
        <div class="table-header"><h2>{escape(g["name"])} <span class="count">({g["count"]})</span></h2></div>
        <table>
          <thead>
            <tr>
              <th class="rank">#</th>
              <th class="artist">Artist</th>
              <th class="album">Album</th>
              <th class="num rating-col">Rating</th>
              <th class="num have-col">Have</th>
              <th class="num want-col">Want</th>
              <th class="num">Power<br>Rank</th>
            </tr>
          </thead>
          <tbody>
{rows_joined}
          </tbody>
        </table>
      </div>""")

    sections_joined = "\n\n".join(sections_html)

    # Full HTML with inline CSS (matching NBA TAP pattern)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Top Spin Collection</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Courier New', Courier, monospace;
      font-weight: 700;
      background: #000;
      color: #fff;
      line-height: 1.4;
      padding: 20px;
    }}

    .container {{
      max-width: 1000px;
      margin: 0 auto;
      border: 3px solid #fff;
      padding: 0;
    }}

    /* Header — white band */
    header {{
      text-align: center;
      padding: 25px 20px 15px;
      background: #fff;
      color: #000;
    }}

    header h1 {{
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 3em;
      font-weight: 900;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 2px;
    }}

    /* Genre nav */
    #genre-nav {{
      padding: 12px 16px;
      border-bottom: 2px solid #fff;
      text-align: center;
    }}

    #genre-nav a {{
      font-size: 0.85em;
      color: #fff;
      text-decoration: none;
      letter-spacing: 0.02em;
      margin: 3px 8px;
      display: inline-block;
      border-bottom: 1px solid transparent;
      transition: border-bottom-color 0.15s;
    }}

    #genre-nav a:hover {{
      border-bottom-color: #fff;
    }}

    /* Genre section headers — white band */
    .table-section {{
      border-bottom: 2px solid #fff;
    }}

    .table-section:last-child {{
      border-bottom: none;
    }}

    .table-header {{
      background: #fff;
      padding: 10px 12px;
      text-align: center;
    }}

    .table-section h2 {{
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 1em;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #000;
      margin: 0;
      padding: 0;
      border: none;
      display: inline;
    }}

    .table-section h2 .count {{
      font-weight: 400;
      font-style: italic;
      text-transform: none;
      letter-spacing: 0;
      font-size: 0.9em;
      margin-left: 6px;
    }}

    /* Tables */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8em;
    }}

    thead th {{
      font-family: Georgia, 'Times New Roman', serif;
      text-align: left;
      padding: 4px 5px;
      font-weight: 900;
      font-size: 0.8em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #fff;
      border-bottom: 1px solid #fff;
      background: #000;
    }}

    tbody tr {{
      border-bottom: 1px solid #333;
    }}

    tbody tr:last-child {{
      border-bottom: none;
    }}

    td {{
      padding: 3px 5px;
      vertical-align: middle;
    }}

    /* Column styles */
    .rank {{
      width: 24px;
      text-align: center;
      font-weight: 700;
    }}

    .artist {{
      max-width: 110px;
    }}

    .album {{
      max-width: 130px;
    }}

    .clamp {{
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 2.8em;
      -webkit-box-pack: center;
    }}

    .num {{
      text-align: center;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    thead th.num {{
      text-align: center;
    }}

    thead th.rank {{
      text-align: center;
    }}

    /* Links — white on dark */
    a {{
      color: #fff;
      text-decoration: none;
      border-bottom: 1px solid #555;
    }}

    a:hover {{
      border-bottom-color: #fff;
    }}

    .table-header a,
    header a {{
      color: #000;
      border-bottom: none;
    }}

    /* Footer */
    footer {{
      text-align: center;
      padding: 14px 0;
      border-top: 2px solid #fff;
      font-size: 0.82em;
      color: #fff;
      background: #000;
    }}

    footer a {{
      color: #fff;
      border-bottom: 1px solid #555;
    }}

    footer a:hover {{
      border-bottom-color: #fff;
    }}

    /* Responsive — mobile primary, all columns visible */
    @media (max-width: 600px) {{
      body {{ padding: 8px; }}

      header h1 {{ font-size: 1.8em; letter-spacing: 0.04em; }}

      #genre-nav a {{ margin: 2px 4px; font-size: 0.7em; }}

      table {{ font-size: 0.65em; }}
      td, thead th {{ padding: 2px 3px; }}

      .artist {{ max-width: 80px; }}
      .album {{ max-width: 90px; }}
      .rank {{ width: 18px; }}
    }}

    @media (max-width: 380px) {{
      header h1 {{ font-size: 1.5em; }}

      table {{ font-size: 0.58em; }}
      td, thead th {{ padding: 2px 2px; }}

      .artist {{ max-width: 65px; }}
      .album {{ max-width: 72px; }}
      .rank {{ width: 16px; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Top Spin Collection</h1>
    </header>

    <div id="genre-nav">
        {nav_html}
    </div>

    <main>
{sections_joined}
    </main>

    <footer>
      <div>Community data sourced from <a href="https://www.discogs.com" target="_blank" rel="noopener">Discogs</a></div>
    </footer>
  </div>

  <script>
    document.querySelectorAll('#genre-nav a').forEach(a => {{
      a.addEventListener('click', e => {{
        e.preventDefault();
        document.querySelector(a.getAttribute('href')).scrollIntoView({{behavior: 'smooth'}});
      }});
    }});
  </script>
</body>
</html>"""

    # Write file (single HTML with inline CSS, no separate style.css)
    os.makedirs(DOCS_DIR, exist_ok=True)

    html_path = os.path.join(DOCS_DIR, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {html_path}")

    print(f"\nWebsite built in {DOCS_DIR}/")
    print("Done.")

if __name__ == "__main__":
    main()
