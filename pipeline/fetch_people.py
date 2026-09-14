"""Fetch Wikipedia intro, short description, thumbnail and Wikidata birth/death years for a set of article titles.
Merges into data/bios_raw.json, data/life.json, data/holder_slugs.json and downloads portraits to img/holders/."""
import json, os, re, sys, time, urllib.parse, urllib.request, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data"); ROOT = os.path.dirname(HERE)
UA = "LineageResearch/1.0 (church-leader-tree; one-off research) python-urllib"
def get(url):
    for i in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90).read())
        except Exception: time.sleep(4 * (i + 1))
    return None

def fetch(titles):
    bios = json.load(open(os.path.join(D, "bios_raw.json")))
    life = json.load(open(os.path.join(D, "life.json")))
    slugs = json.load(open(os.path.join(D, "holder_slugs.json")))
    todo = [t for t in dict.fromkeys(titles) if t and (t not in bios or "desc" not in bios[t])]
    print("fetching", len(todo), "articles")
    for i in range(0, len(todo), 20):
        batch = todo[i:i + 20]
        d = get("https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&formatversion=2"
                "&prop=extracts|pageimages|pageprops|description&exintro=1&explaintext=1&exlimit=20&piprop=thumbnail"
                "&pithumbsize=330&pilimit=50&ppprop=wikibase_item&titles=" + urllib.parse.quote("|".join(batch)))
        if not d: print("  batch failed", i); continue
        q = d["query"]; alias = {t: t for t in batch}
        for n in q.get("normalized", []):
            for k, v in list(alias.items()):
                if v == n["from"]: alias[k] = n["to"]
        for r in q.get("redirects", []):
            for k, v in list(alias.items()):
                if v == r["from"]: alias[k] = r["to"]
        pages = {p["title"]: p for p in q["pages"]}
        for t in batch:
            p = pages.get(alias[t]) or {}
            bios[t] = {"title": p.get("title"), "extract": p.get("extract", ""), "desc": p.get("description", ""),
                       "thumb": (p.get("thumbnail") or {}).get("source"), "qid": (p.get("pageprops") or {}).get("wikibase_item")}
        time.sleep(0.8)
    # lifespans
    need = sorted({v["qid"] for t, v in bios.items() if t in titles and v.get("qid") and v["qid"] not in life})
    def parse(cl, prop):
        best = None
        for c in cl.get(prop, []):
            dv = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if not dv: continue
            m = re.match(r"^([+-])(\d+)-", dv["time"]); p = dv["precision"]
            if not m or p < 7: continue
            y = int(m.group(2)) * (-1 if m.group(1) == "-" else 1)
            if best is None or c.get("rank") == "preferred" or (best[2] < 9 and p >= 9): best = (y, p < 9, p)
        return best
    for i in range(0, len(need), 50):
        d = get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims&ids=" + "|".join(need[i:i + 50]))
        for qid, ent in (d or {}).get("entities", {}).items():
            cl = ent.get("claims", {}); b = parse(cl, "P569"); dd = parse(cl, "P570")
            life[qid] = {"b": b[0] if b else None, "bc": b[1] if b else False, "d": dd[0] if dd else None, "dc": dd[1] if dd else False}
        time.sleep(1)
    # portraits
    got = 0
    for t in titles:
        v = bios.get(t) or {}
        if not v.get("thumb"): continue
        slug = "h-" + re.sub(r"[^a-z0-9]+", "-", (v["title"] or t).lower()).strip("-")[:60]
        dst = os.path.join(ROOT, "img", "holders", slug + ".jpg")
        slugs[t] = slug
        if os.path.exists(dst): continue
        raw = os.path.join(D, "cache", slug + ".img")
        try:
            open(raw, "wb").write(urllib.request.urlopen(urllib.request.Request(v["thumb"], headers={"User-Agent": UA}), timeout=60).read())
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", "128", raw, "--out", dst], capture_output=True)
            got += 1; time.sleep(0.3)
        except Exception as e:
            print("  image failed", t, e)
    json.dump(bios, open(os.path.join(D, "bios_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(life, open(os.path.join(D, "life.json"), "w"), indent=1)
    json.dump(slugs, open(os.path.join(D, "holder_slugs.json"), "w"), indent=1, ensure_ascii=False)
    have = [t for t in titles if t in bios]
    print("articles:", len(have), "| with portrait:", sum(1 for t in have if bios[t].get("thumb")),
          "| new portraits downloaded:", got, "| with lifespan:", sum(1 for t in have if bios[t].get("qid") in life))

if __name__ == "__main__":
    F = json.load(open(os.path.join(D, "family_links.json")))
    titles = [t.replace("_", " ") for v in F.values() for t in v if t]
    extra = ["Martin Luther", "Philip Melanchthon", "Huldrych Zwingli", "John Calvin", "Theodore Beza", "John Knox",
             "Menno Simons", "Conrad Grebel", "Thomas Helwys", "John Smyth (Baptist minister)", "George Fox", "John Wesley",
             "George Whitefield", "Francis Asbury", "William Booth", "William Carey (missionary)", "Pandita Ramabai",
             "William J. Seymour", "Charles Fox Parham", "William Wadé Harris", "Billy Graham", "Nicolaus Zinzendorf",
             "Charles Spurgeon", "Samuel Seabury", "Robert Browne (Brownist)", "Dietrich Bonhoeffer", "Martin Luther King Jr.",
             "Laurentius Petri", "Aimee Semple McPherson", "Jan Hus", "John Wycliffe", "Martin Bucer", "Heinrich Bullinger",
             "Jacob Arminius", "Balthasar Hubmaier", "Jakob Ammann", "Richard Allen (bishop)", "Charles Wesley"]
    fetch(titles + extra)
