import json, time, urllib.request, urllib.parse, os
UA = "LineageResearch/1.0 (church-leader-tree) python-urllib"
SP = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SP, "data", "cache"); os.makedirs(CACHE, exist_ok=True)

def _get(url, key):
    p = os.path.join(CACHE, key)
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(5):
        try:
            s = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
            open(p, "w", encoding="utf-8").write(s)
            time.sleep(1.0)
            return s
        except Exception as e:
            if getattr(e, "code", None) == 404: return ""
            time.sleep(4 * (i + 1))
    return ""

def wikitext(title):
    url = ("https://en.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext"
           "&redirects=1&page=" + urllib.parse.quote(title.replace(" ", "_")))
    raw = _get(url, "wt_" + title.replace("/", "_").replace(" ", "_") + ".json")
    if not raw: return ""
    try: return json.loads(raw)["parse"]["wikitext"]["*"]
    except Exception: return ""

def html(title):
    url = ("https://en.wikipedia.org/w/api.php?action=parse&format=json&prop=text"
           "&redirects=1&page=" + urllib.parse.quote(title.replace(" ", "_")))
    raw = _get(url, "html_" + title.replace("/", "_").replace(" ", "_") + ".json")
    if not raw: return ""
    try: return json.loads(raw)["parse"]["text"]["*"]
    except Exception: return ""

def extract(title):
    url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts"
           "&exintro&explaintext&redirects=1&titles=" + urllib.parse.quote(title.replace(" ", "_")))
    raw = _get(url, "ex_" + title.replace("/", "_").replace(" ", "_") + ".json")
    if not raw: return ""
    try:
        d = json.loads(raw)
        for p in d["query"]["pages"].values():
            return p.get("extract", "")
    except Exception: return ""
    return ""
