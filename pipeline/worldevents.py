"""Give every person one 'Meanwhile in the world' event.

Rules (from the user):
  * every event is used once across the whole site;
  * it happened during the person's tenure (founders: during their working life; Jesus: his lifetime);
  * it frames the world they served in for a Western reader: secular, vivid, a little niche is fine.

Candidates come from the Events section of Wikipedia's year articles (data/years.json, built by fetch_years.py),
topped up with the hand-checked timeline in events.py. People with the fewest candidates choose first.
"""
import html, json, os, re
from events import EVENTS

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")

CHURCH = re.compile(r"\b(pope|popes|antipope|papa[lc]y?|pontiff|patriarch\w*|archbishop\w*|bishop\w*|church(es)?|council of|synod|saint|st\.|"
                    r"abbey|abbot|abbess|monaster\w*|monk|nun|cardinal\w*|canoni[sz]\w*|heres\w*|heretic\w*|clergy|diocese|"
                    r"catholicos|metropolitan|basilica|cathedral|relics?|martyr\w*|consecrat\w*|excommunicat\w*|ordain\w*|"
                    r"christian\w*|jesuits?|franciscan\w*|dominican\w*|benedictine\w*|missionar\w*|theolog\w*|liturg\w*|"
                    r"religio\w*|priest\w*|pilgrim\w*|crusade|bible|gospel|apostle\w*|evangel\w*|jesus|christ)\b", re.I)
DULL = re.compile(r"\b(era name|changes? (his|the) era|appoint\w*|is succeeded|succeeds|consul|consuls|proconsul|"
                  r"governor of|becomes governor|is named|is elected|is re-?elected|takes office|stands for election|census|"
                  r"magistrate|prefect|prefecture|county seat|incorporated|municipal|sources? disagree)\b", re.I)
VIVID = re.compile(r"\b(battle|siege|sack\w*|war\b|invade\w*|invasion|conquer\w*|founds?|founded|foundation of|invent\w*|discover\w*|"
                   r"erupt\w*|earthquake|plague|epidemic|pandemic|famine|flood|fire|comet|eclipse|supernova|treaty|crowned|coronation|"
                   r"assassinat\w*|murder\w*|execut\w*|completed?|built|construction|opens|opened|publish\w*|printed|first|voyage|"
                   r"expedition|reaches|revolt|rebellion|uprising|university|library|observatory|explorer|circumnavigat\w*|"
                   r"independence|abolish\w*|slavery|emperor|empress|king|queen|sultan|caliph|shogun|khan|pharaoh|olympic|"
                   r"composer|symphony|opera|painting|novel|poet|play\b|theatre|telescope|steam|railway|flight|moon|nuclear|atomic|"
                   r"writes|finishes|compos\w*|paints|sculpt\w*|premieres?|performed|exhibition|patent\w*|elected president)\b", re.I)
WEST = re.compile(r"\b(Rome|Roman|Romans|Britain|British|England|English|Scotland|Scots|Ireland|Irish|Wales|France|French|Franks|Frankish|"
                  r"Spain|Spanish|Portugal|Portuguese|Italy|Italian|Venice|Venetian|Florence|Germany|German|Holy Roman|Austria|Vienna|"
                  r"Netherlands|Dutch|Sweden|Swedish|Norway|Denmark|Danes|Viking\w*|Normans?|Byzantine|Constantinople|Greece|Greek|"
                  r"Athens|Egypt|Persia\w*|Ottoman\w*|Mongol\w*|China|Chinese|Japan\w*|India\w*|America\w*|Mexico|Aztec\w*|Inca\w*|"
                  r"Maya|Russia\w*|Moscow|Poland|Hungary|London|Paris|Carthage|Jerusalem|Baghdad|Islam\w*|Arab\w*|Charlemagne|"
                  r"Napoleon|Shakespeare|Leonardo|Columbus|Galileo|Newton)\b")

GRIM = re.compile(r"\b(killed|kills|injur\w*|gunman|shooting|shot dead|bomb\w*|explosion|crash\w*|collision|derail\w*|terrorist\w*|"
                  r"suicide|hostage|stabbing|arrest\w*|sentenced|convicted|lawsuit|court rules|protest\w*|riot\w*|referendum|"
                  r"election|elected|parliament passes|legislation|bill is|act is passed|framework|bilateral|memorandum|minister|"
                  r"first mentioned|is mentioned|charter|count of|countess|duke of|duchy|lord of|earl of|baron|margrave|landgrave|"
                  r"tax\w*|tribute|dowry|marries|marriage|betroth\w*|sues|fined|resigns|dismissed|deposed as|exiled to)\b", re.I)
FAMOUS = re.compile(r"\b(world'?s first|first time|first ever|for the first time|Shakespeare|Newton|Galileo|Copernicus|Kepler|Darwin|Einstein|"
                    r"Mozart|Beethoven|Bach|Handel|Michelangelo|Leonardo|Raphael|Rembrandt|Dante|Chaucer|Gutenberg|Columbus|Magellan|"
                    r"Marco Polo|Joan of Arc|Genghis|Kublai|Saladin|Alfred the Great|Charlemagne|William the Conqueror|Henry VIII|"
                    r"Elizabeth I|Louis XIV|Peter the Great|Catherine the Great|Washington|Lincoln|Victoria|Napoleon|Churchill|Gandhi|"
                    r"Mandela|Moon|Titanic|Eiffel|Suez|Panama Canal|Great Wall|Taj Mahal|Colosseum|Pompeii|Vesuvius|Magna Carta|"
                    r"Black Death|Hundred Years|Wars of the Roses|Armada|Mayflower|Bastille|Waterloo|Trafalgar|Gettysburg|Hastings|"
                    r"Agincourt|Constantinople falls|Ottoman|Aztec|Inca|Maya|Viking|Mongol|Samurai|Shogun|Ming|Tang|Song dynasty|"
                    r"Silk Road|printing|telescope|steam engine|electricity|telegraph|telephone|radio|television|airplane|penicillin|"
                    r"vaccine|internet|World Wide Web|computer|satellite|Sputnik|Apollo|Olympic|Nobel|Oxford|Cambridge|Sorbonne|"
                    r"Louvre|Versailles|Notre-Dame|Westminster|Tower of London|Venice|Florence|Kyoto|Angkor|Timbuktu|Great Zimbabwe)\b", re.I)
BROKEN = re.compile(r"\b(within|about|some|over|nearly|approximately|of|at|by|to) (of|,|\.)|\s[,.;]|\(\s*\)|^\d{2,4}\s*[-\u2013]\s*\d{2,4}\s*[-\u2013]|"
                    r"\b(fuck|shit|cunt)\w*|\ba distance\b\s*(to|from)\b|\b(from|to) (and|,)\b", re.I)
def score(t):
    s = 0.0
    if GRIM.search(t): s -= 4
    s += 3.0 * min(2, len(FAMOUS.findall(t)))
    if CHURCH.search(t): s -= 8
    if DULL.search(t): s -= 5
    s += 2.0 * min(2, len(VIVID.findall(t)))
    s += 1.5 * min(2, len(WEST.findall(t)))
    n = len(t)
    s += 1.5 if 40 <= n <= 140 else (-1 if n > 170 else 0) + (-2 if n > 220 else 0)
    if re.match(r"^(The )?(Emperor|King|Queen) \w+ (dies|is born)", t): s -= 1
    return s

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
def tidy(t):
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip().rstrip(",;:")
    t = re.sub(r"^(?:c\.\s*)?(?:%s)(?:\s+\d{1,2})?(?:\s*[\u2013\u2014-]\s*\d{1,2})?\s*[\u2013\u2014-]\s*" % MONTHS, "", t)
    t = re.sub(r"^(?:approximate date|c\.|circa|(?:early|mid|late)[- ]\w+|(?:%s)(?: or (?:%s))?|spring|summer|autumn|winter)\s*[\u2013\u2014-]\s*" % (MONTHS, MONTHS), "", t, flags=re.I)
    t = re.sub(r"\s*\((?:approximate date|approximate|possibly|traditional date|date uncertain)\)", "", t, flags=re.I)
    t = re.sub(r"\s*\(approximate date\)\.?$", "", t, flags=re.I)
    t = re.sub(r"\s*\((?:[^()]*\d{3,4}[^()]*|modern[^()]*|now[^()]*)\)", "", t)
    t = t[0].upper() + t[1:] if t else t
    return t if t.endswith((".", "!", "?")) else t + "."

def load_candidates():
    pool = {}
    path = os.path.join(D, "years.json")
    if os.path.exists(path):
        for y, evs in json.load(open(path, encoding="utf-8")).items():
            for e in evs:
                t = tidy(e["t"])
                if len(t) < 30 or BROKEN.search(t): continue
                lk = e.get("l")
                if not lk or re.match(r"^(%s)( \d{1,2})?$|^\d{1,4}s?$|^AD \d+$" % MONTHS, lk): lk = ("AD %s" % y) if int(y) < 150 else str(y)
                pool.setdefault(int(y), []).append({"y": int(y), "t": t, "l": lk,
                                                   "s": score(t) + 1.0})
    for y, t, l in EVENTS:                     # hand-checked timeline gets a bonus
        pool.setdefault(y, []).append({"y": y, "t": tidy(t), "l": l, "s": score(t) + 4})
    return pool

def assign_events(recs):
    pool = load_candidates()
    years = sorted(pool)
    used = set()
    def window(r):
        s, e = r["span"]
        if r["c"] == "grey" and r["n"].startswith("Jesus"):
            return (1, 33)
        if r["n"] == "St Andrew":
            return (30, 60)
        if s is None:
            return None
        if r.get("founder"):                                    # founders: their working life
            return (max(s - 15, (r["b"] or s) + 18), r["d"] or 2026)
        return (s, e)
    wins = {pid: window(r) for pid, r in recs.items()}
    def in_terms(r, y):
        ts = r.get("terms_y")
        return True if not ts else any(a <= y <= b for a, b in ts)
    def cands(pid):
        w = wins[pid]; r = recs[pid]
        if not w: return []
        return [ev for y in years if w[0] <= y <= w[1] and in_terms(r, y) for ev in pool[y]]
    order = sorted(recs, key=lambda pid: (0 if recs[pid].get("tag") else 1, len(cands(pid))))
    for pid in order:
        r = recs[pid]; w = wins[pid]
        best = None
        for ev in cands(pid):
            key = ev["t"].lower()
            if key in used: continue
            mid = (w[0] + w[1]) / 2.0
            rank = (ev["s"], -abs(ev["y"] - mid))
            if best is None or rank > best[0]: best = (rank, ev)
        if not best or best[0][0] < -2:      # nothing worth showing: leave the box out rather than show church business
            r["ev"] = None; continue
        ev = best[1]; used.add(ev["t"].lower())
        rel = "During this tenure" if not (r["c"] == "grey") else "In his lifetime"
        if r.get("b") and ev["y"] >= r["b"] and (r.get("d") is None or ev["y"] <= r["d"]):
            rel += ", at about age %d" % (ev["y"] - r["b"])
        yr = ("%d BC" % -ev["y"]) if ev["y"] <= 0 else str(ev["y"])
        r["ev"] = [yr, ev["t"], ev["l"], rel]
