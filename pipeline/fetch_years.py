"""Fetch the Events section of every Wikipedia year article (AD 1-2026) into data/years.json.
Each event keeps its cleaned text, month (if given), and the first article it links to."""
import json, os, re, time, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")
UA = "LineageResearch/1.0 (church-leader-tree; one-off research) python-urllib"
OUT = os.path.join(D, "years.json")
years = json.load(open(OUT)) if os.path.exists(OUT) else {}

def title_for(y): return ("AD %d" % y) if y < 100 else str(y)

def clean(s):
    s = re.sub(r"<ref[^>]*/>", "", s); s = re.sub(r"<ref.*?</ref>", "", s, flags=re.S)
    for _ in range(3): s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    first = re.search(r"\[\[([^\]|#]+)", s)
    link = first.group(1).strip() if first else None
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"'''?", "", s); s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip(" *:;")
    return s, link

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
def parse(wt):
    m = re.search(r"==\s*Events\s*==(.*?)(\n==\s*(Births|Deaths)\s*==|\Z)", wt, flags=re.S)
    if not m: return []
    body = m.group(1); out = []; month = None
    for line in body.split("\n"):
        if not line.startswith("*"): continue
        depth = len(line) - len(line.lstrip("*"))
        txt, link = clean(line[depth:])
        if not txt: continue
        mm = re.match(r"^(%s)(?: \d{1,2})?\s*[–-]\s*(.*)$" % MONTHS, txt)
        if mm: month, txt = mm.group(1), mm.group(2)
        elif re.match(r"^(%s)( \d{1,2})?$" % MONTHS, txt): month = txt.split()[0]; continue
        if len(txt) < 25 or len(txt) > 260: continue
        out.append({"t": txt, "l": link, "m": month if depth > 1 or mm else None})
    return out

todo = [y for y in range(1, 2027) if not years.get(str(y))]
print("years to fetch:", len(todo), flush=True)
for i in range(0, len(todo), 20):
    batch = todo[i:i + 20]
    titles = {}
    for y in batch:
        titles["AD %d" % y] = y
        titles[str(y)] = y
    url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&redirects=1&prop=revisions"
           "&rvprop=content&rvslots=main&titles=" + urllib.parse.quote("|".join(titles)))
    d = None
    for a in range(8):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90).read()); break
        except Exception: time.sleep(20 * (a + 1))
    if not d: print("batch failed", batch[0], flush=True); continue
    q = d["query"]; alias = {t: t for t in titles}
    for n in q.get("normalized", []):
        for k, v in list(alias.items()):
            if v == n["from"]: alias[k] = n["to"]
    for r in q.get("redirects", []):
        for k, v in list(alias.items()):
            if v == r["from"]: alias[k] = r["to"]
    pages = {p["title"]: p for p in q.get("pages", [])}
    best = {}
    for t, y in titles.items():
        p = pages.get(alias[t]) or {}
        try: wt = p["revisions"][0]["slots"]["main"]["content"]
        except Exception: wt = ""
        if "may refer to" in wt[:400]: continue
        evs = parse(wt)
        if len(evs) > len(best.get(y, [])): best[y] = evs
    for y in batch: years[str(y)] = best.get(y, [])
    json.dump(years, open(OUT, "w"), ensure_ascii=False)
    print("through", batch[-1], "| events so far:", sum(len(v) for v in years.values()), flush=True)
    time.sleep(3)
print("done", flush=True)
