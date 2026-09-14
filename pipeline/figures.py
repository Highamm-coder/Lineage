"""Hand-curated landmark figures for the three main lines (bios checked by the historian review)."""

# (name, meta, bio, start, end, slug, wiki)
COLS = {
 "anglican": [
  ("Augustine", "597&ndash;604 &middot; 1st", "Sent to England by Gregory I.", 597, 604, "augustine-of-canterbury", "Augustine_of_Canterbury"),
  ("Theodore of Tarsus", "668&ndash;690 &middot; 7th", "Organised the English Church.", 668, 690, None, "Theodore_of_Tarsus"),
  ("Anselm", "1093&ndash;1109 &middot; 36th", "Argued for God in the Proslogion.", 1093, 1109, "anselm-of-canterbury", "Anselm_of_Canterbury"),
  ("Thomas Becket", "1162&ndash;1170 &middot; 40th", "Murdered in his cathedral, 1170.", 1162, 1170, "thomas-becket", "Thomas_Becket"),
  ("Stephen Langton", "1207&ndash;1228 &middot; 44th", "Helped negotiate Magna Carta.", 1207, 1228, "stephen-langton", "Stephen_Langton"),
  ("Thomas Cranmer", "1533&ndash;1555 &middot; 69th", "Compiled the Book of Common Prayer.", 1533, 1555, "thomas-cranmer", "Thomas_Cranmer"),
  ("Matthew Parker", "1559&ndash;1575 &middot; 71st", "Shaped the Elizabethan Church.", 1559, 1575, "matthew-parker", "Matthew_Parker"),
  ("William Laud", "1633&ndash;1645 &middot; 76th", "Enforced ceremony; executed 1645.", 1633, 1645, "william-laud", "William_Laud"),
  ("Michael Ramsey", "1961&ndash;1974 &middot; 100th", "Met Paul VI in Rome, 1966.", 1961, 1974, "michael-ramsey", "Michael_Ramsey"),
  ("Rowan Williams", "2002&ndash;2012 &middot; 104th", "Came to Canterbury from Wales.", 2002, 2012, "rowan-williams", "Rowan_Williams"),
  ("Justin Welby", "2013&ndash;2025 &middot; 105th", "Crowned King Charles III, 2023.", 2013, 2025, "justin-welby", "Justin_Welby"),
  ("Sarah Mullally", "2026&ndash; &middot; 106th", "First woman Archbishop of Canterbury.", 2026, 2026, "sarah-mullally", "Sarah_Mullally"),
 ],
 "catholic": [
  ("St Peter", "d. c. 64, by tradition &middot; 1st", "Led the apostles; martyred in Rome.", 30, 64, "saint-peter", "Saint_Peter"),
  ("Clement I", "c. 88&ndash;c. 99 &middot; 4th", "Credited with the letter to Corinth.", 88, 99, "pope-clement-i", "Pope_Clement_I"),
  ("Leo I", "440&ndash;461 &middot; 45th", "His Tome was affirmed at Chalcedon.", 440, 461, "pope-leo-i", "Pope_Leo_I"),
  ("Gregory I", "590&ndash;604 &middot; 64th", "Sent Augustine to England, 597.", 590, 604, "pope-gregory-i", "Pope_Gregory_I"),
  ("Leo III", "795&ndash;816 &middot; 96th", "Crowned Charlemagne emperor, 800.", 795, 816, "pope-leo-iii", "Pope_Leo_III"),
  ("Leo IX", "1049&ndash;1054 &middot; 152nd", "His legates went east in 1054.", 1049, 1054, "pope-leo-ix", "Pope_Leo_IX"),
  ("Innocent III", "1198&ndash;1216 &middot; 176th", "Called the Fourth Lateran Council.", 1198, 1216, "pope-innocent-iii", "Pope_Innocent_III"),
  ("Clement VII", "1523&ndash;1534 &middot; 219th", "Refused Henry VIII&rsquo;s annulment.", 1523, 1534, "pope-clement-vii", "Pope_Clement_VII"),
  ("Pius IX", "1846&ndash;1878 &middot; 255th", "Called the First Vatican Council.", 1846, 1878, "pope-pius-ix", "Pope_Pius_IX"),
  ("Paul VI", "1963&ndash;1978 &middot; 262nd", "Lifted the 1054 anathemas, 1965.", 1963, 1978, "pope-paul-vi", "Pope_Paul_VI"),
  ("John Paul II", "1978&ndash;2005 &middot; 264th", "Travelled to 129 countries.", 1978, 2005, "pope-john-paul-ii", "Pope_John_Paul_II"),
  ("Leo XIV", "2025&ndash; &middot; 267th", "First pope from the United States.", 2025, 2026, "pope-leo-xiv", "Pope_Leo_XIV"),
 ],
 "orthodox": [
  ("St Andrew", "1st century, by tradition", "Founded the see, by tradition.", 38, 60, "andrew-the-apostle", "Andrew_the_Apostle"),
  ("Gregory of Nazianzus", "379&ndash;381", "Preached the Theological Orations.", 379, 381, "gregory-of-nazianzus", "Gregory_of_Nazianzus"),
  ("John Chrysostom", "398&ndash;404", "Preached reform; died in exile.", 398, 404, "john-chrysostom", "John_Chrysostom"),
  ("John IV the Faster", "582&ndash;595", "Took the title &lsquo;Ecumenical&rsquo;.", 582, 595, "john-iv-of-constantinople", "John_IV_of_Constantinople"),
  ("Tarasios", "784&ndash;806", "Led the Second Council of Nicaea.", 784, 806, "tarasios-of-constantinople", "Tarasios_of_Constantinople"),
  ("Photios I", "858&ndash;867, 877&ndash;886", "Challenged Rome over the Filioque.", 858, 886, "photios-i-of-constantinople", "Photios_I_of_Constantinople"),
  ("Michael I Cerularius", "1043&ndash;1058", "Condemned the papal legates, 1054.", 1043, 1058, "michael-i-cerularius", "Michael_I_Cerularius"),
  ("Gennadius Scholarius", "1454&ndash;1456", "First patriarch under the Ottomans.", 1454, 1456, "gennadius-scholarius", "Gennadius_Scholarius"),
  ("Jeremias II", "1572&ndash;1595", "Made Moscow a patriarchate, 1589.", 1572, 1595, "jeremias-ii-of-constantinople", "Jeremias_II_of_Constantinople"),
  ("Cyril Lucaris", "1620&ndash;1638", "Sent Codex Alexandrinus to England.", 1620, 1638, "cyril-lucaris", "Cyril_Lucaris"),
  ("Athenagoras I", "1948&ndash;1972", "Lifted the anathemas with Paul VI.", 1948, 1972, "athenagoras-i-of-constantinople", "Athenagoras_I_of_Constantinople"),
  ("Bartholomew I", "1991&ndash;", "First among equals in Orthodoxy.", 1991, 2026, "bartholomew-i-of-constantinople", "Bartholomew_I_of_Constantinople"),
 ],
}
ORDER = ["anglican", "catholic", "orthodox"]
HEAD = {
 "anglican": ("Anglican", "Archbishops of Canterbury", "Canterbury"),
 "catholic": ("Catholic", "Bishops of Rome", "Rome"),
 "orthodox": ("Orthodox", "Patriarchs of Constantinople", "Constantinople"),
}
JESUS = ("Jesus of Nazareth", "c. 4 BC &ndash; c. AD 33", "The Church traces itself to him.", "jesus", "Jesus")
