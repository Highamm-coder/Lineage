"""Hand corrections to the cached source data, applied every time site.py loads it.

The registers and lifespans come from Wikipedia and Wikidata and contain some errors. Fixes live here, not in
data/*.json, so refreshing the source data (fetch_people.py, family_links.py) never undoes them.
Each entry notes its reason; most were found by the historian while checking the weekly emails.
"""

# Register rows: (line key, row index, the name currently at that index) -> what to do.
# Indices refer to the rows as fetched; the name check stops a correction landing on the wrong row after a refresh.
ROWS = [
    # Maximus the Cynic was consecrated in rivalry to Gregory; the Council of Constantinople (381) declared his
    # consecration invalid, so Gregory's successor is Nectarius. Kept as a note on the chart instead (views.py).
    ("constantinople", 11, "Maximus I", "drop"),
    # Two different men were both shown as "Sahak I": Shahak of Manazkert (373-377) and Sahak the Great (c. 387-428).
    ("armenian", 18, "Sahak I", {"name": "Shahak of Manazkert"}),
    ("armenian", 21, "Sahak I", {"name": "Sahak I the Great"}),
    # Melchizedek I held office c. 1010-1033 (the register gave 1001-1030); his successor's first term starts after him.
    ("georgia", 63, "Melkisedek I", {"start": 1010, "end": 1033}),
    ("georgia", 64, "Okropir (Ioane) II", {"start": 1033}),
]

# Rows missing from a register: (line key, insert before this index, the name currently there, row, Wikipedia title)
INSERTS = [
    # Modestus (d. 634) was succeeded by Sophronius, not Anastasius II; the see was then vacant for decades.
    ("jerusalem", 13, "Anastasius II", {"name": "Sophronius I", "start": 634, "end": 638, "num": ""}, "Sophronius_of_Jerusalem"),
]

# Lifespans by Wikidata id: replaces the fetched values. b/d are years; bc/dc mark "c."; age overrides "aged about".
LIFE = {
    "Q243187": dict(b=815, bc=True, d=891, dc=True),     # Photios I: born c. 810-820, died c. 891-893 (not 827 / 891)
    "Q3057500": dict(b=None, bc=False, d=634, dc=False),  # Modestus of Jerusalem: birth year 537 is hagiography
    "Q251060": dict(b=None, bc=False, d=383, dc=True),    # Frumentius: died c. 383, birth unknown (not born 310, died 380)
    "Q442737": dict(b=None, bc=False, d=595, dc=False),   # John IV the Faster: "born c. 600" is after his death
    "Q32520": dict(b=None, bc=False, d=604, dc=True),     # Augustine of Canterbury: birth unknown; died c. 604
    "Q729105": dict(b=None, bc=False, d=538, dc=False),   # Severus of Antioch: born c. 465, not 456
    "Q497497": dict(b=None, bc=False, d=None, dc=False),  # Athanasius II of Constantinople: "born c. 1500" is impossible
    # Apostles and Jesus: Wikidata's placeholder years (Peter "born 1 BC", Bartholomew "born c. 100 BC") dropped;
    # deaths given as tradition dates them. Jesus matches the chart card (c. 4 BC - c. AD 33).
    "Q33923": dict(b=None, bc=False, d=64, dc=True),      # St Peter: died c. 64-68 in Rome, by tradition
    "Q43399": dict(b=None, bc=False, d=60, dc=True),      # St Andrew: died c. 60, by tradition
    "Q43982": dict(b=None, bc=False, d=70, dc=True),      # St Bartholomew: died c. 69-71, by tradition
    "Q302": dict(b=-4, bc=True, d=33, dc=True),           # Jesus of Nazareth
    "Q9554": dict(b=1483, bc=False, d=1546, dc=False, age=62),    # Martin Luther: 10 Nov 1483 - 18 Feb 1546
    "Q318622": dict(b=1491, bc=False, d=1551, dc=False, age=59),  # Martin Bucer: 11 Nov 1491 - 28 Feb 1551
}

# Lifespans by the person's Wikipedia title, for people Wikidata did not supply
LIFE_BY_TITLE = {
    "Eulogius_I_of_Alexandria": dict(b=None, bc=False, d=608, dc=False),   # "born c. 501" would make him 80 at election
}


def apply(lines, main_links, fam_links, life, bios):
    def links_for(key):
        return main_links.get(key) if key in main_links else fam_links.get(key)
    for key, i, name, fix in ROWS:
        rows = lines[key]["rows"]
        if i >= len(rows) or rows[i]["name"] != name:
            raise SystemExit("corrections.py: %s row %d is no longer %r; update the index" % (key, i, name))
    # apply edits before drops, and drops from the end, so indices stay valid
    for key, i, name, fix in ROWS:
        if fix != "drop": lines[key]["rows"][i].update(fix)
    for key, i, name, fix in sorted([r for r in ROWS if r[3] == "drop"], key=lambda r: -r[1]):
        del lines[key]["rows"][i]
        lk = links_for(key)
        if lk is not None and i < len(lk): del lk[i]
    for key, i, name, row, title in sorted(INSERTS, key=lambda r: -r[1]):
        rows = lines[key]["rows"]
        if rows[i]["name"] != name:
            raise SystemExit("corrections.py: %s row %d is no longer %r; update the index" % (key, i, name))
        rows.insert(i, dict(row))
        lk = links_for(key)
        if lk is not None:
            while len(lk) < i: lk.append(None)
            lk.insert(i, title)
    for qid, v in LIFE.items():
        life[qid] = dict(v)
    for title, v in LIFE_BY_TITLE.items():
        b = bios.get(title.replace("_", " "))
        if b is not None:
            qid = b.get("qid") or ("title:" + title)
            b["qid"] = qid
            life[qid] = dict(v)
