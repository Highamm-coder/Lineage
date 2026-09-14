"""Build the Lineage web app: every page in views.py, plus data/people.json for the person dialog.

    cd pipeline && python3 site.py

Reads cached data in pipeline/data/, writes HTML pages to the project root and data/people.json.
Styles and behaviour live in assets/ and are never written by this script.
"""
import html, json, os, re, urllib.parse
import figures, views
from worldevents import assign_events

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data"); ROOT = os.path.dirname(HERE)
W = "https://en.wikipedia.org/wiki/"
esc = lambda s: html.escape(str(s or ""), quote=True)
load = lambda f: json.load(open(os.path.join(D, f), encoding="utf-8"))
LINES, MAIN_LINKS, FAM_LINKS = load("lines.json"), load("holder_links.json"), load("family_links.json")
BIOS, LIFE, SLUGS = load("bios_raw.json"), load("life.json"), load("holder_slugs.json")

def ordinal(n):
    n = int(n); return "%d%s" % (n, "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
def century(y): return (int(y) - 1) // 100 + 1
def cent_label(c): return "%s c." % ordinal(c)
def endyear(s, e): return 2026 if e == "present" else (e if isinstance(e, int) and e >= s else s)

GREEK = {"Photius I": "Photios I", "Gennadius II": "Gennadius Scholarius", "Cyril I": "Cyril Lucaris",
         "John IV": "John IV the Faster", "Michael I": "Michael I Cerularius"}
def clean_name(col, n):
    n = re.sub(r"\s*\[[a-z]{2,3}\]", "", n)
    n = re.sub(r"^(St\.?|Saint|Bl\.?|Cardinal|Pope|Patriarch|Abune|Mor|Mar)\s+", "", n)
    n = re.sub(r"\s+\b(OSB|OFM|OP|OCist|OCarm|OSA|OBE)\b", "", n).strip()
    return GREEK.get(n, n) if col["id"] == "orthodox" else n

def plausible(title, row):
    """Drop a link whose Wikidata lifespan cannot contain the tenure (catches name-matching mistakes)."""
    b = BIOS.get(title.replace("_", " ")) or {}
    L = LIFE.get(b.get("qid"), {}) if b.get("qid") else {}
    s = row["start"]
    if L.get("b") is not None and L["b"] > s - 12: return False
    if L.get("d") is not None and L["d"] < s: return False
    return True

def link_for(col, i):
    src = MAIN_LINKS if col.get("links") == "main" else FAM_LINKS
    v = src.get(col["key"], [])
    t = v[i] if i < len(v) else None
    if not t: return None
    t = urllib.parse.unquote(t).replace(" ", "_")
    if col.get("links") != "main" and not plausible(t, LINES[col["key"]]["rows"][i]): return None
    return t

def seal(name):
    w = [x for x in re.sub(r"&[a-z]+;|\bof\b|\bthe\b|^St\.? ", " ", name).split() if x]
    return (w[0][:2] if len(w) == 1 else "".join(x[0] for x in w[:2])).upper() if w else "?"

def img_path(slug):
    if not slug: return None
    for folder in ("landmarks", "holders"):
        if os.path.exists(os.path.join(ROOT, "img", folder, slug + ".jpg")): return "img/%s/%s.jpg" % (folder, slug)
    return None

# ============================================================ people
PEOPLE = {}          # pid -> record used by the dialog
def person(pid, **kw):
    p = PEOPLE.setdefault(pid, {"terms": [], "cards": {}})
    for k, v in kw.items():
        if v is not None and not p.get(k): p[k] = v
    return p

def bio_of(title):
    if not title: return {}
    return BIOS.get(title.replace("_", " ")) or BIOS.get(urllib.parse.unquote(title).replace("_", " ")) or {}

def trim_bio(t, limit=560):
    t = re.sub(r"\s+", " ", t or "").strip()
    if not t: return ""
    abbr = {"st", "sts", "c", "ca", "fl", "r", "b", "d", "dr", "mr", "mrs", "rev", "jr", "sr", "vs", "no", "ie", "eg", "bc", "ad", "mt"}
    out, cur = [], ""
    for tok in re.split(r"(\s+)", t):
        cur += tok
        if re.search(r"[.!?]$", tok):
            wd = re.sub(r"[^A-Za-z]", "", tok).lower()
            if wd in abbr or (len(wd) == 1 and tok[:-1].isupper()): continue
            out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    out[0] = re.sub(r"\s*\([^()]*\)", "", re.sub(r"\s*\([^()]*\)", "", out[0])).replace(" ,", ",")
    res = ""
    for s in out:
        if len(res) + len(s) + 1 > limit and res: break
        res = (res + " " + s).strip()
    return res

# ============================================================ one column's entries
def auto_cards(col, rows):
    """Pick about 8 figures for a family column: the first holder, the current holder, and portrait-bearing
    holders spread one per century in between."""
    idx = list(range(len(rows)))
    if not idx: return set()
    pick = {idx[0], idx[-1]}
    by_c = {}
    for i in idx:
        t = link_for(col, i)
        if t and (bio_of(t).get("thumb")): by_c.setdefault(century(rows[i]["start"]), []).append(i)
    cs = sorted(by_c)
    budget = 6
    step = max(1, len(cs) // budget) if cs else 1
    for c in cs[::step][:budget]:
        pick.add(by_c[c][len(by_c[c]) // 2])
    return pick

RESTATES = re.compile(r"\b(patriarch|primate|metropolitan|catholicos|abuna|pope|head of the|presiding bishop|bishop|archbishop|"
                      r"from \d{3,4}|since \d{3,4}|\d{1,2}(st|nd|rd|th)[- ]century|incumbent)\b", re.I)
def card_bio(title, fallback):
    """Use Wikipedia's short description only when it says something the card doesn't already say."""
    d = re.sub(r"\s*\([^)]*\)", "", bio_of(title).get("desc", "")).strip().rstrip(".")
    if not d or RESTATES.search(d) or len(d) > 40: return fallback
    return d[0].upper() + d[1:] + "."

def entries_for(col, view):
    out = []
    pidp = col["id"]
    if col["key"]:
        rows = LINES[col["key"]]["rows"]
        curated = {}
        if col["cards"] == "curated":
            for card in figures.COLS[col["id"]]:
                name, meta, bio, s, e, slug, wiki = card
                m = re.search(r"(\d+)(st|nd|rd|th)\s*$", re.sub(r"&[a-z]+;", " ", meta))
                best = None
                for i, r in enumerate(rows):
                    if col["numbered"] and m:
                        if r["num"] == m.group(1): best = i; break
                    elif clean_name(col, r["name"]).split(" (")[0] == name and (best is None or abs(r["start"] - s) < abs(rows[best]["start"] - s)):
                        best = i
                curated[best if best is not None else ("x", wiki)] = card
            picks = set()
        else:
            picks = auto_cards(col, rows)
        seen = {}
        for i, r in enumerate(rows):
            if re.match(r"^(seat vacant|vacant|sede vacante|interregnum)", r["name"], re.I): continue
            base = clean_name(col, r["name"]).replace(" (again)", "")
            seen[base] = seen.get(base, 0) + 1
            title = link_for(col, i)
            pid = "%s:%s" % (pidp, title or "name:%s:%d" % (r["name"], r["start"]))
            num = ordinal(r["num"]) if (col["numbered"] and str(r["num"]).isdigit()) else ""
            p = person(pid, col=pidp, name=base, wiki=title, office=col["office"], line=col["line"])
            if [r["start"], r["end"], num] not in p["terms"]: p["terms"].append([r["start"], r["end"], num])
            circa = "c. " if (pidp == "catholic" and r["start"] < 250) else ""
            if r["end"] == "present": dt = "%s%d&ndash;" % (circa, r["start"])
            elif isinstance(r["end"], int) and r["end"] > r["start"]: dt = "%s%d&ndash;%s%d" % (circa, r["start"], circa, r["end"])
            else: dt = "%s%d" % (circa, r["start"])
            meta = dt + (" &middot; " + num if num else "")
            if i in curated or i in picks:
                if i in curated:
                    card = curated[i]
                else:
                    slug = SLUGS.get((title or "").replace("_", " "))
                    bio = (col["office"] + ".") if col.get("plain_bio") else card_bio(title, col["office"] + ".")
                    card = (base, meta, bio, r["start"], endyear(r["start"], r["end"]), slug, title or "")
                p["cards"][view] = card
                out.append({"kind": "card", "year": card[3], "end": card[4], "card": card, "pid": pid})
                continue
            nm = base + (" (restored)" if "(again)" in r["name"] else (" (%s term)" % ordinal(seen[base]) if seen[base] > 1 and not col["numbered"] else ""))
            out.append({"kind": "holder", "year": r["start"], "end": endyear(r["start"], r["end"]), "name": nm, "meta": meta,
                        "href": title, "pid": pid})
        for k, card in curated.items():                 # curated figures not in the register (St Andrew)
            if isinstance(k, tuple):
                pid = "%s:%s" % (pidp, card[6])
                p = person(pid, col=pidp, name=card[0], wiki=card[6], office=col["office"], line=col["line"])
                p["cards"][view] = card; p["founder_of_see"] = True
                out.append({"kind": "card", "year": card[3], "end": card[4], "card": card, "pid": pid})
    else:
        for card in col["cards"]:
            pid = "%s:%s" % (pidp, card[6])
            p = person(pid, col=pidp, name=re.sub(r"&[a-z]+;", "e", card[0]), wiki=card[6], office="", line=col["line"])
            p["cards"][view] = card; p["act"] = card[3]
            out.append({"kind": "card", "year": card[3], "end": card[4], "card": card, "pid": pid})
    for cid, cards in (view_cfg(view).get("extra_cards") or {}).items():
        if cid == col["id"]:
            for card in cards:
                pid = "%s:%s" % (pidp, card[6])
                p = person(pid, col=pidp, name=card[0], wiki=card[6], office="", line=col["line"])
                p["cards"][view] = card
                if [card[3], card[4], ""] not in p["terms"]: p["terms"].append([card[3], card[4], ""])
                out.append({"kind": "card", "year": card[3], "end": card[4], "card": card, "pid": pid})
    return out

def view_cfg(v): return views.VIEWS[v]
PAGE_OF = {"root": "index.html"}   # line id -> the page that shows it (filled while rendering)

def asset_version(rel):
    """A short content hash, so browsers fetch CSS/JS again whenever they change."""
    import hashlib
    return hashlib.sha1(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]

# ============================================================ site nav (every page)
CHEVRON = '<svg class="nav__chev" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg>'
SEARCH_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.75"/><path d="M13 13l4.5 4.5"/></svg>'
THEME_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.25"/><path d="M10 2.75a7.25 7.25 0 0 1 0 14.5z"/></svg>'
# Site-wide facts shown in the footer and legal pages. Fill the None values before publishing;
# until then the pages show a visible "to be confirmed" marker.
SITE = dict(url=None, name="Lineage of the Church", builder="MAE Online", builder_url=None, owner=None,
            email=None, jurisdiction=None, host=None, updated="14 September 2026")
DEFAULT_DESC = "Catholic, Anglican and Orthodox lines of succession from the apostles to today, aligned by century."
def head_meta(desc=DEFAULT_DESC, title=None, image=None):
    """Description plus Open Graph tags. Social sites need absolute image URLs: set SITE["url"] before publishing."""
    base = (SITE["url"] or "").rstrip("/") + "/" if SITE["url"] else ""
    out = ['<meta name="description" content="%s">' % desc, '<meta property="og:site_name" content="%s">' % SITE["name"],
           '<meta property="og:description" content="%s">' % desc]
    if title: out.append('<meta property="og:title" content="%s">' % title)
    if image: out += ['<meta property="og:image" content="%s%s">' % (base, image), '<meta name="twitter:card" content="summary_large_image">']
    return "\n".join(out)

def tbc(v, what): return v if v else '<mark class="tbc">[%s to be confirmed]</mark>' % what

def footer_html():
    fams = []
    for _, year, _, page, _ in views.RINGS:
        cfg = next(c for c in views.VIEWS.values() if c["file"] == page)
        fams.append('<li><a href="%s">%s</a></li>' % (page, re.sub(r" churches", "", cfg["title"])))
    builder = ('<a href="%s" rel="noopener">%s</a>' % (SITE["builder_url"], SITE["builder"])) if SITE["builder_url"] else SITE["builder"]
    return ('<footer class="sf"><div class="sf__in">'
            '<div class="sf__brand"><a class="sf__name" href="index.html">%s</a>'
            '<p>Every archbishop, pope and patriarch, side by side, century by century.</p></div>'
            '<nav class="sf__cols" aria-label="Footer">'
            '<div><h2>Explore</h2><ul><li><a href="index.html#chart">The three churches</a></li><li><a href="line.html">Follow the line back</a></li>%s</ul></div>'
            '<div><h2>The site</h2><ul><li><a href="about.html">About</a></li><li><a href="terms.html">Terms &amp; conditions</a></li>'
            '<li><a href="privacy.html">Privacy policy</a></li></ul></div></nav>'
            '<div class="sf__base"><p>Text from Wikipedia, under <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">CC BY-SA 4.0</a>. '
            'Not an official publication of any church.</p><p>Site built by %s</p></div>'
            '</div></footer>' % (SITE["name"], "".join(fams), builder))

def nav_html(current):
    fams = []
    for _, year, _, page, _ in views.RINGS:
        cfg = next(c for c in views.VIEWS.values() if c["file"] == page)
        subs = [(v["title"], page.replace(".html", "-%s.html" % k)) for k, v in (cfg.get("variants") or {}).items()]
        cur = lambda f: ' aria-current="page"' if f == current else ""
        sub = ('<ul class="menu__sub">%s</ul>' % "".join('<li><a href="%s"%s>%s</a></li>' % (f, cur(f), t) for t, f in subs)) if subs else ""
        name = re.sub(r" churches", "", cfg["title"])
        fams.append('<li><a href="%s"%s><span class="menu__y">%d</span>%s</a>%s</li>' % (page, cur(page), year, name, sub))
    home = "#chart" if current == "index.html" else "index.html#chart"
    return ('<a class="skip" href="#chart">Skip to the chart</a>'
            '<header class="nav%s" id="nav"><div class="nav__in">'
            '<a class="nav__brand" href="index.html"%s><span class="nav__full">Lineage of the Church</span><span class="nav__short">Lineage</span></a>'
            '<nav class="nav__links" aria-label="Site">'
            '<button class="nav__search" id="searchbtn" type="button" aria-haspopup="dialog" aria-controls="sx">%s<span class="nav__slabel">Search</span></button>'
            '<div class="menu"><button class="nav__btn" id="menubtn" type="button" aria-expanded="false" aria-controls="menu">Churches %s</button>'
            '<div class="menu__panel" id="menu" hidden>'
            '<a class="menu__main" href="%s"%s>The three churches<span>Anglican &middot; Catholic &middot; Orthodox</span></a>'
            '<a class="menu__main menu__main--line" href="line.html">Follow the line back<span>Anyone&rsquo;s office, back to its founding</span></a>'
            '<p class="menu__lab">Families of churches</p><ul class="menu__fams">%s</ul></div></div>'
            '<a class="nav__a" href="about.html"%s>About</a>'
            '<button class="nav__theme" id="themebtn" type="button" aria-label="Switch colour theme">%s</button>'
            '</nav></div></header>'
            '<dialog class="sx" id="sx" aria-label="Search people">'
            '<div class="sx__bar">%s<input id="sx-q" type="search" autocomplete="off" spellcheck="false" '
            'placeholder="Search a name, office or year" aria-label="Search a name, office or year" aria-controls="sx-res">'
            '<button class="sx__x" type="button" data-sx-close>Close</button></div>'
            '<p class="sx__hint" id="sx-status" aria-live="polite">Try &ldquo;Becket&rdquo;, &ldquo;Moscow&rdquo; or a year such as &ldquo;1492&rdquo;.</p>'
            '<ul class="sx__res" id="sx-res" role="listbox"></ul></dialog>'
            % ("", ' aria-current="page"' if current == "index.html" else "", SEARCH_ICON, CHEVRON, home,
               ' aria-current="page"' if current == "index.html" else "", "".join(fams),
               ' aria-current="page"' if current == "about.html" else "", THEME_ICON, SEARCH_ICON))

# ============================================================ render one view
def render(vname, cfg, cols, outfile, chooser=None):
    splits = cfg.get("splits", [])
    split_cent = {century(y): y for y, _ in splits}
    def slot(s, e):
        mid = (s + e) / 2.0
        c = century(round(mid + 0.01))
        return (c, ("a" if mid < split_cent[c] else "b") if c in split_cent else "")

    E = {}
    for col in cols:
        ents = entries_for(col, vname)
        for cid, y, d, t in cfg.get("notes", []):
            if cid == col["id"]: ents.append({"kind": "note", "year": y + 0.5, "end": y, "date": d, "text": t})
        for cid, y, label, page, sent in cfg.get("rings", []):
            if cid == col["id"]: ents.append({"kind": "ring", "year": y, "end": y, "label": label, "page": page})
        for e in ents: e["slot"] = slot(e["year"] if e["kind"] != "card" else e["year"], e["end"] if e["kind"] != "note" else int(e["year"]))
        ents.sort(key=lambda e: (e["year"], {"card": 0, "ring": 1, "holder": 2, "note": 3}[e["kind"]]))
        E[col["id"]] = ents
    VIS = ("card", "ring")
    def items(sk, col): return [e for e in E[col["id"]] if e["slot"] == sk]
    def visible_in(sk): return any(e["kind"] in VIS and e["slot"] == sk for col in cols for e in E[col["id"]])

    since = cfg.get("since", 1)
    seq = []
    for c in range(since, 22):
        for h in (["a", "b"] if c in split_cent else [""]):
            seq.append((c, h))
            if c in split_cent and h == "a": seq.append(("split", split_cent[c]))
    ROWS, gap = [], []
    def flush():
        if not gap: return
        a, b = gap[0][0], gap[-1][0]
        gid = "g%d-%d" % (a, b)
        lab = cent_label(a) if a == b else "%s&ndash;%s c." % (ordinal(a), ordinal(b))
        if len(gap) == 1: ROWS.append(dict(kind="cent", sk=gap[0], group=gid, visible=True, label=lab, gapsingle=True))
        else:
            ROWS.append(dict(kind="gaplabel", group=gid, visible=True, label=lab))
            for sk in gap: ROWS.append(dict(kind="cent", sk=sk, group=gid, visible=False, label=cent_label(sk[0])))
        gap.clear()
    for s in seq:
        if s[0] == "split": flush(); ROWS.append(dict(kind="split", year=s[1])); continue
        c, h = s
        if visible_in(s) or (h == "b" and visible_in((c, "a"))):
            flush(); ROWS.append(dict(kind="cent", sk=s, group="c%d" % c, visible=visible_in(s), label="" if h == "b" else cent_label(c)))
        elif h == "b": continue
        else: gap.append(s)
    flush()
    GROUPS = {}
    for i, r in enumerate(ROWS):
        if "group" in r: GROUPS.setdefault(r["group"], []).append(i)
    def hidden_count(g):
        return sum(1 for i in GROUPS[g] if ROWS[i]["kind"] == "cent" for col in cols for e in items(ROWS[i]["sk"], col) if e["kind"] == "holder")
    def gtitle(g):
        if g.startswith("c"): return "%s century" % ordinal(int(g[1:]))
        a, b = g[1:].split("-")
        return "%s century" % ordinal(int(a)) if a == b else "%s and %s centuries" % (ordinal(int(a)), ordinal(int(b)))
    LABELS = {}
    for r in ROWS:
        if r.get("group") and r["group"] not in LABELS and r.get("label"): LABELS[r["group"]] = r["label"]
    def has_vis(i, col): return ROWS[i]["kind"] == "cent" and any(e["kind"] in VIS for e in items(ROWS[i]["sk"], col))
    FIRST, LAST = {}, {}
    for col in cols:
        vis = [i for i in range(len(ROWS)) if has_vis(i, col)]
        FIRST[col["id"]], LAST[col["id"]] = (min(vis), max(vis)) if vis else (10 ** 6, -1)
    aug = None
    if vname == "main":
        aug = next((i for i in range(len(ROWS)) if ROWS[i]["kind"] == "cent" and any(e["kind"] == "card" and e["card"][0] == "Augustine" for e in items(ROWS[i]["sk"], cols[0]))), None)

    def hue(col): return col.get("hue", col["id"])
    def pic(slug, name, size=56):
        p = img_path(slug)
        if p: return '<span class="pic"><img src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async"></span>' % (p, size, size)
        return '<span class="pic pic--mono"><span>%s</span></span>' % esc(seal(name))
    def card_html(e, cls="", see=None):
        name, meta, bio, s, en, slug, wiki = e["card"]
        if see == "Constantinople" and (s is None or s < 330): see = "Byzantium"   # the city was renamed in 330
        m = ("%s &middot; %s" % (see, meta)) if see else meta
        klass = "mcard" if see else "card " + cls
        return ('<a class="%s" data-p="%s" href="%s%s" target="_blank" rel="noopener">%s<span class="txt"><span class="nm">%s</span>'
                '<span class="mt">%s</span><span class="bio">%s</span></span></a>' % (klass, esc(e["pid"]), W, wiki, pic(slug, name), name, m, bio))
    def hpic(pid, name):
        slug = SLUGS.get((PEOPLE.get(pid, {}).get("wiki") or "").replace("_", " "))
        p = img_path(slug)
        if p: return '<span class="hp"><img src="%s" alt="" width="26" height="26" loading="lazy" decoding="async"></span>' % p
        return '<span class="hp hp--seal" aria-hidden="true"><span>%s</span></span>' % esc(seal(name))
    def holder_html(e, see=None):
        meta = ("%s &middot; %s" % (see, e["meta"])) if see else e["meta"]
        inner = '%s<span class="hn">%s</span><span class="hdt">%s</span>' % (hpic(e["pid"], e["name"]), esc(e["name"]), meta)
        if e["href"]: return '<a class="h" data-p="%s" href="%s%s" target="_blank" rel="noopener">%s</a>' % (esc(e["pid"]), W, e["href"], inner)
        return '<button class="h h--btn" type="button" data-p="%s">%s</button>' % (esc(e["pid"]), inner)
    def note_html(e, see=None):
        d = ('<span class="nd">%s</span> &middot; ' % e["date"]) if e["date"] else ""
        return '<p class="note">%s%s<i>%s</i></p>' % (("%s &middot; " % see) if see else "", d, e["text"])
    RING_SVG = '<svg class="ring__o" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="11" pathLength="16"/></svg>'
    # Jesus is named above the lines as the origin all three claim, not drawn as a node in the chain
    ORIGIN = ('<p class="origin__t">All three trace themselves to <a class="origin__j" data-p="root:Jesus" href="%sJesus" target="_blank" rel="noopener">'
              'Jesus of Nazareth</a> <span class="origin__d">(%s)</span> and his apostles.</p>'
              '<p class="origin__hint"><span class="k-click">Click</span><span class="k-tap">Tap</span> anyone for their story '
              '<span class="mast__dot" aria-hidden="true">&middot;</span> <b class="mast__more">+ more</b> shows everyone in a century '
              '<span class="mast__dot" aria-hidden="true">&middot;</span> %s<span class="vh">A dotted circle</span> opens a family of churches</p>'
              % (W, figures.JESUS[1], RING_SVG.replace('class="ring__o"', 'class="ring__o mast__ring"')))
    def ring_html(e, see=None):
        rid = "ring-" + e["page"].replace(".html", "")
        return ('<a class="ring%s" id="%s%s" href="%s">%s<span class="ring__t"><span class="ring__n">%s <span class="ring__y">&middot; %d</span></span>'
                '<span class="ring__go">Explore the family &rsaquo;</span></span></a>'
                % (" ring--m" if see else "", "m-" if see else "", rid, e["page"], RING_SVG, e["label"], e["year"]))
    def toggle(g, where="top"):
        n = hidden_count(g)
        if where == "bot":
            return '<button class="tg tg--bot" type="button" data-toggle="%s" data-bot="1" hidden>&minus; hide</button>' % g if n else ""
        if not n: return '<span class="sublab">%s</span>' % LABELS.get(g, "")
        return ('<button class="tg" type="button" data-toggle="%s" aria-expanded="false" aria-label="Show %d more entries in the %s">'
                '<span class="tg1">%s</span><span class="tg2" data-more="+%d more">+%d more</span></button>' % (g, n, gtitle(g), LABELS.get(g), n, n))
    def cell_content(sk, col, g, row_visible):
        parts, run = [], []
        def close():
            if run:
                parts.append('<div class="run" data-g="%s"%s>%s</div>' % (g, ' hidden="until-found"' if row_visible else "", "".join(run))); run.clear()
        its = items(sk, col)
        for e in its:
            if e["kind"] in VIS:
                close()
                if e["kind"] == "ring": parts.append(ring_html(e)); continue
                cls = []
                if vname == "main" and e["card"][0] == "Augustine": cls.append("c-aug")
                if col.get("spine", True) and e is E[col["id"]][-1]: cls.append("c-last")
                parts.append(card_html(e, " ".join(cls)))
            elif e["kind"] == "holder": run.append(holder_html(e))
            else: run.append(note_html(e))
        close()
        return "".join(parts)

    # ---- desktop grid
    out = []
    if cfg.get("root"):
        out.append('<div class="row row--origin"><div class="gut"></div><div class="cell origin">%s</div></div>' % ORIGIN)
    heads = []
    for k, col in enumerate(cols):
        drop = ""
        extra = ""
        if chooser and k == cfg.get("variant_slot"):
            extra = '<p class="chooser">Or: %s</p>' % " &middot; ".join('<a href="%s">%s</a>' % (f, t) for t, f in chooser)
        ctx = ' <span class="hd__ctx">for context</span>' if col.get("context") else ""
        heads.append('<div class="cell hd%s" style="--c:var(--%s)"><span class="hd__t">%s</span><span class="hd__s">%s%s</span>%s</div>'
                     % (drop, hue(col), col["title"], col["sub"], ctx, extra))
    out.append('<div class="row row--head"><div class="gut"></div>%s</div>' % "".join(heads))
    if since > 1:
        out.append('<div class="row row--before"><div class="gut"><span class="sublab">%s</span></div><div class="cell before">'
                   '<a href="index.html">See the main chart for the centuries before</a></div></div>'
                   % ("1st&ndash;%s c." % ordinal(since - 1)))
    split_text = {y: t for y, t in splits}
    for i, r in enumerate(ROWS):
        if r["kind"] == "split":
            cells = []
            for k, col in enumerate(cols):
                active = col.get("spine", True) and FIRST[col["id"]] <= i <= LAST[col["id"]]
                txt = ""
                if split_text.get(r["year"]) and k == 0: txt = '<p class="split">%s</p>' % split_text[r["year"]]
                if split_text.get(r["year"]) is None and k == 1:
                    ring = next(x for x in cfg["rings"] if x[0] is None and x[1] == r["year"])
                    txt = ('<a class="ring ring--axis" id="ring-%s" href="%s">%s<span class="ring__t"><span class="ring__sent">%s</span>'
                           '<span class="ring__n">%s</span><span class="ring__go">Explore the family &rsaquo;</span></span></a>'
                           % (ring[3].replace(".html", ""), ring[3], RING_SVG, ring[4], ring[2]))
                cells.append('<div class="cell%s" style="--c:var(--%s)">%s</div>' % (" sp" if active else "", hue(col), txt))
            out.append('<div class="row row--split%s" id="y%d"><div class="gut gut--split">%d</div>%s</div>'
                       % (" row--ring" if split_text.get(r["year"]) is None else "", r["year"], r["year"], "".join(cells)))
            continue
        g = r["group"]; grow = GROUPS[g]
        gut = toggle(g) if i == grow[0] else ('<span class="sublab">%s</span>' % r["label"] if not r["visible"] and r["label"] else "")
        if i == grow[-1]: gut += toggle(g, "bot")
        cls = ["row", "row--" + ("gap" if r["kind"] == "gaplabel" or r.get("gapsingle") else "cent")]
        if i == aug: cls.append("row--stub")
        cells = []
        for col in cols:
            active = col.get("spine", True) and FIRST[col["id"]] <= i <= LAST[col["id"]]
            c = ["cell"] + (["sp"] if active else []) + (["sp-first"] if i == FIRST[col["id"]] else []) + (["sp-last"] if i == LAST[col["id"]] else [])
            if i == aug and col["id"] == "catholic": c.append("cell--stubfrom")
            content = "" if r["kind"] == "gaplabel" else cell_content(r["sk"], col, g, r["visible"])
            cells.append('<div class="%s" style="--c:var(--%s)">%s</div>' % (" ".join(c), hue(col), content))
        rid = (' id="%s"' % g) if i == grow[0] else ""
        out.append('<div class="%s"%s data-g="%s"%s%s><div class="gut">%s</div>%s</div>'
                   % (" ".join(cls), rid, g, ' data-row="1"' if not r["visible"] else "", "" if r["visible"] else ' hidden="until-found"', gut, "".join(cells)))
    GRID = "".join(out)

    # ---- mobile list
    m = []
    if cfg.get("root"):
        m.append('<div class="morigin">%s</div>' % ORIGIN)
    done = set()
    for r in ROWS:
        if r["kind"] == "split":
            if split_text.get(r["year"]): m.append('<p class="msplit"><b>%d</b> %s</p>' % (r["year"], split_text[r["year"]]))
            else:
                ring = next(x for x in cfg["rings"] if x[0] is None and x[1] == r["year"])
                m.append('<p class="msplit"><b>%d</b> %s</p>' % (r["year"], ring[4]))
                m.append(ring_html({"page": ring[3], "label": ring[2], "year": ring[1]}, see=True))
            continue
        if r["kind"] == "gaplabel": continue
        g = r["group"]
        if g not in done:
            done.add(g); n = hidden_count(g)
            title = gtitle(g).replace(" and ", "&ndash;").capitalize()
            if n:
                m.append('<h3 class="mcent"><button class="tg tg--m" type="button" data-toggle="%s" aria-expanded="false" '
                         'aria-label="Show %d more entries in the %s"><span class="tg1">%s</span> <span class="tg2" data-more="+%d more">+%d more</span></button></h3>'
                         % (g, n, gtitle(g), title, n, n))
            else:
                m.append('<h3 class="mcent"><span class="tg1">%s</span></h3>' % title)
        its = sorted([(e["year"], col, e) for col in cols for e in items(r["sk"], col)], key=lambda t: t[0])
        run, block = [], []
        def mclose():
            if run: block.append('<div class="run mrun" data-g="%s" hidden="until-found">%s</div>' % (g, "".join(run))); run.clear()
        for _, col, e in its:
            see = col["see"]
            if e["kind"] == "card": mclose(); block.append(card_html(e, see=see).replace('class="mcard"', 'class="mcard" style="--c:var(--%s)"' % hue(col)))
            elif e["kind"] == "ring": mclose(); block.append('<div style="--c:var(--%s)">%s</div>' % (hue(col), ring_html(e, see=see)))
            elif e["kind"] == "holder": run.append('<div class="mh" style="--c:var(--%s)">%s</div>' % (hue(col), holder_html(e, see)))
            else: run.append('<div class="mh" style="--c:var(--%s)">%s</div>' % (hue(col), note_html(e, see)))
        mclose(); m.append("".join(block))
    MOBILE = "".join(m)

    total = sum(len(LINES[c["key"]]["rows"]) for c in cols if c["key"])
    hero = ""
    if vname == "main":
        hero = ('<section class="hero" aria-labelledby="hero-t"><div class="wall" aria-hidden="true"><div class="wall__cols"></div></div>'
                '<div class="hero__in">'
                '<p class="hero__kicker">1,501 leaders in 14 lines of succession. Lists in the order they begin; names newest first.</p>'
                '<h1 class="hero__t" id="hero-t"><span>Every archbishop, pope and patriarch.</span> <span>Side by side, century by century.</span></h1>'
                '<p class="hero__sub">Canterbury, Rome and Constantinople on one shared timeline, and eleven more lines besides. Open anyone to read their story.</p>'
                '<a class="hero__cta" href="#chart">Begin with the apostles <span aria-hidden="true">&darr;</span></a>'
                '<p class="hero__alt"><a href="line.html">or follow one leader&rsquo;s line back</a></p>'
                '<p class="vh">Behind the heading, the names of all 1,501 leaders on this site, list by list.</p></div>'
                '</section>')
        mast = ""
        foot = ('<p>Jesus is named above the three lines as the origin all three claim; he is not drawn into any one of them. Rome sits in the centre column only for layout, not as a claim '
                'the other churches accept: the Orthodox see 1054 as Rome&rsquo;s departure, and Anglicans see 1534 as a reform, not a founding.</p>'
                '<p>Each figure sits in the century, and on the side of 1054 or 1534, in which most of their tenure fell. Source: Wikipedia, September 2026.</p>')
        doc_title = "Lineage of the Church"
    else:
        back = "index.html#ring-%s" % cfg["file"].replace(".html", "")
        mast = ('<header class="mast mast--fam"><a class="mast__crumb" href="%s">&larr; The three churches</a><h1>%s</h1><p>%s</p>'
                '<p class="mast__how">Shown through selected figures%s.</p>%s</header>'
                % (back, cfg["title"], cfg["origin"], "; click &lsquo;+ more&rsquo; beside a century to see every holder" if total else "",
                   ('<p class="mast__choose">Also in this family: %s</p>' % " &middot; ".join('<a href="%s">%s</a>' % (f, t) for t, f in chooser)) if chooser else ""))
        foot = ('<p>Figures are placed in the century in which most of their tenure fell%s. Source: Wikipedia, September 2026.</p>'
                % ("; founders are placed at the year of the act they are known for" if any(not c["key"] for c in cols) else ""))
        doc_title = "%s &middot; Lineage of the Church" % cfg["title"]
    allbtn = ('<p><button id="allbtn" class="allbtn" type="button" aria-expanded="false" data-label="Show every holder (%d entries)">'
              'Show every holder (%d entries)</button></p>' % (total, total)) if total else ""
    doc = TEMPLATE.format(head=head_meta(), v_css=asset_version("assets/css/app.css"), v_js=asset_version("assets/js/app.js"), title=doc_title, body='%s%s<div class="page page--%s">%s<div id="chart" class="chartwrap" tabindex="-1"><main class="chart" aria-label="Lines of succession">%s</main>'
                          '<main class="mlist" aria-label="Lines of succession, in date order">%s</main></div><section class="foot" aria-label="Notes on the chart">%s%s</section></div>%s'
                          % (nav_html(outfile), hero, vname, mast, GRID, MOBILE, foot, allbtn, footer_html()), dialog=DIALOG)
    doc = doc.encode("ascii", "xmlcharrefreplace").decode("ascii")
    open(os.path.join(ROOT, outfile), "w", encoding="ascii").write(doc)
    return len(doc), total

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="assets/css/app.css?v={v_css}">
<script>if ("onbeforematch" in HTMLElement.prototype) document.documentElement.classList.add("uf");
try {{ var t = localStorage.getItem("theme"); if (t) document.documentElement.setAttribute("data-theme", t); }} catch (e) {{}}
try {{ document.documentElement.classList.add(sessionStorage.getItem("heroSeen") || matchMedia("(prefers-reduced-motion: reduce)").matches ? "hero-still" : "hero-play"); }}
catch (e) {{ document.documentElement.classList.add("hero-still"); }}</script>
<script src="assets/js/app.js?v={v_js}" defer></script>
</head>
<body>
{body}
{dialog}
</body>
</html>
"""
DIALOG = ('<dialog class="pm" id="pm" aria-labelledby="pm-name"><div class="pm__in">'
          '<button class="pm__x" type="button" aria-label="Close" data-close>&times;</button>'
          '<div class="pm__top"><div class="pm__pic" id="pm-pic"></div><div><div class="pm__line" id="pm-line"></div>'
          '<h2 class="pm__name" id="pm-name"></h2><div class="pm__office" id="pm-office"></div></div></div>'
          '<dl class="pm__facts" id="pm-facts"></dl><p class="pm__tag" id="pm-tag"></p><p class="pm__bio" id="pm-bio"></p>'
          '<p class="pm__src" id="pm-src"></p>'
          '<p class="pm__trace" id="pm-trace"></p>'
          '<div class="pm__ev" id="pm-ev"><div class="pm__evh">Meanwhile in the world</div><p class="pm__evt" id="pm-evt"></p>'
          '<p class="pm__evr" id="pm-evr"></p></div>'
          '<nav class="pm__nav" aria-label="Along the line"><button type="button" class="pv" id="pm-prev"><small>Before</small><b></b></button>'
          '<button type="button" class="nx" id="pm-next"><small>After</small><b></b></button></nav>'
          '</div></dialog>')

# ============================================================ person dialog data
def yrs(y, circa=False):
    if y is None: return None
    s = ("%d BC" % -y) if y <= 0 else str(y)
    return ("c. " + s) if circa else s

def build_people_json(order):
    person("root:Jesus", col="root", name="Jesus of Nazareth", wiki="Jesus", office="", line="The root of every line")
    J = figures.JESUS
    PEOPLE["root:Jesus"]["cards"]["main"] = (J[0], J[1], J[2], None, None, J[3], J[4])
    # line order for before/after navigation
    prevnext = {}
    for ids in order:
        for a, b in zip(ids, ids[1:]): prevnext.setdefault(a, [None, None])[1] = b; prevnext.setdefault(b, [None, None])[0] = a
    recs = {}
    for pid, p in PEOPLE.items():
        bio = bio_of(p.get("wiki")); q = bio.get("qid"); L = LIFE.get(q, {}) if q else {}
        card = p["cards"].get("main") or next(iter(p["cards"].values()), None)
        name = card[0] if card else p.get("name", "")
        slug = (card[5] if card else None) or SLUGS.get((p.get("wiki") or "").replace("_", " "))
        terms = []
        for s, e, n in p["terms"]:
            circ = "c. " if (p["col"] == "catholic" and s < 250) else ""
            terms.append("%s%d&ndash;present" % (circ, s) if e == "present" else ("%s%d&ndash;%s%d" % (circ, s, circ, e) if isinstance(e, int) and e > s else "%s%d" % (circ, s)))
        nums = [n for _, _, n in p["terms"] if n]
        office = p.get("office", "")
        if office and nums: office = "%s %s" % (nums[0], office)
        if office and len(p["terms"]) > 1: office += " &middot; %d terms" % len(p["terms"])
        if pid == "orthodox:Andrew_the_Apostle": office = "Founder of the see of Byzantium, by tradition"
        if p.get("act"): office = re.sub(r"^.*&middot;\s*", "", card[1]) if card else ""
        life = []
        if L.get("b") is not None: life.append("Born " + yrs(L["b"], L.get("bc")))
        if L.get("d") is not None: life.append("Died " + yrs(L["d"], L.get("dc")))
        if L.get("b") is not None and L.get("d") is not None and not L.get("bc") and not L.get("dc") and L["d"] > L["b"]:
            life.append("aged about %d" % (L["d"] - L["b"]))
        pn = prevnext.get(pid, [None, None])
        recs[pid] = {"n": re.sub(r"&eacute;", "é", name), "l": p.get("line", ""), "c": p["col"] if p["col"] != "root" else "grey",
                     "o": office, "t": " and ".join(terms), "life": " &middot; ".join(life),
                     "tag": card[2] if card else "", "bio": trim_bio(bio.get("extract", "")), "w": (p.get("wiki") or "").replace("_", " ") or None,
                     "img": img_path(slug), "prev": pn[0], "next": pn[1], "b": L.get("b"), "d": L.get("d"), "founder": bool(p.get("act")), "terms_y": [[a, endyear(a, b)] for a, b, _ in p["terms"]],
                     "span": [min((t[0] for t in p["terms"]), default=p.get("act")), max((endyear(t[0], t[1]) for t in p["terms"]), default=p.get("act"))],
                     "pg": PAGE_OF.get(p["col"], "index.html")}
    for r in recs.values():
        r["pn"] = recs[r["prev"]]["n"] if r["prev"] in recs else None
        r["nn"] = recs[r["next"]]["n"] if r["next"] in recs else None
    assign_events(recs)
    for r in recs.values():
        ty = r.get("terms_y") or ([[r["span"][0], r["span"][1]]] if r.get("span") and r["span"][0] is not None else [])
        r["y"] = [[a, b if b is not None else a] for a, b in ty if a is not None]
        for k in ("b", "d", "span", "founder", "terms_y"): r.pop(k, None)
    json.dump(recs, open(os.path.join(ROOT, "data", "people.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return recs

# ============================================================ follow the line back
def trace_chain(pid, recs):
    """Sections oldest first: [(line id, [pids oldest..newest], join or None)]. Mirrors the walk in app.js."""
    import trace as T
    pid = T.ALIAS.get(pid, pid)
    if pid not in recs or recs[pid]["c"] in T.NO_TRACE: return []
    secs, cur = [], pid
    for _ in range(8):
        hs, p, seen = [], cur, set()
        while p and p in recs and p not in seen:
            seen.add(p); hs.append(p); p = recs[p].get("prev")
        line = recs[cur]["c"]; meta = T.TRACE.get(line, {})
        j = meta.get("join")
        secs.insert(0, (line, hs[::-1], j if j and j[0] in recs else None))
        if not (j and j[0] in recs): break
        cur = j[0]
    return secs

WALL_LABELS = {  # label, short form for continued chunks
    "anglican": ("Archbishops of Canterbury", "Canterbury"), "catholic": ("Bishops of Rome", "Rome"),
    "orthodox": ("Patriarchs of Constantinople", "Constantinople"), "coptic": ("Coptic popes of Alexandria", "Alexandria (Coptic)"),
    "alexandria": ("Greek patriarchs of Alexandria", "Alexandria (Greek)"), "syriac": ("Syriac patriarchs of Antioch", "Antioch (Syriac)"),
    "antioch": ("Patriarchs of Antioch", "Antioch"), "jerusalem": ("Patriarchs of Jerusalem", "Jerusalem"),
    "armenian": ("Catholicoi of All Armenians", "Armenia"), "ethiopian": ("Bishops and patriarchs of Ethiopia", "Ethiopia"),
    "georgia": ("Catholicos-patriarchs of Georgia", "Georgia"), "moscow": ("Metropolitans and patriarchs of Moscow", "Moscow"),
    "tec": ("Presiding bishops of the Episcopal Church", "Episcopal Church"), "acna": ("Archbishops of the Anglican Church in North America", "ACNA"),
}
def build_wall(recs, current):
    """data/wall.json for the intro: each line of succession, newest first, ordered by the earliest dated term in the list
    (ties alphabetical). Names come from the same predecessor chains as the dialog; nothing is added by hand."""
    lists = []
    for pid in current:
        line = recs[pid]["c"]
        if line not in WALL_LABELS: continue
        names, p, seen, years = [], pid, set(), []
        while p and p in recs and p not in seen:
            seen.add(p); names.append(html.unescape(recs[p]["n"])); years += [a for a, _ in recs[p].get("y") or []]; p = recs[p].get("prev")
        lists.append({"c": line, "label": WALL_LABELS[line][0], "short": WALL_LABELS[line][1], "names": names, "_start": min(years) if years else 9999})
    lists.sort(key=lambda L: (L["_start"], L["short"]))
    for L in lists: L.pop("_start")
    json.dump(lists, open(os.path.join(ROOT, "data", "wall.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return lists

def slugify(n): return re.sub(r"[^a-z0-9]+", "-", html.unescape(n).lower()).strip("-")

def build_trace_pages(recs):
    """line.html (any person, from ?p=), line-<name>.html for each current holder (with share tags), data/trace.json."""
    import trace as T
    current = []
    for pid, r in recs.items():
        if r["c"] in T.TRACE and not r.get("next") and r.get("y") and max(b for _, b in r["y"]) >= 2025:
            current.append(pid)
    order = list(T.TRACE)
    current.sort(key=lambda pid: order.index(recs[pid]["c"]))
    shares = {}
    for pid in current:
        slug = slugify(recs[pid]["n"])
        shares[pid] = ("line-%s.html" % slug, "img/share/line-%s.png" % slug)
        recs[pid]["sh"] = shares[pid][0]
    json.dump(recs, open(os.path.join(ROOT, "data", "people.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    build_wall(recs, current)
    json.dump({"lines": T.TRACE, "none": sorted(T.NO_TRACE), "alias": T.ALIAS, "current": current},
              open(os.path.join(ROOT, "data", "trace.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    out = []
    def page(fname, pid=None):
        if pid:
            secs = trace_chain(pid, recs); n = sum(len(h) for _, h, _ in secs) - 1
            title = "The line before %s" % recs[pid]["n"]
            desc = "%s. Followed back through %d predecessors, as each church records it." % (html.unescape(re.sub(r"<[^>]+>", "", recs[pid]["o"])), n)
            head = head_meta(esc(desc), esc(title), shares[pid][1] if os.path.exists(os.path.join(ROOT, shares[pid][1])) else None)
            doc_title = "%s &middot; %s" % (esc(title), SITE["name"])
        else:
            head = head_meta("Choose anyone on the chart and follow their office back, predecessor by predecessor, as each church records it.",
                             "Follow the line back")
            doc_title = "Follow the line back &middot; %s" % SITE["name"]
        body = ('%s<div class="page page--trace"><main class="trace" id="chart" tabindex="-1"%s aria-live="polite">'
                '<noscript><p class="tr__empty">This page needs JavaScript to draw the line.</p></noscript></main></div>%s'
                % (nav_html(fname), (' data-trace="%s"' % esc(pid)) if pid else "", footer_html()))
        doc = TEMPLATE.format(head=head, v_css=asset_version("assets/css/app.css"), v_js=asset_version("assets/js/app.js"),
                              title=doc_title, body=body, dialog=DIALOG)
        doc = doc.encode("ascii", "xmlcharrefreplace").decode("ascii")
        open(os.path.join(ROOT, fname), "w", encoding="ascii").write(doc)
        out.append((fname, len(doc)))
    page("line.html")
    for pid in current: page(shares[pid][0], pid)
    return out

# ============================================================ main
if __name__ == "__main__":
    built, order = [], []
    for vname, cfg in views.VIEWS.items():
        variants = cfg.get("variants") or {}
        pages = [(cfg["file"], cfg["cols"])]
        slot_i = cfg.get("variant_slot")
        for vk, vcol in variants.items():
            cols = list(cfg["cols"]); cols[slot_i] = vcol
            pages.append((cfg["file"].replace(".html", "-%s.html" % vk), cols))
        for f, cols in pages:
            for c in cols: PAGE_OF.setdefault(c["id"], f)
            chooser = [(p_cols[slot_i]["title"], p_f) for p_f, p_cols in pages if p_f != f] if variants else None
            size, total = render(vname, cfg, cols, f, chooser)
            built.append((f, size, total))
    # before/after order per line (register order), shared across pages
    for pidp, key, lk in [("anglican", "canterbury", "main"), ("catholic", "rome", "main"), ("orthodox", "constantinople", "main"),
                          ("moscow", "moscow", "family"), ("antioch", "antioch", "family"), ("georgia", "georgia", "family"),
                          ("jerusalem", "jerusalem", "family"), ("alexandria", "alexandria_gr", "family"), ("coptic", "coptic", "family"),
                          ("syriac", "syriac", "family"), ("armenian", "armenian", "family"), ("ethiopian", "ethiopia", "family"),
                          ("tec", "tec", "family"), ("acna", "acna", "family")]:
        col = dict(id=pidp, key=key, links=lk)
        ids = []
        for i, r in enumerate(LINES[key]["rows"]):
            if re.match(r"^(seat vacant|vacant|sede vacante|interregnum)", r["name"], re.I): continue
            t = link_for(col, i); pid = "%s:%s" % (pidp, t or "name:%s:%d" % (r["name"], r["start"]))
            if pid not in ids: ids.append(pid)
        if pidp == "orthodox": ids.insert(0, "orthodox:Andrew_the_Apostle")
        order.append(ids)
    for col in (views.LUTHERAN, views.REFORMED, views.FREE):
        order.append(["%s:%s" % (col["id"], c[6]) for c in col["cards"]])
    recs = build_people_json(order)
    import pages
    for f, size in pages.build(dict(head=head_meta(), TEMPLATE=TEMPLATE, nav=nav_html, footer=footer_html, ver=asset_version, SITE=SITE, tbc=tbc, ROOT=ROOT)):
        built.append((f, size, 0))
    for f, size in build_trace_pages(recs): built.append((f, size, 0))
    for f, size, total in built: print("  %-40s %8d bytes  %4d holders" % (f, size, total))
    print("people:", len(recs), "| with event:", sum(1 for r in recs.values() if r.get("ev")))
