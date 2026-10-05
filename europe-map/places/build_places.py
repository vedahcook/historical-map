# Places: landmarks that are not cities on the map (battlefields, abbeys, castles, camps...), chosen as central to a
# country's history. They show on the map when you highlight a country whose story they belong to, and only where
# that country held them in the year on the map. Ranked in tiers (1 = shown first), so zooming in brings in more,
# the way cities work. Trial for France and Poland, October 5, 2026 (Project doc claude/city-views-pilot.md).
#   cd europe-map && python3 places/build_places.py        (writes places.json; needs pyproj and shapely)
# Descriptions are written from each place's English Wikipedia article; pictures are Wikidata's (P18) unless noted.
import json, sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cities'))
from place_cities import page_data, Placer

# country stories: the map's countries (unit keys) that make up each country as people know it, across the years.
# A unit also belongs if its overlord (U.ov) is in the list (France's medieval fiefs, for example).
STORIES = {
    'France': ['FRA', 'BRI', 'PRV', 'LOR', 'FCM', 'O_GER_FRA', 'A_GER_FRA', 'O_ITA_FRA', 'BNF'],
    'Poland': ['PLK', 'PLC', 'POL_I', 'WAR', 'POL', 'KRA', 'GPL', 'LPL', 'MAZ', 'MAZ_P', 'SIL', 'GGV', 'A_GER_POL_I', 'O_GER_POL_I',
               'O_GER_POL', 'O_AUT_POL', 'POL_R'],
}

# threads: larger stories a place belongs to; each item is a place (its id) or a city's event ([city index, Wikidata id])
THREADS = {
    'angevin': ('Capetian kings against the Plantagenets', ['gaillard', 'bouvines']),
    'cathars': ('Albigensian Crusade', [[1052, 'Q941312'], [1956, 'Q3485852'], 'montsegur']),
    'hyw': ("Hundred Years' War", ['crecy', [181, 'Q676340'], 'poitiers1356', 'agincourt', [178, 'Q392213'], [106, 'Q4201115'], 'msm', 'castillon']),
    'monks': ('Great abbeys', ['cluny', 'msm']),
    'revwars': ('French Revolutionary Wars', [[4131, 'Q572883'], 'valmy']),
    'ww1fr': ('World War I in France', ['marne', [4131, 'Q130847'], 'somme', [2241, 'Q253224']]),
    'ww2fr': ('World War II in France', [[4069, 'Q269207'], [443, 'Q911972'], 'normandy', 'oradour']),
    'teutonic': ('Wars with the Teutonic Knights', ['plowce', 'grunwald', [2443, 'Q653582'], 'malbork']),
    'kosciuszko': ('Kościuszko Uprising', ['raclawice', [9, 'Q2591793'], 'maciejowice', [9, 'Q1347209']]),
    'inv1939': ('German invasion of Poland, 1939', [[74, 'Q533034'], 'wizna', [1947, 'Q165549'], [9, 'Q182240']]),
    'holocaust': ('The Holocaust in occupied Poland', [[9, 'Q154607'], 'auschwitz', 'treblinka', 'sobibor', [9, 'Q160161']]),
}

# id, name, kind (icon), what it is, when (label), map year to show, tier, stories, Wikipedia title, Wikidata id,
# Wikipedia language editions, lon, lat, picture [file, width, height, author, license, md5 folder] or None, description
P = [
    ('msm', 'Mont-Saint-Michel', 'religion', 'Abbey on a tidal island', '', 1433, 1, ['France'], 'Mont-Saint-Michel', 'Q20892', 86, -1.5102778, 48.6358333,
     ['Mont St Michel 3, Brittany, France - July 2011.jpg', 2811, 1993, 'Diliff', 'Public domain', 'd1'],
     "A tidal island off the Normandy coast, crowned by an abbey that drew pilgrims for centuries. It was never taken in the Hundred Years' War: in 1433 a small garrison drove off a full English attack."),
    ('cluny', 'Cluny Abbey', 'religion', 'Benedictine abbey', 'founded 910', 1100, 3, ['France'], 'Cluny Abbey', 'Q220301', 50, 4.659221, 46.434051,
     None,      # (Wikidata's picture has no author to credit)
     "This Benedictine abbey led a reform movement that spread to monasteries across Western Europe. Its last church was the largest in the world until St. Peter's in Rome; most of the abbey was destroyed in 1790."),
    ('gaillard', 'Château Gaillard', 'war', 'Siege', '1203–1204', 1204, 3, ['France'], 'Siege of Château Gaillard', 'Q7509935', 6, 1.40333333, 49.23777778,
     ['ChatoGaillardPano1.jpg', 4589, 1584, 'Urban', 'CC BY-SA 3.0', '47'],
     "King Philip II of France besieged this Norman fortress on the Seine, held for King John of England, for six months. Its fall opened the way to the French conquest of Normandy."),
    ('bouvines', 'Battle of Bouvines', 'war', 'Battle', 'July 27, 1214', 1214, 2, ['France'], 'Battle of Bouvines', 'Q830626', 32, 3.225, 50.58,
     ['Bataille de Bouvines gagnee par Philippe Auguste.jpg', 2482, 1222, 'Horace Vernet', 'Public domain', 'f2'],
     "King Philip II of France routed a larger alliance, led by Emperor Otto IV and backed by King John of England, that had set out to undo his conquests. It was one of the most decisive battles of the Middle Ages."),
    ('montsegur', 'Montségur', 'war', 'Siege', '1243–1244', 1244, 3, ['France'], 'Siege of Montségur', 'Q2750233', 9, 1.8325, 42.8755556,
     ['Heretics of Montsegur, 1244 (É. Bayard).png', 723, 958, 'Émile Bayard', 'Public domain', 'b0'],
     "Royal and church forces besieged this mountain castle, the stronghold of the Cathar church, for nine months. After it surrendered, about 210 Cathars were burned at the foot of the mountain."),
    ('crecy', 'Battle of Crécy', 'war', 'Battle', 'August 26, 1346', 1346, 2, ['France'], 'Battle of Crécy', 'Q27759', 50, 1.88777778, 50.25638889,
     ['Battle of crecy froissart.jpg', 1998, 1755, 'Loyset Liédet', 'Public domain', '24'],
     "King Edward III's outnumbered English army, holding a hillside, cut down wave after wave of French cavalry with its archers. The French suffered heavy losses in one of England's greatest victories of the Hundred Years' War."),
    ('poitiers1356', 'Battle of Poitiers', 'war', 'Battle', 'September 19, 1356', 1356, 3, ['France'], 'Battle of Poitiers', 'Q201692', 51, 0.40333333, 46.52222222,
     ['Battle-poitiers(1356).jpg', 1658, 1446, 'Loyset Liédet', 'Public domain', '21'],
     "An Anglo-Gascon army under Edward the Black Prince, fighting on foot, beat back a much larger French army south of Poitiers. King John II of France was taken prisoner."),
    ('agincourt', 'Battle of Agincourt', 'war', 'Battle', 'October 25, 1415', 1415, 1, ['France'], 'Battle of Agincourt', 'Q188495', 59, 2.14166667, 50.46361111,
     ["Battle of Agincourt, St. Alban's Chronicle by Thomas Walsingham.jpg", 1500, 1249, "Illuminator of the St. Albans Chronicle", 'Public domain', 'b9'],
     "Henry V's outnumbered English army, weakened by disease and made up mostly of archers, crushed a far larger French army. It began 14 years of English dominance in the war, until the French relieved Orléans in 1429."),
    ('castillon', 'Battle of Castillon', 'war', 'Battle', 'July 17, 1453', 1453, 2, ['France'], 'Battle of Castillon', 'Q932613', 32, -0.01888889, 44.85166667,
     ['Battle of Castillon.jpg', 743, 1200, 'Charles-Philippe Larivière', 'Public domain', '5c'],
     "French artillery destroyed an English attack on a fortified French camp, the first major battle in Europe won through the extensive use of field artillery. England lost nearly all its lands in France, ending the Hundred Years' War."),
    ('chambord', 'Château de Chambord', 'castle', 'Royal château', 'built 1519–1547', 1539, 3, ['France'], 'Château de Chambord', 'Q205367', 54, 1.51722222, 47.61611111,
     ['France Loir-et-Cher Chambord Chateau 03.jpg', 2258, 1686, 'Calips', 'CC BY-SA 3.0', '80'],
     "Francis I built this hunting lodge, the largest château in the Loire Valley, as a show of wealth and power. Its design blends French medieval forms with the Italian Renaissance; Leonardo da Vinci may have influenced it."),
    ('valmy', 'Battle of Valmy', 'war', 'Battle', 'September 20, 1792', 1792, 2, ['France'], 'Battle of Valmy', 'Q4411', 39, 4.76722222, 49.08027778,
     ['Valmy Battle painting.jpg', 6926, 4226, 'Horace Vernet', 'Public domain', 'c8'],
     "The armies of revolutionary France stopped a Prussian march on Paris. The unexpected victory saved the Revolution and emboldened the new National Convention to end the monarchy and declare France a republic."),
    ('marne', 'First Battle of the Marne', 'war', 'Battle', 'September 5–12, 1914', 1914, 1, ['France'], 'First Battle of the Marne', 'Q190712', 56, 3.38333333, 49.01666667,
     ['German soldiers Battle of Marne WWI.jpg', 501, 548, 'German Army', 'Public domain', '3b'],
     "French and British armies turned on the German forces that had come within 25 miles of Paris and drove them back. Remembered in France as the \"Miracle on the Marne,\" it wrecked Germany's plan to win the war in 40 days."),
    ('somme', 'Battle of the Somme', 'war', 'Battle', 'July 1–November 18, 1916', 1916, 2, ['France'], 'Battle of the Somme', 'Q132568', 66, 2.6975, 50.01555556,
     ['British Mark I male tank Somme 25 September 1916.jpg', 3503, 2480, 'Ernest Brooks', 'Public domain', 'f6'],
     "British and French armies attacked German lines along the river for four and a half months. More than a million men were killed or wounded, making it one of the deadliest battles in history."),
    ('normandy', 'Normandy landings', 'war', 'Landings', 'June 6, 1944', 1944, 1, ['France'], 'Normandy landings', 'Q16470', 71, -0.6, 49.34,
     ['Into the Jaws of Death 23-0455M edit.jpg', 2963, 2385, "Robert F. Sargent, U.S. Coast Guard", 'Public domain', 'a5'],
     "On D-Day, Allied troops landed by sea and air on the beaches of Normandy, the largest seaborne invasion in history. It began the liberation of France and the rest of Western Europe."),
    ('oradour', 'Oradour-sur-Glane', 'memorial', 'Massacre', 'June 10, 1944', 1944, 2, ['France'], 'Oradour-sur-Glane massacre', 'Q836897', 31, 1.041, 45.928,
     ['Oradour-sur-Glane-Streets-1290.jpg', 2048, 1536, 'Dna-Dennis', 'Public domain', 'b0'],
     "Four days after D-Day, an SS company destroyed this village and murdered 642 men, women and children in reprisal for Resistance activity. Only six people are known to have survived."),
    # Poland
    ('legnica', 'Battle of Legnica', 'war', 'Battle', 'April 9, 1241', 1241, 2, ['Poland'], 'Battle of Legnica', 'Q159512', 42, 16.22277778, 51.14527778,
     ['Bitwa pod Legnicą.jpg', 614, 480, 'Matthäus Merian', 'Public domain', '43'],
     "A Mongol army crushed the Polish and Moravian forces of Duke Henry II the Pious of Silesia, who had tried to stop the Mongol invasion of Poland. Henry was killed in the battle."),
    ('plowce', 'Battle of Płowce', 'war', 'Battle', 'September 27, 1331', 1331, 3, ['Poland'], 'Battle of Płowce', 'Q1049697', 12, 18.6439, 52.6156,
     ['Płowce 1331 Juliusz Kossak.jpeg', 800, 423, 'Juliusz Kossak', 'Public domain', '33'],
     "King Władysław the Elbow-high caught part of a Teutonic army leaving Poland and won a hard fight, briefly capturing its marshal. Teutonic reinforcements then arrived, and he withdrew at nightfall."),
    ('grunwald', 'Battle of Grunwald', 'war', 'Battle', 'July 15, 1410', 1410, 1, ['Poland'], 'Battle of Grunwald', 'Q33570', 69, 20.12472222, 53.48611111,
     ['Jan Matejko, Bitwa pod Grunwaldem.jpg', 11788, 5235, 'Jan Matejko', 'Public domain', '38'],      # (the whole painting, not Wikidata's detail)
     "Poland and Lithuania, led by King Władysław II Jagiełło and Grand Duke Vytautas, crushed the Teutonic Knights in one of the largest battles of medieval Europe. The order never recovered its former power."),
    ('malbork', 'Malbork Castle', 'castle', 'Castle of the Teutonic Order', 'built about 1274–1406', 1457, 1, ['Poland'], 'Malbork Castle', 'Q71279', 56, 19.02777778, 54.03972222,
     ['Panorama of Malbork Castle, part 4.jpg', 4138, 2706, 'DerHexer; derivative work: Carschten', 'CC BY-SA 3.0', '82'],
     "Built by the Teutonic Knights, it is the largest castle in the world by area. Unpaid Bohemian mercenaries sold it to the King of Poland in 1457, and it served as a Polish royal residence until 1772."),
    ('wieliczka', 'Wieliczka Salt Mine', 'mine', 'Royal salt mine', 'from the 1200s', 1500, 2, ['Poland'], 'Wieliczka Salt Mine', 'Q454019', 49, 20.055655, 49.983053,
     ['Αλατωρυχεία Βιελίτσκα 5021.jpg', 4443, 2962, 'C messier', 'CC BY-SA 4.0', '80'],
     "Mined from the 13th century until 1996, this royal salt mine near Kraków was one of the oldest in the world. Miners carved chapels and statues out of the rock salt deep underground."),
    ('raclawice', 'Battle of Racławice', 'war', 'Battle', 'April 4, 1794', 1794, 2, ['Poland'], 'Battle of Racławice', 'Q1577800', 18, 20.22888889, 50.31055556,
     ['Jan Matejko - Kościuszko at Racławice - MNK II-a-151 - National Museum Kraków.jpg', 4000, 2018, 'Jan Matejko', 'Public domain', 'ab'],
     "Tadeusz Kościuszko's army, with about 2,000 peasants armed with scythes, defeated a Russian force early in his uprising. The battle is mentioned in the original text of Poland's national anthem."),
    ('maciejowice', 'Battle of Maciejowice', 'war', 'Battle', 'October 10, 1794', 1794, 3, ['Poland'], 'Battle of Maciejowice', 'Q2237038', 12, 21.60479, 51.70624,
     ['POL Maciejowice battle.jpg', 2272, 1835, 'Józef Hussarzewski', 'Public domain', 'b6'],
     "A larger Russian army destroyed Kościuszko's force, and Kościuszko himself was wounded and taken prisoner. The uprising ended that November, and in 1795 Poland was partitioned for the last time."),
    ('wizna', 'Battle of Wizna', 'war', 'Battle', 'September 7–10, 1939', 1939, 3, ['Poland'], 'Battle of Wizna', 'Q694500', 19, 22.4896574, 53.2124837, None,
     "Between 350 and 720 Polish soldiers held a fortified line for three days against more than 40,000 German troops invading Poland. It is sometimes called the Polish Thermopylae."),
    ('auschwitz', 'Auschwitz', 'memorial', 'Concentration and extermination camp', '1940–1945', 1943, 1, ['Poland'], 'Auschwitz concentration camp', 'Q7341', 104, 19.17833333, 50.03583333,
     ['Birkenau múzeum - panoramio (cropped).jpg', 2048, 1357, 'pzk net', 'CC BY 3.0', '37'],
     "The largest of the camps Nazi Germany ran in occupied Poland. Of at least 1.3 million people sent here, at least 1.1 million were murdered, most of them Jews brought from all over Europe."),
    ('treblinka', 'Treblinka', 'memorial', 'Extermination camp', '1942–1943', 1942, 2, ['Poland'], 'Treblinka extermination camp', 'Q152010', 59, 22.05305556, 52.63111111, None,
     "In this camp in a forest northeast of Warsaw, Nazi Germany murdered between 800,000 and 925,000 Jews in gas chambers, more than at any camp except Auschwitz."),
    ('sobibor', 'Sobibor', 'memorial', 'Extermination camp', '1942–1943', 1943, 3, ['Poland'], 'Sobibor extermination camp', 'Q152658', 55, 23.59361111, 51.44722222,
     ['Foto genomen vanuit een wachttoren van Sobibor, met gevangenen en bewakers.jpg', 3200, 1800, '', 'Public domain', '1b'],
     "Nazi Germany murdered some 170,000 to 250,000 Jews at this camp. On October 14, 1943, prisoners revolted; about 300 escaped, roughly 60 survived the war, and the camp was shut down."),
]

if __name__ == '__main__':
    D, topo = page_data()
    pl = Placer(D, topo)
    keys = {u['k'] for u in D['units']}
    for s, ks in STORIES.items():
        miss = [k for k in ks if k not in keys]
        assert not miss, (s, miss)
    ids = {p[0] for p in P}
    for t, (n, items) in THREADS.items():
        for it in items: assert isinstance(it, list) or it in ids, (t, it)
    out = []
    for (pid, n, k, what, when, y, tier, st, wt, q, sl, lon, lat, pic, note) in P:
        x, yy, ss = pl.place(lon, lat)
        th = [t for t, (_, items) in THREADS.items() if pid in items]
        m = re.match(r'(?:[A-Z][a-z]+ \d+, )?(\d{3,4})', when)      # the year it is listed under in a thread: its date, or (a site) its map year
        out.append({'id': pid, 'n': n, 'k': k, 'what': what, 'when': when, 'y': y, 'ly': int(m.group(1)) if m else y, 't': tier, 'st': st, 'w': '' if wt == n else wt, 'q': q, 'sl': sl,
                    'x': x, 'yk': yy, 'ss': ss, 'pic': pic, 'note': note, 'th': th})
    json.dump({'source': 'Hand-picked landmarks, October 5, 2026 (places/build_places.py); descriptions written from English Wikipedia; pictures from Wikimedia Commons',
               'stories': STORIES, 'threads': {t: [n, items] for t, (n, items) in THREADS.items()}, 'p': out},
              open('places.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(len(out), 'places')
