"""Builds the Our Family Presents umbrella site.

python3 src/build.py  ->  dist/  (published to GitHub Pages by .github/workflows/pages.yml)
The brands and their status live in BRANDS below; change a brand's status there when its site opens.
"""
import hashlib, json, shutil
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DOMAIN = "www.ourfamilypresents.com"
SITE = f"https://{DOMAIN}"
EMAIL = "hello@familyboardbooks.com"
FORM = f"https://formsubmit.co/ajax/{EMAIL}"

# status: "live" (open for orders or reservations), "soon" (site up, waitlist open), "planned" (no site yet)
BRANDS = [
    {"key": "boardbooks", "name": "Family Board Books", "url": "https://www.familyboardbooks.com",
     "domain": "familyboardbooks.com", "status": "live", "colour": "red", "icon": "board", "ages": "Ages 0 to 4",
     "text": "Sturdy little board books starring your family: ABC, numbers, colours, feelings and more, with everyone drawn as a cartoon.",
     "cta": "Visit Family Board Books"},
    {"key": "storybooks", "name": "Family Storybooks", "url": "https://www.familystorybooks.co.uk",
     "domain": "familystorybooks.co.uk", "status": "soon", "colour": "sky", "icon": "story", "ages": "Ages 3 to 7",
     "text": "Classic fairy tales retold with your family as the characters, as hardcover picture books. Little Red Riding Hood, Goldilocks and more.",
     "cta": "Visit Family Storybooks"},
    {"key": "learntoread", "name": "Family Learn to Read", "url": "https://www.familylearntoread.com", "cta": "Visit Family Learn to Read",
     "domain": "familylearntoread.com", "status": "soon", "colour": "leaf", "icon": "read", "ages": "Ages 4 and up",
     "text": "Phonics and early reading books that grow with your child, stage by stage, with their own family in every story."},
    {"key": "calendars", "name": "Family Photo Calendars", "url": "https://www.familyphotocalendars.com",
     "domain": "familyphotocalendars.com", "status": "soon", "colour": "orange", "icon": "calendar", "ages": "For the whole family",
     "text": "A4 and A5 wall calendars from your family photos: as they are, as cartoons or somewhere new like Paris, with birthdays and special days marked.",
     "cta": "Visit Family Photo Calendars"},
    {"key": "jigsaws", "name": "Family Jigsaw Puzzles", "url": "https://www.familyjigsawpuzzles.com",
     "domain": "familyjigsawpuzzles.com", "status": "soon", "colour": "grape", "icon": "puzzle", "ages": "All ages",
     "text": "Your family photo as a jigsaw, as it is, as a cartoon or somewhere new like Paris. From 30 chunky pieces to 1,000, in cardboard or wood.",
     "cta": "Visit Family Jigsaw Puzzles"},
]
STATUS = {"live": "Open now", "soon": "Opening soon", "planned": "Coming later"}

FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Figtree:wght@400;500;600;700&display=swap"

# A gift box in the group's colours (our own drawing).
MARK = """<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="13" width="26" height="16" rx="3" fill="#16A6E3"/><rect x="2" y="9" width="28" height="6" rx="2.5" fill="#EE4B2B"/><rect x="14" y="9" width="4" height="20" fill="#FFC21A"/><path d="M16 9c-3-5-9-6-9-2s5 2 9 2zM16 9c3-5 9-6 9-2s-5 2-9 2z" fill="#1FB45A"/></svg>"""
FAVICON = MARK.replace('class="mark" ', 'xmlns="http://www.w3.org/2000/svg" ').replace(' aria-hidden="true"', "")

ICONS = {
    "board": '<rect x="18" y="20" width="64" height="62" rx="10" fill="var(--c)"/><rect x="24" y="26" width="52" height="50" rx="6" fill="#fff"/><text x="50" y="64" text-anchor="middle" font-family="Bricolage Grotesque, sans-serif" font-weight="800" font-size="34" fill="var(--c)">Aa</text>',
    "story": '<path d="M50 28C40 20 22 20 12 23v52c10-3 28-3 38 5z" fill="var(--c)"/><path d="M50 28c10-8 28-8 38-5v52c-10-3-28-3-38 5z" fill="var(--c)" opacity=".75"/><path d="M50 28v52" stroke="#fff" stroke-width="2"/><circle cx="31" cy="44" r="6" fill="#fff"/><path d="M21 64c3-8 17-8 20 0z" fill="#fff"/><path d="M60 42h18M60 50h18M60 58h12" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
    "read": '<rect x="22" y="18" width="56" height="66" rx="8" fill="var(--c)"/><rect x="28" y="24" width="44" height="54" rx="4" fill="#fff"/><text x="50" y="50" text-anchor="middle" font-family="Bricolage Grotesque, sans-serif" font-weight="800" font-size="20" fill="var(--c)">sh</text><path d="M36 60h28M36 68h18" stroke="var(--c)" stroke-width="3" stroke-linecap="round" opacity=".5"/>',
    "calendar": '<rect x="16" y="24" width="68" height="60" rx="8" fill="var(--c)"/><rect x="22" y="38" width="56" height="40" rx="4" fill="#fff"/><path d="M32 18v12M68 18v12" stroke="var(--ink)" stroke-width="5" stroke-linecap="round"/>' + "".join(f'<rect x="{28 + c * 12}" y="{44 + r * 11}" width="8" height="7" rx="2" fill="var(--c)" opacity="{".9" if (r, c) == (1, 2) else ".3"}"/>' for r in range(3) for c in range(4)),
    "puzzle": '<path d="M20 22h22a8 8 0 1 1 16 0h22v22a8 8 0 1 0 0 16v22H58a8 8 0 1 0-16 0H20V60a8 8 0 1 1 0-16z" fill="var(--c)"/><circle cx="50" cy="52" r="10" fill="#fff" opacity=".9"/>',
}


def v(rel):
    h = hashlib.sha1((ROOT / "assets" / rel).read_bytes()).hexdigest()[:8]
    return f"assets/{rel}?v={h}"


def page(path, title, desc, body):
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{path}">
<link rel="canonical" href="{SITE}/{path}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{v("css/site.css")}">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Our Family Presents", "url": SITE, "email": EMAIL, "brand": [{"@type": "Brand", "name": b["name"], **({"url": b["url"]} if b.get("url") else {})} for b in BRANDS]})}</script>
</head>
<body>
<header class="site-head"><div class="wrap">
<a class="logo" href="index.html" aria-label="Our Family Presents home">{MARK}<span>Our Family Presents</span></a>
<nav class="nav" aria-label="Main"><a href="index.html#brands">Our brands</a><a href="index.html#how">How it works</a><a href="index.html#photos">Your photos</a><a href="index.html#contact">Contact</a></nav>
<a class="btn btn-sm red" href="index.html#news">Get launch news</a>
</div></header>
<main>
{body}
</main>
<footer class="site-foot"><div class="wrap foot-grid">
<div class="foot-about"><a class="logo" href="index.html">{MARK}<span>Our Family Presents</span></a>
<p class="small">Personalised books, puzzles and calendars that star your children and the people they love.</p></div>
<div class="foot-cols">
<div><h3 class="foot-h">Our brands</h3><ul class="foot-links">{"".join(f'<li><a href="{b["url"]}">{e(b["name"])}</a></li>' if b.get("url") else f'<li><span>{e(b["name"])}</span> <span class="tag">soon</span></li>' for b in BRANDS)}</ul></div>
<div><h3 class="foot-h">Help</h3><ul class="foot-links"><li><a href="index.html#how">How it works</a></li><li><a href="index.html#photos">Your photos</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
</div>
<p class="small copy">&copy; <span data-year>2026</span> Our Family Presents &middot; ourfamilypresents.com</p>
</div></footer>
<script>window.OFP={{form:{json.dumps(FORM)},email:{json.dumps(EMAIL)}}};</script>
<script src="{v("js/site.js")}"></script>
</body>
</html>
"""


def card(b):
    icon = f'<svg viewBox="0 0 100 100" aria-hidden="true">{ICONS[b["icon"]]}</svg>'
    head = f'<div class="brand-top"><span class="pill s-{b["status"]}">{STATUS[b["status"]]}</span><span class="ages">{e(b["ages"])}</span></div>'
    if b.get("url"):
        foot = f'<a class="btn btn-sm" href="{b["url"]}">{e(b["cta"])}<span aria-hidden="true">&rarr;</span></a><span class="dom">{e(b["domain"])}</span>'
    else:
        foot = f'<a class="btn btn-sm ghost" href="#news" data-brand="{b["key"]}">Tell me when it opens</a><span class="dom">{e(b["domain"])}</span>'
    return f'<article class="brand c-{b["colour"]}"><div class="brand-art">{icon}</div>{head}<h3>{e(b["name"])}</h3><p>{e(b["text"])}</p><div class="brand-foot">{foot}</div></article>'


def index():
    cards = "".join(card(b) for b in BRANDS)
    choices = "".join(f'<label class="chk"><input type="checkbox" name="brands" value="{e(b["name"])}"{" checked" if b["status"] != "live" else ""} data-key="{b["key"]}"><span>{e(b["name"])}</span></label>' for b in BRANDS)
    steps = [
        ("1", "Add a few photos", "A clear photo of each person, and the family pet if you like. Our guide shows what works best."),
        ("2", "We draw your family", "Everyone becomes a friendly cartoon character, in the style you choose."),
        ("3", "See it free, then order", "Look at a free preview before you pay anything. We print and post it to you."),
    ]
    step_html = "".join(f'<li class="step"><span class="num">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for n, t, d in steps)
    body = f"""<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<p class="eyebrow">Personalised presents for families</p>
<h1>Presents that star <span class="hl">your family</span></h1>
<p class="lede">Books, puzzles and calendars where your children and the people they love are the heroes. We turn your photos into cartoon characters, and you see a free preview before you order.</p>
<div class="hero-cta"><a class="btn red" href="#brands">See our brands</a><a class="btn ghost" href="#how">How it works</a></div>
</div>
<div class="hero-art" aria-hidden="true">{"".join(f'<div class="tile c-{b["colour"]}"><svg viewBox="0 0 100 100">{ICONS[b["icon"]]}</svg></div>' for b in BRANDS)}</div>
</div></section>

<section class="section" id="brands"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Our brands</p><h2>One family, five ways to make them smile</h2>
<p class="lede">Each brand has its own shop, all made by the same small team with the same care for your photos.</p></div>
<div class="brands">{cards}</div>
</div></section>

<section class="section alt" id="how"><div class="wrap">
<div class="sec-head"><p class="eyebrow">How it works</p><h2>From your photos to a present in three steps</h2></div>
<ol class="steps">{step_html}</ol>
</div></section>

<section class="section" id="photos"><div class="wrap split">
<div class="sec-head"><p class="eyebrow">Your photos</p><h2>Your photos stay private</h2>
<p class="lede">We use your photos only to draw your family's characters. They are never shown on our websites or used in our adverts.</p></div>
<ul class="ticks">
<li>Stored privately and encrypted, in the EU.</li>
<li>Unordered previews are deleted after 14 days.</li>
<li>Original photos are deleted once your order has been printed.</li>
<li>You can delete everything yourself at any time.</li>
</ul>
</div></section>

<section class="section" id="news"><div class="wrap">
<div class="band">
<div class="band-copy"><h2>Hear when new presents open</h2>
<p>Tell us which brands you'd like to hear about. We'll email you when they open, with a founding-family discount. No other emails.</p></div>
<form class="signup" data-signup novalidate>
<fieldset><legend>I'd like to hear about</legend><div class="chks">{choices}</div></fieldset>
<div class="form-row"><label class="field"><span>Email</span><input type="email" name="email" id="n-email" autocomplete="email" placeholder="name@example.com" required></label>
<button class="btn red" type="submit">Keep me posted</button></div>
<input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
<p class="form-msg" role="status"></p>
</form>
</div>
</div></section>

<section class="section contact" id="contact"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Contact</p><h2>Questions? Just ask.</h2>
<p class="lede">Email <a href="mailto:{EMAIL}">{EMAIL}</a> and a real person will reply, usually within a working day.</p></div>
</div></section>"""
    return page("", "Our Family Presents: personalised books, puzzles and calendars starring your family",
                "Personalised board books, storybooks, learn-to-read books, photo calendars and jigsaw puzzles where your own family are the cartoon stars. See a free preview before you order.", body)


def not_found():
    body = """<section class="section"><div class="wrap sec-head"><p class="eyebrow">Page not found</p><h1>Sorry, that page isn't here</h1>
<p class="lede">It may have moved. Have a look at <a href="index.html#brands">our brands</a> instead.</p></div></section>"""
    return page("404.html", "Page not found | Our Family Presents", "This page could not be found.", body).replace('href="index.html', 'href="/index.html').replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    (DIST / "assets/favicon.svg").write_text(FAVICON)
    (DIST / "index.html").write_text(index())
    (DIST / "404.html").write_text(not_found())
    (DIST / "CNAME").write_text(DOMAIN + "\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc></url></urlset>\n')
    print("Built", DIST)


if __name__ == "__main__":
    main()
