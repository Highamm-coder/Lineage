"""'Follow the line back': how each line is traced, exported to data/trace.json.

A trace follows succession in office (each holder's predecessor in the same see). Where a line's charted list
begins, it either joins another line at a recorded historical act, or ends with the see's founding tradition,
told in the church's own words. Consecration lineages are deliberately not used.

For each line id:
  office      plural office name, used in folded runs ("41 archbishops of Canterbury")
  church      the see, for crossing captions ("from Rome to Canterbury")
  join        [person id to continue from, year, sentence, optional year label] - a recorded act linking this line to an older one
  begins      sentence shown where the trace starts, when there is no join
  gap         sentence for holders missing from the charted list at its start (optional)
  early       holders who took office before this year are marked "names and dates from early lists"
  markers     [year, sentence] events drawn as dashed rules where the traced span crosses them
Founders' columns (Protestant) and Jesus are never traced.
"""

NO_TRACE = {"lutheran", "reformed", "free", "grey", "root"}
ALIAS = {"tec:Samuel_Seabury": "tec:Samuel_Seabury_(bishop)"}   # the 1784 card is the same man as the second presiding bishop

TRACE = {
 "catholic": dict(office="bishops of Rome", church="Rome", early=189,
     begins="The Church of Rome counts St Peter, an apostle of Jesus of Nazareth, as its first bishop.",
     markers=[[451, "Council of Chalcedon; the churches that do not accept it part from Rome and Constantinople."],
              [1054, "Papal legates and the Patriarch of Constantinople excommunicate each other; the division deepens over later centuries."]]),
 "orthodox": dict(office="patriarchs of Constantinople", church="Constantinople", early=314,
     begins="The Church of Constantinople counts St Andrew, an apostle of Jesus of Nazareth, as its founder.",
     gap="The bishops of Byzantium before Alexander (c. 314) are not charted here; those before Metrophanes (c. 306) are known only from later lists.",
     markers=[[451, "Council of Chalcedon; the churches that do not accept it part from Rome and Constantinople."],
              [1054, "Papal legates and the Patriarch of Constantinople excommunicate each other; the division deepens over later centuries."]]),
 "anglican": dict(office="archbishops of Canterbury", church="Canterbury",
     join=["catholic:Pope_Gregory_I", 597, "Augustine, sent from Rome by Pope Gregory I, arrives in Kent."],
     markers=[[1534, "England breaks with Rome; communion is restored under Mary I (1554&ndash;1558), then broken again."]]),
 "coptic": dict(office="popes of Alexandria", church="Alexandria (Coptic)", early=188,
     begins="The Coptic Orthodox Church counts St Mark the Evangelist as the founder of the Church of Alexandria.",
     markers=[[451, "Council of Chalcedon; the Church of Alexandria divides over it."]]),
 "alexandria": dict(office="patriarchs of Alexandria", church="Alexandria (Greek)",
     join=["coptic:Cyril_of_Alexandria", 444, "The Greek and Coptic churches of Alexandria share one list of patriarchs until Cyril (d. 444); they divide over his successor Dioscorus and the Council of Chalcedon (451)."],
     gap="The patriarchs of the Greek line between 444 and 536 are not charted here."),
 "syriac": dict(office="patriarchs of Antioch (Syriac)", church="Antioch (Syriac)",
     begins="The Syriac Orthodox Church counts St Peter as the founder of the Church of Antioch.",
     gap="The patriarchs of Antioch before Severus (512) are not charted here."),
 "antioch": dict(office="patriarchs of Antioch", church="Antioch",
     begins="The Church of Antioch counts St Peter as its founder.",
     gap="The patriarchs of Antioch before 519 are not charted here."),
 "jerusalem": dict(office="patriarchs of Jerusalem", church="Jerusalem",
     begins="The Church of Jerusalem counts St James, called the brother of the Lord, as its first bishop.",
     gap="The bishops of Jerusalem before 458 are not charted here."),
 "armenian": dict(office="catholicoi of All Armenians", church="Armenia", early=390,
     begins="The Armenian Apostolic Church counts the apostles Thaddeus and Bartholomew as its founders."),
 "ethiopian": dict(office="bishops and patriarchs of Ethiopia", church="Ethiopia",
     join=["coptic:Athanasius_of_Alexandria", 340, "Frumentius is consecrated bishop of Aksum by Athanasius of Alexandria.", "c. 340"],
     markers=[[1959, "The Ethiopian Orthodox Tewahedo Church receives its own patriarch, independent of Alexandria."]]),
 "georgia": dict(office="bishops and catholicos-patriarchs of Georgia", church="Georgia", early=500,
     begins="The Georgian Orthodox Church dates the conversion of Kartli to the preaching of St Nino, and counts John, a bishop sent by the Emperor Constantine, as its first bishop."),
 "moscow": dict(office="metropolitans and patriarchs of Moscow", church="Moscow",
     join=["orthodox:Athanasius_I_of_Constantinople", 1308, "Peter is consecrated Metropolitan of Kiev and all Rus&rsquo; in Constantinople by Patriarch Athanasius I."],
     markers=[[1448, "Russian bishops elect Jonah metropolitan without Constantinople&rsquo;s approval."],
              [1589, "Moscow is raised to a patriarchate by Jeremias II of Constantinople."]]),
 "tec": dict(office="presiding bishops of the Episcopal Church", church="the Episcopal Church",
     join=["anglican:John_Moore_(archbishop_of_Canterbury)", 1787, "William White is consecrated at Lambeth Palace by John Moore, Archbishop of Canterbury."],
     markers=[[1784, "Samuel Seabury is consecrated by bishops of the Scottish Episcopal Church, in Aberdeen."]]),
 "acna": dict(office="archbishops of the Anglican Church in North America", church="the Anglican Church in North America",
     begins="The Anglican Church in North America was formed in 2009. Its first bishops had been consecrated in the Episcopal Church, "
            "the Anglican Church of Canada, the Reformed Episcopal Church and several other Anglican provinces; its line is not traced further here."),
}
