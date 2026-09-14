"""Recover a Wikipedia article link for every holder on the family-view lines, by matching register names
to link text on each list page, in order."""
import json, os, re, html, urllib.parse
from html.parser import HTMLParser
import wikilib
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")
lines = json.load(open(os.path.join(D, "lines.json")))
PAGES = {
 "coptic": "List of popes of the Coptic Orthodox Church", "armenian": "List of catholicoi of all Armenians",
 "moscow": "List of metropolitans and patriarchs of Moscow", "syriac": "List of Syriac Orthodox patriarchs of Antioch",
 "antioch": "List of Greek Orthodox patriarchs of Antioch", "alexandria_gr": "List of Greek Orthodox patriarchs of Alexandria",
 "jerusalem": "Greek Orthodox Patriarch of Jerusalem", "georgia": "List of heads of the Georgian Orthodox Church",
 "ethiopia": "List of abunas of Ethiopia", "tec": "Presiding Bishop of the Episcopal Church",
}
class A(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.out=[]; s.cur=None; s.skip=0
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in ("sup","style"): s.skip+=1
        if t=="a" and not s.skip:
            h=a.get("href","")
            if h.startswith("/wiki/") and ":" not in h: s.cur=[h[6:].split("#")[0], []]
    def handle_endtag(s,t):
        if t in ("sup","style"): s.skip=max(0,s.skip-1)
        if t=="a" and s.cur: s.out.append((s.cur[0], "".join(s.cur[1]))); s.cur=None
    def handle_data(s,d):
        if s.cur is not None: s.cur[1].append(d)
def norm(x):
    x = re.sub(r"^(St\.?|Saint|Pope|Patriarch|Mor|Mar|Abune|Catholicos|Ignatius)\s+", "", x.strip(), flags=re.I)
    return re.sub(r"[^a-z0-9]", "", x.lower())
out = {}
for key, title in PAGES.items():
    p = A(); p.feed(wikilib.html(title)); anchors = [(h, norm(t)) for h, t in p.out if t.strip()]
    res, pos, first_seen = [], 0, {}
    for r in lines[key]["rows"]:
        k = norm(r["name"]); found = None
        if k:
            for i in range(pos, len(anchors)):
                if anchors[i][1] == k: found = anchors[i][0]; pos = i + 1; break
            if not found:
                cands = [h for h, t in anchors if t == k]
                found = cands[0] if cands else None
            if not found:
                cands = [h for h, t in anchors if t.startswith(k) and len(t) - len(k) < 25]
                found = cands[0] if cands else None
        if found and re.match(r"^(List_of|Patriarch_of|Catholicos|Pope_of|Presiding_Bishop)", found): found = None
        res.append(urllib.parse.unquote(found) if found else None)
    out[key] = res
    print("%-14s %3d/%3d linked" % (key, sum(1 for x in res if x), len(res)))
out["acna"] = ["Robert Duncan (bishop)", "Foley Beach", "Steve Wood (bishop)"]
json.dump(out, open(os.path.join(D, "family_links.json"), "w"), indent=1, ensure_ascii=False)
