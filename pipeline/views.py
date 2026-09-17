"""Every page the site builds, and the lines each one shows.

A column is a dict:
  id      pid prefix and default colour token (people shared across pages keep one id)
  key     register key in data/lines.json (None for founder-only columns)
  links   which link file maps register rows to Wikipedia: "main" (holder_links.json) or "family" (family_links.json)
  title / sub / see   header, sub-header, and the short see name used on mobile
  office  noun used in the person dialog ("Bishop of Rome")
  line    label used at the top of the person dialog
  hue     colour token (defaults to id); "grey" for context columns
  numbered   show ordinals from the register
  spine   draw the continuous line (False for founders: no single succession)
  cards   "curated" (figures.COLS[id]), "auto" (picked from the register), or a list of founder cards
  since   first century shown (earlier centuries collapse into one row pointing back to the main chart)
"""

CANTERBURY = dict(id="anglican", key="canterbury", links="main", title="Anglican", sub="Archbishops of Canterbury",
                  see="Canterbury", office="Archbishop of Canterbury", line="Anglican &middot; Archbishops of Canterbury",
                  numbered=True, spine=True, cards="curated")
ROME = dict(id="catholic", key="rome", links="main", title="Catholic", sub="Bishops of Rome", see="Rome",
            office="Bishop of Rome", line="Catholic &middot; Bishops of Rome", numbered=True, spine=True, cards="curated")
CONSTANTINOPLE = dict(id="orthodox", key="constantinople", links="main", title="Orthodox", sub="Patriarchs of Constantinople",
                      see="Constantinople", office="Patriarch of Constantinople",
                      line="Orthodox &middot; Patriarchs of Constantinople", numbered=False, spine=True, cards="curated")

def reg(id, key, title, sub, see, office, line, numbered=False):
    return dict(id=id, key=key, links="family", title=title, sub=sub, see=see, office=office, line=line,
                numbered=numbered, spine=True, cards="auto")

MOSCOW = reg("moscow", "moscow", "Russian Orthodox", "Metropolitans and Patriarchs of Moscow", "Moscow",
             "Primate of the Russian Church", "Russian Orthodox &middot; Moscow")
ANTIOCH = reg("antioch", "antioch", "Antioch", "Greek Orthodox Patriarchs of Antioch", "Antioch",
              "Greek Orthodox Patriarch of Antioch", "Orthodox &middot; Patriarchs of Antioch")
GEORGIA = reg("georgia", "georgia", "Georgian Orthodox", "Catholicos-Patriarchs of All Georgia", "Georgia",
              "Catholicos-Patriarch of Georgia", "Georgian Orthodox &middot; Catholicos-Patriarchs")
JERUSALEM = reg("jerusalem", "jerusalem", "Jerusalem", "Greek Orthodox Patriarchs of Jerusalem", "Jerusalem",
                "Greek Orthodox Patriarch of Jerusalem", "Orthodox &middot; Patriarchs of Jerusalem")
ALEXANDRIA = reg("alexandria", "alexandria_gr", "Alexandria", "Greek Orthodox Patriarchs of Alexandria", "Alexandria",
                 "Greek Orthodox Patriarch of Alexandria", "Orthodox &middot; Patriarchs of Alexandria")
COPTIC = reg("coptic", "coptic", "Coptic Orthodox", "Popes of Alexandria", "Coptic", "Coptic Pope of Alexandria",
             "Coptic Orthodox &middot; Popes of Alexandria", numbered=True)
SYRIAC = reg("syriac", "syriac", "Syriac Orthodox", "Patriarchs of Antioch", "Syriac", "Syriac Orthodox Patriarch of Antioch",
             "Syriac Orthodox &middot; Patriarchs of Antioch")
ARMENIAN = reg("armenian", "armenian", "Armenian Apostolic", "Catholicoi of All Armenians", "Armenian",
               "Catholicos of All Armenians", "Armenian Apostolic &middot; Catholicoi")
ETHIOPIAN = reg("ethiopian", "ethiopia", "Ethiopian Orthodox", "Patriarchs and Abunas of Ethiopia", "Ethiopian",
                "Abuna of Ethiopia", "Ethiopian Orthodox &middot; Abunas and Patriarchs")
TEC = reg("tec", "tec", "The Episcopal Church", "Presiding Bishops", "Episcopal", "Presiding Bishop of the Episcopal Church",
          "Episcopal Church &middot; Presiding Bishops", numbered=True)
ACNA = reg("acna", "acna", "ACNA", "Archbishops of the Anglican Church in North America", "ACNA",
           "Archbishop of the Anglican Church in North America", "ACNA &middot; Archbishops", numbered=True)
ACNA["plain_bio"] = True      # title and dates only (the archbishop's status must be re-checked before any publish)

# Founder cards: (name, meta, bio, year of defining act, end, portrait slug, wiki title, stream)
def F(name, life, stream, bio, year, slug, wiki):
    return (name, "%s &middot; %s" % (life, stream), bio, year, year, slug, wiki)

LUTHERAN = dict(id="lutheran", key=None, title="Lutheran", sub="Reformers and movements &middot; no single succession",
                see="Lutheran", office="", line="Protestant &middot; Lutheran", spine=False, cards=[
  F("Martin Luther", "1483&ndash;1546", "Lutheran", "Posted the Ninety-five Theses, 1517.", 1517, "martin-luther", "Martin_Luther"),
  F("Philipp Melanchthon", "1497&ndash;1560", "Lutheran", "Drafted the Augsburg Confession, 1530.", 1530, "philip-melanchthon", "Philip_Melanchthon"),
  F("Laurentius Petri", "1499&ndash;1573", "Lutheran", "First Lutheran Archbishop of Uppsala.", 1531, "h-laurentius-petri", "Laurentius_Petri"),
  F("Nicolaus Zinzendorf", "1700&ndash;1760", "Moravian", "Renewed the Moravian Church, 1727.", 1727, "nicolaus-zinzendorf", "Nicolaus_Zinzendorf"),
  F("Dietrich Bonhoeffer", "1906&ndash;1945", "Lutheran", "Resisted Hitler; executed in 1945.", 1934, "h-dietrich-bonhoeffer", "Dietrich_Bonhoeffer"),
])
REFORMED = dict(id="reformed", key=None, title="Reformed", sub="Reformers and movements &middot; no single succession",
                see="Reformed", office="", line="Protestant &middot; Reformed and Presbyterian", spine=False, cards=[
  F("Huldrych Zwingli", "1484&ndash;1531", "Reformed", "Led the Reformation in Zurich.", 1519, "huldrych-zwingli", "Huldrych_Zwingli"),
  F("Martin Bucer", "1491&ndash;1551", "Reformed", "Led reform in Strasbourg.", 1523, "h-martin-bucer", "Martin_Bucer"),
  F("Heinrich Bullinger", "1504&ndash;1575", "Reformed", "Succeeded Zwingli in Zurich, 1531.", 1531, "h-heinrich-bullinger", "Heinrich_Bullinger"),
  F("John Calvin", "1509&ndash;1564", "Reformed", "Wrote the Institutes, 1536.", 1536, "john-calvin", "John_Calvin"),
  F("John Knox", "c. 1514&ndash;1572", "Presbyterian", "Led the Scottish Reformation, 1560.", 1560, "john-knox", "John_Knox"),
  F("Theodore Beza", "1519&ndash;1605", "Reformed", "Succeeded Calvin in Geneva, 1564.", 1564, "theodore-beza", "Theodore_Beza"),
  F("Jacob Arminius", "1560&ndash;1609", "Reformed", "Challenged Calvinist predestination.", 1603, "h-jacob-arminius", "Jacob_Arminius"),
])
FREE = dict(id="free", key=None, title="Free churches", sub="Anabaptist, Baptist, Quaker, Methodist, Pentecostal",
            see="Free church", office="", line="Protestant &middot; Free churches", spine=False, cards=[
  F("Menno Simons", "1496&ndash;1561", "Anabaptist", "Gathered the scattered Anabaptists.", 1536, "menno-simons", "Menno_Simons"),
  F("Thomas Helwys", "c. 1575&ndash;c. 1616", "Baptist", "Founded England's first Baptist church.", 1612, None, "Thomas_Helwys"),
  F("George Fox", "1624&ndash;1691", "Quaker", "Began the Quaker movement, 1652.", 1652, "george-fox", "George_Fox"),
  F("John Wesley", "1703&ndash;1791", "Methodist", "Began Methodism as an Anglican priest.", 1738, "john-wesley", "John_Wesley"),
  F("William Carey", "1761&ndash;1834", "Baptist", "Sailed as a missionary to India, 1793.", 1793, "h-william-carey-missionary", "William_Carey_(missionary)"),
  F("Richard Allen", "1760&ndash;1831", "Methodist", "Founded the AME Church, 1816.", 1816, "h-richard-allen-bishop", "Richard_Allen_(bishop)"),
  F("William Booth", "1829&ndash;1912", "Salvation Army", "Began The Salvation Army's work, 1865.", 1865, "william-booth", "William_Booth"),
  F("Pandita Ramabai", "1858&ndash;1922", "Evangelical", "Founded the Mukti Mission in India.", 1889, "h-pandita-ramabai", "Pandita_Ramabai"),
  F("William J. Seymour", "1870&ndash;1922", "Pentecostal", "Led the Azusa Street Revival, 1906.", 1906, "william-j-seymour", "William_J._Seymour"),
  F("William Wad&eacute; Harris", "c. 1860&ndash;1929", "Evangelical", "Preached across West Africa, 1913.", 1913, "h-william-wad-harris", "William_Wad%C3%A9_Harris"),
  F("Billy Graham", "1918&ndash;2018", "Evangelical", "Preached to millions on six continents.", 1949, "billy-graham", "Billy_Graham"),
  F("Martin Luther King Jr.", "1929&ndash;1968", "Baptist", "Led the US civil rights movement.", 1955, "h-martin-luther-king-jr", "Martin_Luther_King_Jr."),
])

MAIN_NOTES = [
 ("catholic", 31, "", "Early names and dates follow later tradition."),
 ("orthodox", 39, "", "Bishops before Metrophanes (c. 306) are known from later lists."),
 ("orthodox", 380, "380", "Maximus the Cynic was consecrated as a rival to Gregory; the Council of 381 declared his consecration invalid."),
 ("orthodox", 1450, "1450&ndash;1453", "Athanasius II is known from a single disputed source; many historians count Gregory III, in Rome from 1451, as nominal patriarch until 1453."),
 ("catholic", 1268, "1268&ndash;1271", "The see stood vacant for nearly three years."),
 ("orthodox", 1204, "1204&ndash;1261", "The Latin Empire held the city; patriarchs reigned from Nicaea."),
 ("catholic", 1378, "1378&ndash;1417", "Rival popes at Avignon (from 1378) and Pisa (from 1409); this list follows the Roman line."),
 ("anglican", 1554, "1554&ndash;1558", "England reconciled with Rome under Mary I; Pole the last archbishop in communion with the Pope."),
 ("anglican", 1645, "1645&ndash;1660", "No archbishop after Laud&rsquo;s execution; episcopacy abolished 1646."),
 ("anglican", 2025, "2025", "Vacant after Welby&rsquo;s resignation."),
]

SPLITS_MAIN = [
 (451, None),   # the ring row: Oriental Orthodox churches
 (1054, "Catholic and Orthodox divide: Rome and Constantinople exchange excommunications."),
 (1534, "Anglican and Catholic divide: Henry VIII made head of the English Church."),
]

# rings on the main chart: (column id or None for the 451 axis, year, label, page)
RINGS = [
 (None, 451, "Oriental Orthodox churches", "oriental-orthodox.html",
  "After 451, churches rejecting Chalcedon parted from Rome and Constantinople alike."),
 ("catholic", 1517, "Protestant churches", "protestant.html", None),
 ("orthodox", 1589, "Orthodox churches", "orthodox.html", None),
 ("anglican", 1784, "Anglican churches in North America", "anglican-north-america.html", None),
]

VIEWS = {
 "main": dict(file="index.html", cols=[CANTERBURY, ROME, CONSTANTINOPLE], root=True, splits=SPLITS_MAIN,
              notes=MAIN_NOTES, rings=RINGS),
 "oriental": dict(file="oriental-orthodox.html", title="Oriental Orthodox churches", ring_id="ring-oriental",
     origin="After 451, churches rejecting the Council of Chalcedon parted from Rome and Constantinople alike. "
            "Armenia&rsquo;s church rejected the council later, in 506.",
     cols=[COPTIC, SYRIAC, ARMENIAN], variants={"ethiopian": ETHIOPIAN}, variant_slot=2),
 "orthodox": dict(file="orthodox.html", title="Orthodox churches", ring_id="ring-orthodox",
     origin="Moscow became a patriarchate in 1589; Georgia&rsquo;s church is independent by ancient tradition "
            "(recognised by Constantinople in 1990); Jerusalem, Antioch and Alexandria are older sees of equal standing.",
     cols=[dict(CONSTANTINOPLE, hue="grey", context=True), MOSCOW, ANTIOCH],
     variants={"georgia": GEORGIA, "jerusalem": JERUSALEM, "alexandria": ALEXANDRIA}, variant_slot=2,
     notes=[("moscow", 1589, "1589", "Raised to a patriarchate by Jeremias II of Constantinople.")]),
 "protestant": dict(file="protestant.html", title="Protestant churches", ring_id="ring-protestant",
     origin="From 1517, reformers sought to renew the one Church; Rome excommunicated Luther in 1521. "
            "Protestants find continuity in Scripture and faith rather than in a line of bishops, so these columns "
            "show founders and movements, not successions.",
     cols=[LUTHERAN, REFORMED, FREE], since=16),
 "anglican-na": dict(file="anglican-north-america.html", title="Anglican churches in North America", ring_id="ring-anglican-na",
     origin="American Anglicans organised after independence; Samuel Seabury was consecrated by Scottish bishops in 1784. "
            "The Anglican Church in North America was formed in 2009 by Anglicans who left the Episcopal Church and the "
            "Anglican Church of Canada; it is recognised by GAFCON provinces, not by the Anglican Communion&rsquo;s official bodies.",
     cols=[dict(CANTERBURY, hue="grey", context=True), TEC, ACNA], since=18,
     extra_cards={"tec": [("Samuel Seabury", "1784&ndash;1796 &middot; first American bishop",
                           "Consecrated by Scottish bishops, 1784.", 1784, 1796, "samuel-seabury", "Samuel_Seabury")]}),
}
