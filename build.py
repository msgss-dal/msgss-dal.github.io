"""Build seminar/index.html from talks.yaml.

Edit talks.yaml, then run:  python build.py
(GitHub Actions also runs this automatically when talks.yaml changes.)
"""
import html
import os
import yaml

with open("talks.yaml", encoding="utf-8") as f:
    data = yaml.safe_load(f)

info = data.get("info") or {}
talks = data["talks"]
name = html.escape(info.get("name") or "Talks")
contact = html.escape(info.get("contact") or "")
blurb = "".join(
    f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>"
    for p in str(info.get("blurb") or "").split("\n\n") if p.strip()
)

talks.sort(key=lambda t: str(t["date"]), reverse=True)

parts = []
year = None
for t in talks:
    y = str(t["date"])[:4]
    if y != year:
        year = y
        parts.append(f"<h2>{year}</h2>")
    title = html.escape(t.get("title") or "TBA")
    meta = f'{t["date"]} &middot; {html.escape(t["speaker"])}'
    abstract = t.get("abstract") or ""
    paras = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>"
        for p in abstract.split("\n\n") if p.strip()
    )
    parts.append(f"<article><h3>{title}</h3><p><i>{meta}</i></p>{paras}</article>")

page = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>

    <link href="../style.css" rel="stylesheet" type="text/css" media="all">
    <style>
      .body {{ max-width: 42rem; line-height: 1.5; }}
      article {{ margin-bottom: 2rem; }}
      article h3 {{ margin-bottom: 0; }}
    </style>
  </head>

  <body>
    <div class="menu">
        <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="index.html">Seminar</a></li>
            <li><a href="../travel-grant.html">Travel Grant</a></li>
            <li><a href="../docs.html">Documents</a></li>
            <li><a href="../contact.html">Contact</a></li>
        </ul>
    </div>
    <div class="body">
<h1>{name}</h1>
{blurb}
<p><b>Location:</b> {html.escape(str(info.get("location") or "TBA"))}<br>
<b>Time:</b> {html.escape(str(info.get("time") or "TBA"))}<br>
<b>Want to give a presentation?</b> Email <a href="mailto:{contact}">{contact}</a></p>
{chr(10).join(parts)}
    </div>
  </body>
</html>
"""

os.makedirs("seminar", exist_ok=True)
with open("seminar/index.html", "w", encoding="utf-8") as f:
    f.write(page)
