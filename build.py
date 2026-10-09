"""Build seminar/index.html and one page per talk (seminar/talks/) from talks.yaml.

Edit talks.yaml, then run:  python build.py
(GitHub Actions also runs this automatically when talks.yaml changes.)
"""
import html
import datetime
import glob
import os
import re
import unicodedata
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


def nice_date(d):
    """2026-10-09 -> October 9, 2026"""
    if not isinstance(d, datetime.date):
        d = datetime.date.fromisoformat(str(d))
    return f"{d:%B} {d.day}, {d.year}"


def slugify(text):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# Each talk gets a page at seminar/talks/<date>-<speaker>.html
# (with -2, -3, ... added if two talks would get the same name).
used = set()
for t in talks:
    base = f'{t["date"]}-{slugify(t["speaker"])}'
    slug, n = base, 2
    while slug in used:
        slug, n = f"{base}-{n}", n + 1
    used.add(slug)
    t["_slug"] = slug

parts = []
year = None
for t in talks:
    y = str(t["date"])[:4]
    if y != year:
        year = y
        parts.append(f"<h2>{year}</h2>")
    title = html.escape(t.get("title") or "TBA")
    meta = f'{nice_date(t["date"])} &middot; {html.escape(t["speaker"])}'
    abstract = t.get("abstract") or ""
    paras = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>"
        for p in abstract.split("\n\n") if p.strip()
    )
    parts.append(f'<article><h3><a href="talks/{t["_slug"]}.html">{title}</a></h3><p><i>{meta}</i></p>{paras}</article>')

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
            <li><a href="../docs/">Documents</a></li>
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

# ---- One page per talk ----
TALK_PAGE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} &middot; {name}</title>

    <link href="../../style.css" rel="stylesheet" type="text/css" media="all">
    <style>
      .body {{ max-width: 42rem; line-height: 1.5; }}
    </style>
  </head>

  <body>
    <div class="menu">
        <ul>
            <li><a href="../../index.html">Home</a></li>
            <li><a href="../index.html">Seminar</a></li>
            <li><a href="../../travel-grant.html">Travel Grant</a></li>
            <li><a href="../../docs/">Documents</a></li>
            <li><a href="../../contact.html">Contact</a></li>
        </ul>
    </div>
    <div class="body">
<p><a href="../index.html">&larr; All talks</a></p>
<h1>{title}</h1>
<p><b>Speaker:</b> {speaker}<br>
<b>Date:</b> {date}<br>
<b>Location:</b> {location}<br>
<b>Time:</b> {time}</p>
{abstract}
    </div>
  </body>
</html>
"""

os.makedirs("seminar/talks", exist_ok=True)
# Remove all old talk pages first, so every build starts fresh and
# deleted/renamed talks don't leave stale pages behind.
for old in glob.glob("seminar/talks/*.html"):
    os.remove(old)

for t in talks:
    abstract = t.get("abstract") or ""
    paras = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>"
        for p in abstract.split("\n\n") if p.strip()
    ) or "<p><i>Abstract TBA.</i></p>"
    talk_page = TALK_PAGE.format(
        title=html.escape(t.get("title") or "TBA"),
        name=name,
        speaker=html.escape(t["speaker"]),
        date=nice_date(t["date"]),
        location=html.escape(str(info.get("location") or "TBA")),
        time=html.escape(str(info.get("time") or "TBA")),
        abstract=paras,
    )
    with open(f'seminar/talks/{t["_slug"]}.html', "w", encoding="utf-8") as f:
        f.write(talk_page)
