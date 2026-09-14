"""Share images (1200x630 PNG) for 'Follow the line back', one per current office holder: img/share/line-<name>.png.

Renders a small HTML card per person and screenshots it with headless Google Chrome (needs internet for the web font).
Run after site.py, then run site.py again so the pages pick up the og:image tags:

    python3 site.py && python3 share_images.py && python3 site.py
"""
import html, json, os, re, subprocess, tempfile
import trace as T

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HUE = {"anglican": "#35587F", "catholic": "#5E4380", "orthodox": "#8A611C", "moscow": "#8C4A2F", "antioch": "#2F6B62", "georgia": "#7A3B55",
       "jerusalem": "#5B6B2E", "alexandria": "#3F5A8A", "coptic": "#8E2F3A", "syriac": "#6A4C8C", "armenian": "#9A5B1E", "ethiopian": "#2E6B45",
       "tec": "#2F5C8F", "acna": "#1C6B68"}

def chain(pid, P):
    secs, cur = [], pid
    for _ in range(8):
        hs, p, seen = [], cur, set()
        while p and p in P and p not in seen: seen.add(p); hs.append(p); p = P[p].get("prev")
        line = P[cur]["c"]; j = T.TRACE.get(line, {}).get("join")
        secs.insert(0, (line, hs[::-1], j if j and j[0] in P else None))
        if not (j and j[0] in P): break
        cur = j[0]
    return secs

def year(r): return r["y"][0][0] if r.get("y") else 30
def plain(s): return html.unescape(re.sub(r"<[^>]+>", "", s or ""))

def card(pid, P):
    r = P[pid]; secs = chain(pid, P)
    n = sum(len(h) for _, h, _ in secs) - 1
    y0, y1 = year(P[secs[0][1][0]]), year(r)
    top, bottom, x = 70, 560, 930
    scale = lambda y: top + (bottom - top) * (y - y0) / max(1, y1 - y0)
    parts, labels = [], []
    for i, (line, hs, j) in enumerate(secs):
        a = j[1] if (i and j) else year(P[hs[0]])
        b = secs[i + 1][2][1] if i + 1 < len(secs) and secs[i + 1][2] else y1
        early = T.TRACE.get(line, {}).get("early") or (100 if a < 100 else a)
        if a < early:
            parts.append('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2" opacity=".45"/>' % (x, scale(a), x, scale(min(early, b)), HUE.get(line, "#888")))
        parts.append('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="5"/>' % (x, scale(max(a, early)), x, scale(b), HUE.get(line, "#888")))
        if i:
            yy = scale(a)
            parts.append('<rect x="%d" y="%.0f" width="18" height="18" transform="rotate(45 %d %.0f)" fill="#F5F4F0" stroke="%s" stroke-width="3"/>' % (x - 9, yy - 9, x, yy, HUE.get(line, "#888")))
            labels.append((yy, "%s &middot; %s" % (j[3] if len(j) > 3 else j[1], html.escape(T.TRACE[line]["church"].replace("the ", "")))))
    parts.append('<circle cx="%d" cy="%d" r="11" fill="#F5F4F0" stroke="%s" stroke-width="3"/>' % (x, top, HUE.get(secs[0][0], "#888")))
    parts.append('<circle cx="%d" cy="%d" r="15" fill="%s"/>' % (x, bottom, HUE.get(r["c"], "#888")))
    labels.insert(0, (top, "%s" % ("1st century" if y0 < 100 else y0)))
    labels.append((bottom, str(y1)))
    lab = "".join('<text x="%d" y="%.0f" font-size="22" fill="#55514A" dominant-baseline="middle">%s</text>' % (x + 34, yy, t) for yy, t in labels)
    office = plain(r.get("o") or r.get("l"))
    return """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap">
<style>html,body{margin:0;width:1200px;height:630px;background:#F5F4F0;color:#1F1D1A;font-family:"EB Garamond",Georgia,serif;overflow:hidden}
.col{position:absolute;left:80px;top:88px;bottom:52px;width:720px;display:flex;flex-direction:column}
.k{font-size:20px;letter-spacing:.16em;text-transform:uppercase;font-weight:500;color:#6C675E}
h1{margin:14px 0 0;font-size:76px;font-weight:400;line-height:1.02;letter-spacing:-.01em}
.o{margin-top:22px;font-size:30px;font-style:italic;color:#55514A;line-height:1.25}
.n{margin-top:auto;font-size:26px;color:#1F1D1A}
.w{margin-top:10px;font-size:22px;color:#6C675E}
svg{position:absolute;left:0;top:0}</style></head><body>
<div class="col"><div class="k">Follow the line back</div><h1>The line before %s</h1><div class="o">%s</div>
<div class="n">%d predecessors, %s</div><div class="w">Lineage of the Church</div></div>
<svg width="1200" height="630">%s%s</svg></body></html>""" % (html.escape(r["n"]), html.escape(office), n,
        "back to the 1st century" if y0 < 100 else "back to %d" % y0, "".join(parts), lab)

if __name__ == "__main__":
    P = json.load(open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8"))
    tj = json.load(open(os.path.join(ROOT, "data", "trace.json"), encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    for pid in tj["current"]:
        r = P[pid]
        if not r.get("sh"): continue
        out = os.path.join(ROOT, "img", "share", r["sh"].replace(".html", ".png"))
        src = os.path.join(tmp, "card.html"); open(src, "w", encoding="utf-8").write(card(pid, P))
        profile = os.path.join(tmp, "profile")   # a throwaway profile, so a running Chrome is never touched
        for attempt in range(3):
            try:
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                                "--no-first-run", "--user-data-dir=" + profile, "--window-size=1200,630", "--virtual-time-budget=4000",
                                "--screenshot=%s" % out, "file://" + src],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
                break
            except subprocess.TimeoutExpired:
                print("  timed out, retrying", pid)
        print(out, os.path.getsize(out))
