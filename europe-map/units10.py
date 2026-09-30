"""Units, OHM roles and Cliopatria names for 1000-1499 (the medieval era).

Loaded by units.py only when ERA=medieval: R10 goes in front of the other roles and C10 in front of the other
Cliopatria names, so the 1500-1799 and 1800-2026 maps are unaffected. UNITS10 is always added to UNITS (new keys only).

Choices:
  - France: the great fiefs (Normandy, Brittany, Aquitaine, Burgundy, Flanders, Champagne, Toulouse, Blois, Anjou...)
    are drawn in their own color, striped in France's color: they owed homage to the king but were ruled by their own
    dukes and counts. OHM's Kingdom of France is treated as an umbrella, so Cliopatria's outlines of the fiefs show.
  - Lands in France held by the kings of England (Normandy 1066-1204, the Angevin lands 1152-1204, Aquitaine and
    Gascony 1152-1453) are drawn in England's color, striped in France's: the English king held them as the French
    king's vassal. Land taken in the Hundred Years' War after 1415 is plain England, as the sources draw it.
  - The Holy Roman Empire: its larger members (the stem duchies, Bohemia, Austria, Brandenburg...) show as their own
    states, as in the 1500s map; the rest shows as the Empire. The Kingdom of Arles (Burgundy) is an umbrella the same way.
  - Italy south of the Papal States, Iberia, the Balkans, the Rus' principalities and the steppe: each state as the
    sources draw it. Groups of very small states are one unit: the smaller taifa kingdoms, the Catalan counties,
    Gaelic Ireland, the Welsh kingdoms other than the main ones.
"""
E10 = 1499

# key: (display name, overlord key or None, color family)
UNITS10 = {
    # ---- British Isles and the North Atlantic ----
    'NSE': ('North Sea Empire', None, 'NSE'), 'STR': ('Strathclyde', None, 'STR'), 'GLW': ('Galloway', None, 'GLW'),
    'KIS': ('Kingdom of the Isles', None, 'KIS'), 'ORK': ('Earldom of Orkney', 'NOR', 'ORK'), 'DUB': ('Norse Dublin', None, 'DUB'),
    'LIR': ('Lordship of Ireland', None, 'IRL'), 'GWY': ('Gwynedd', None, 'GWY'), 'POW': ('Powys', None, 'POW'),
    'DEH': ('Deheubarth', None, 'DEH'), 'MRG': ('Morgannwg', None, 'MRG'), 'BRY': ('Brycheiniog', None, 'BRY'),
    'WLS': ('Welsh kingdoms', None, 'WLS'), 'JAM': ('Jämtland', None, 'JAM'),
    # ---- France: fiefs (striped in France's color) ----
    'NMD': ('Duchy of Normandy', 'FRA', 'NMD'), 'NMD_E': ('Duchy of Normandy', 'FRA', 'GBR'),
    'AQU': ('Duchy of Aquitaine', 'FRA', 'AQU'), 'AQU_E': ('Duchy of Aquitaine', 'FRA', 'GBR'),
    'ANJ': ('County of Anjou', 'FRA', 'ANJ'), 'ANJ_E': ('Angevin lands in France', 'FRA', 'GBR'), 'MAE': ('County of Maine', 'FRA', 'MAE'),
    'BUR': ('Duchy of Burgundy', 'FRA', 'BUR'), 'FLA': ('County of Flanders', 'FRA', 'FLA'), 'CHA': ('County of Champagne', 'FRA', 'CHA'),
    'BLO': ('County of Blois', 'FRA', 'BLO'), 'TOU': ('County of Toulouse', 'FRA', 'TOU'), 'VRM': ('County of Vermandois', 'FRA', 'VRM'),
    'ARG': ('County of Armagnac', 'FRA', 'ARG'), 'FOX': ('Foix and Béarn', 'FRA', 'FOX'), 'BOB': ('Duchy of Bourbon', 'FRA', 'BOB'),
    'BGS': ('Burgundian State', None, 'BUR'),
    # ---- Kingdom of Arles and the western Empire ----
    'ARL': ('Kingdom of Arles', None, 'ARL'), 'PRV': ('County of Provence', None, 'PRV'), 'DAU': ('Dauphiné', None, 'DAU'),
    'FCM': ('Free County of Burgundy', None, 'FCO'), 'LLO': ('Lower Lotharingia', None, 'LLO'), 'HLD': ('County of Holland', None, 'HLD'),
    'HAI': ('County of Hainaut', None, 'HAI'), 'BRB': ('Duchy of Brabant', None, 'BRB'), 'FRI': ('Frisia', None, 'FRI'),
    # ---- the Empire: stem duchies and other larger members ----
    'SXD': ('Duchy of Saxony', None, 'SXD'), 'SWA': ('Duchy of Swabia', None, 'SWA'), 'FRC': ('Duchy of Franconia', None, 'FRC'),
    'THU': ('Duchy of Thuringia', None, 'THU'), 'CAR': ('Duchy of Carinthia', None, 'CAR'), 'AQL': ('Patriarchate of Aquileia', None, 'AQL'),
    # ---- Italy ----
    'TSC': ('March of Tuscany', None, 'TUS'), 'VRN': ('Verona', None, 'VRN'), 'SPO': ('Duchy of Spoleto', None, 'SPO'),
    'PIS': ('Republic of Pisa', None, 'PIS'), 'SLR': ('Principality of Salerno', None, 'SLR'), 'CPU': ('Principality of Capua', None, 'CPU'),
    'NPD': ('Duchy of Naples', None, 'NPD'), 'AMA': ('Duchy of Amalfi', None, 'AMA'), 'GTA': ('Duchy of Gaeta', None, 'GTA'),
    'NRM': ('Norman Italy', None, 'NRM'), 'SIC_M': ('Kingdom of Sicily', None, 'SIC_M'), 'BEN_L': ('Principality of Benevento', None, 'BEN_L'), 'ESC': ('Emirate of Sicily', None, 'ESC'), 'SIC_R': ('Kingdom of Sicily', 'ARA', 'SIC'),
    'ARB': ('Judicate of Arborea', None, 'ARB'), 'CAG': ('Judicate of Cagliari', None, 'CAG'), 'GLL': ('Judicate of Gallura', None, 'GLL'),
    'LGD': ('Judicate of Logudoro', None, 'LGD'), 'SDR': ('Kingdom of Sardinia', 'ARA', 'SDS'),
    # ---- Iberia ----
    'CRD': ('Caliphate of Córdoba', None, 'CRD'), 'TOL': ('Taifa of Toledo', None, 'TOL'), 'SEV': ('Taifa of Seville', None, 'SEV'),
    'ZAR': ('Taifa of Zaragoza', None, 'ZAR'), 'BDJ': ('Taifa of Badajoz', None, 'BDJ'), 'VLC': ('Taifa of Valencia', None, 'VLC'),
    'GRT': ('Taifa of Granada', None, 'GRT'), 'DNI': ('Taifa of Dénia', None, 'DNI'), 'ALR': ('Taifa of Almería', None, 'ALR'),
    'MUR': ('Taifa of Murcia', None, 'MUR'), 'TAI': ('Smaller taifa kingdoms', None, 'TAI'),
    'ALV': ('Almoravid Empire', None, 'ALV'), 'ALH': ('Almohad Caliphate', None, 'ALH'), 'GRN': ('Emirate of Granada', None, 'GRN'),
    'LEO': ('Kingdom of León', None, 'LEO'), 'CAS': ('Castile', None, 'CAS'), 'ARA': ('Aragon', None, 'ARA'),
    'BCN': ('County of Barcelona', None, 'BCN'), 'CAT': ('Catalan counties', None, 'CAT'), 'URG': ('County of Urgell', None, 'URG'),
    'RIB': ('County of Ribagorza', None, 'RIB'), 'POR_C': ('County of Portugal', 'LEO', 'POR'), 'GLC': ('Kingdom of Galicia', None, 'GLC'),
    'MAJ': ('Kingdom of Majorca', None, 'MAJ'),
    # ---- North Africa and the Near East ----
    'ZIR': ('Zirids', None, 'ZIR'), 'HMD': ('Hammadids', None, 'HMD'), 'FAT': ('Fatimid Caliphate', None, 'FAT'),
    'BRG': ('Barghawata', None, 'BRG'), 'NKR': ('Emirate of Nekor', None, 'NKR'), 'ABB': ('Abbasid Caliphate', None, 'ABB'),
    'BUY': ('Buyids', None, 'BUY'), 'JAZ': ('Emirates of Upper Mesopotamia', None, 'JAZ'), 'SEL': ('Great Seljuk Empire', None, 'SEL'),
    'RUM': ('Sultanate of Rum', None, 'RUM'), 'DSH': ('Danishmendids', None, 'DSH'), 'CIL': ('Armenian Kingdom of Cilicia', None, 'CIL'),
    'ANT': ('Principality of Antioch', None, 'ANT'), 'EDE': ('County of Edessa', None, 'EDE'), 'TRP': ('County of Tripoli', None, 'TRP'),
    'JER': ('Kingdom of Jerusalem', None, 'JER'), 'ZNG': ('Zengids', None, 'ZNG'), 'AYY': ('Ayyubid Sultanate', None, 'AYY'),
    'KHW': ('Khwarazmian Empire', None, 'KHW'), 'MNG': ('Mongol Empire', None, 'MNG'), 'ILK': ('Ilkhanate', None, 'ILK'),
    'CHB': ('Chobanids', None, 'CHB'), 'JAL': ('Jalayirids', None, 'JAL'), 'TIM': ('Timurid Empire', None, 'TIM'),
    'QQY': ('Qara Qoyunlu', None, 'QQY'), 'ARB_A': ('Bagratid Armenia', None, 'ARB_A'), 'VAS': ('Kingdom of Vaspurakan', None, 'VAS'),
    'KRM': ('Karamanids', None, 'KRM'), 'GRM': ('Germiyanids', None, 'GRM'), 'AYD': ('Aydinids', None, 'AYD'),
    'MEN': ('Menteshe', None, 'MEN'), 'SRH': ('Saruhanids', None, 'SRH'), 'KRS': ('Karasids', None, 'KRS'),
    'HMI': ('Hamidids', None, 'HMI'), 'TKE': ('Teke', None, 'TKE'), 'CND': ('Candarids', None, 'CND'),
    'DUL': ('Dulkadirids', None, 'DUL'), 'RMD': ('Ramadanids', None, 'RMD'), 'BEY': ('Other Turkish beyliks', None, 'BEY'),
    # ---- Byzantium, the Balkans, the Aegean ----
    'BYZ': ('Byzantine Empire', None, 'BYZ'), 'LAT': ('Latin Empire', None, 'LAT'), 'NIC': ('Empire of Nicaea', None, 'NIC'),
    'THL': ('Kingdom of Thessalonica', None, 'THL'), 'EPI': ('Despotate of Epirus', None, 'EPI'), 'TRE': ('Empire of Trebizond', None, 'TRE'),
    'ACH': ('Principality of Achaea', None, 'ACH'), 'ATH': ('Duchy of Athens', None, 'ATH'), 'KHR': ('Knights Hospitaller', None, 'MLT'),
    'CYK': ('Kingdom of Cyprus', None, 'CYK'), 'THD': ('Principality of Theodoro', None, 'THD'),
    'BGE': ('Bulgarian Empire', None, 'BUL'), 'VID': ('Tsardom of Vidin', None, 'VID'), 'DOB': ('Despotate of Dobruja', None, 'DOB'),
    'SRM': ('Serbia', None, 'SRB'), 'DUK': ('Duklja and Zeta', None, 'MNE'), 'HRZ': ('Duchy of Saint Sava', None, 'HRZ'),
    'BOS': ('Bosnia', None, 'BIH'), 'CRO': ('Kingdom of Croatia', None, 'CRO'), 'ALP': ('Albanian principalities', None, 'ALP'),
    'WAL_I': ('Wallachia', None, 'WAL'), 'MOL_I': ('Moldavia', None, 'MOL'),
    # ---- Poland, the Baltic, the Rus', the steppe ----
    'GPL': ('Duchy of Greater Poland', None, 'GPL'), 'LPL': ('Duchy of Kraków and Sandomierz', None, 'PLC'), 'SIL': ('Silesian duchies', None, 'SIL'),
    'MAZ': ('Duchy of Masovia', None, 'MAZ'), 'MAZ_P': ('Duchy of Masovia', 'PLK', 'MAZ'), 'KUY': ('Duchy of Kuyavia', None, 'KUY'),
    'KIE': ("Kievan Rus'", None, 'KIE'), 'PKV': ('Principality of Kiev', None, 'KIE'), 'CHN': ('Principality of Chernigov', None, 'CHN'),
    'PYS': ('Principality of Pereyaslavl', None, 'PYS'), 'VLS': ('Vladimir-Suzdal', None, 'VLS'), 'NVG': ('Novgorod Republic', None, 'NVG'),
    'PLT': ('Principality of Polotsk', None, 'PLT'), 'SMO': ('Principality of Smolensk', None, 'SMO'), 'HLC': ('Principality of Halych', None, 'HLC'),
    'VOL': ('Principality of Volhynia', None, 'VOL'), 'GVO': ('Galicia-Volhynia', None, 'GVO'), 'TPI': ('Turov and Pinsk', None, 'TPI'),
    'TVE': ('Principality of Tver', None, 'TVE'), 'NNO': ('Nizhny Novgorod', None, 'NNO'), 'RYA_I': ('Principality of Ryazan', None, 'RYA'),
    'VBU': ('Volga Bulgaria', None, 'VBU'), 'OGZ': ('Oghuz and Pechenegs', None, 'OGZ'), 'CUM': ('Cumans', None, 'CUM'),
    'GOH': ('Golden Horde', None, 'GOH'),
}

# (regex on the English name, level or None for any, unit, priority, from, to); None as the unit: the record
# decides nothing (the country record or Cliopatria does)
R10 = [
    # ---- umbrellas ----
    (r'^Kingdom of France$', '2', 'FRA', 1, 0, E10),
    (r'^Kingdom of Burgundy$', '2', 'ARL', 2, 0, 1031), (r'^Kingdom of Burgundy$', '3', 'ARL', 1, 1032, E10),
    (r'^Angevin Empire$', '1', 'ANJ_E', 1, 0, 1203), (r'^Angevin Empire$', '1', 'AQU_E', 1, 1204, E10),
    # ---- British Isles ----
    (r'^Kingdom of England$', '2', 'ENG', 2, 0, E10), (r'^Kingdom of Scotland$', '2', 'SCO', 2, 0, E10),
    (r'^Kingdom of Strathclyde$', None, 'STR', 2, 0, E10), (r'^Kingdom of Galloway$', None, 'GLW', 2, 0, E10),
    (r'^(Sodor|Lands of the Crovan Dynasty)$', None, 'KIS', 2, 0, E10), (r'^Isle of Man$', '4', 'SCO', 2, 0, E10),
    (r'^Earldom of Orkney$', '4', 'ORK', 3, 0, 1467), (r'^Kingdom of Dublin$', None, 'DUB', 2, 0, E10),
    (r'^Kingdom of (Desmond|Thomond|Leinster|Meath)$', None, 'GAE', 2, 0, E10),
    (r'^Lordship of (Eastern |Western )?Meath$', None, 'LIR', 2, 0, E10),
    (r'^(Kingdom of Gwynedd|Arfon|Llŷn|Meirionydd|Rhos)$', None, 'GWY', 2, 0, 1283),
    (r'^(Kingdom of Powys|Southern Powys)$', None, 'POW', 2, 0, 1283), (r'^Deheubarth$', None, 'DEH', 2, 0, E10),
    (r'^Kingdom of Glywysing/Morgannwg$', None, 'MRG', 2, 0, E10), (r'^Brycheiniog$', None, 'BRY', 2, 0, E10),
    (r'^Rhwng Gwy a Hafren$', None, 'WLS', 2, 0, E10),
    (r'^Duchy of Normandy$', '2', 'ENG', 2, 0, E10),              # the Channel Islands after 1204
    # ---- Scandinavia and the North Atlantic ----
    (r'^Kingdom of Norway$', '2', 'NOR', 2, 0, E10), (r'^Faroe Islands$', '2', 'NOR', 2, 0, E10),
    (r'^(Faroe Islands|Iceland)$', '4', 'NOR', 2, 0, 1379), (r'^Icelandic Commonwealth$', None, 'ISL', 2, 0, E10),
    (r'^Kingdom of Sweden$', '2', 'SWE', 2, 0, E10), (r'^Duchy of Estonia$', None, 'DEN', 2, 0, E10), (r'^Danish March$', None, 'DEN', 2, 0, E10),
    # ---- France ----
    (r'^Duchy of Normandy$', '3', 'NMD', 3, 0, 1066), (r'^Duchy of Normandy$', '3', 'NMD_E', 3, 1067, 1086),
    (r'^Duchy of Normandy$', '3', 'NMD', 3, 1087, 1105), (r'^Duchy of Normandy$', '3', 'NMD_E', 3, 1106, 1143),
    (r'^Duchy of Normandy$', '3', 'ANJ', 3, 1144, 1151), (r'^Duchy of Normandy$', '3', 'NMD_E', 3, 1152, E10),
    (r'^Duchy of (Aquitaine|Gascony)$', '3', 'AQU', 3, 0, 1151), (r'^Duchy of (Aquitaine|Gascony)$', '3', 'AQU_E', 3, 1152, E10),
    (r'^Duchy of Brittany$', '3', 'BRI', 3, 0, E10), (r'^County of Nantes$', None, 'BRI', 3, 0, E10),
    (r'^Duchy of Burgundy$', None, 'BUR', 3, 0, E10), (r'^Burgundian State$', None, 'BGS', 2, 0, E10),
    (r'^County of Champagne$', None, 'CHA', 3, 0, 1284), (r'^County of Champagne$', None, 'FRA', 2, 1285, E10),
    (r'^County of Flanders$', None, 'FLA', 3, 0, 1383), (r'^County of Flanders$', None, 'BGS', 2, 1384, E10),
    (r'^County of Artois$', None, 'FRA', 2, 0, 1382), (r'^County of Artois$', None, 'BGS', 2, 1383, 1481),
    (r'^County of Artois$', None, 'FRA', 2, 1482, 1492), (r'^County of Artois$', None, 'HNL', 2, 1493, E10),
    (r'^Dauphiné of Viennois$', None, 'DAU', 3, 0, 1349), (r'^Dauphiné of Viennois$', None, 'FRA', 2, 1350, E10),
    (r'^County of (Alençon|Angoulême|Anjou|La Marche|Maine|Perche|Poitou|Tours|Vendôme|Saint-Pol)$', '4', None, 0, 0, E10),
    (r'^Duchy of Nemours$', '4', None, 0, 0, E10),
    # ---- Low Countries, Lorraine ----
    (r'^County of (Holland|Zeeland)$', None, 'HLD', 2, 0, 1432), (r'^County of (Holland|Zeeland)$', None, 'BGS', 2, 1433, 1481),
    (r'^County of (Holland|Zeeland)$', None, 'HNL', 2, 1482, E10),
    (r'^County of Hainaut$', None, 'HAI', 2, 0, 1432), (r'^County of Hainaut$', None, 'BGS', 2, 1433, 1481), (r'^County of Hainaut$', None, 'HNL', 2, 1482, E10),
    (r'^County of Namur$', None, 'HRE', 2, 0, 1420), (r'^County of Namur$', None, 'BGS', 2, 1421, 1481), (r'^County of Namur$', None, 'HNL', 2, 1482, E10),
    (r'^Duchy of Luxembourg$', None, 'LUX', 2, 0, 1442), (r'^Duchy of Luxembourg$', None, 'BGS', 2, 1443, 1481), (r'^Duchy of Luxembourg$', None, 'HNL', 2, 1482, E10),
    (r'^Friesland$', None, 'FRI', 2, 0, E10), (r'^Cambrésis$', None, 'HRE', 2, 0, E10),
    (r'^Duchy of Lower Lotharingia$', None, 'LLO', 2, 0, E10), (r'^(Duchy of Upper Lotharingia|County of Bar|Duchy of Bar|Duchy of Lorraine)$', None, 'LOR', 2, 0, E10),
    (r'^Free County of Burgundy$', None, 'HNL', 2, 1493, E10),
    # ---- the Empire ----
    (r'^Duchy of Saxony$', None, 'SXD', 2, 0, E10), (r'^Billung March$', None, 'SXD', 2, 0, E10),
    (r'^(Duchy of Saxe-Wittenberg|Electorate of Saxony\(-Wittenberg\)|March of Meissen)$', None, 'SAX', 2, 0, E10),
    (r'^Duchy of Swabia$', None, 'SWA', 2, 0, E10), (r'^Duchy of Franconia$', None, 'FRC', 2, 0, E10),
    (r'^Duchy of Thuringia$', None, 'THU', 2, 0, E10), (r'^Duchy of Carinthia$', None, 'CAR', 2, 0, E10),
    (r'^Duchy of Austria$', None, 'AUT', 2, 0, E10), (r'^(Duchy of Bavaria|March of Cham)$', None, 'BAV', 2, 0, E10),
    (r'^Duchy of Bohemia$', None, 'BOK', 2, 0, E10), (r'^Duchy of Brunswick-Lüneburg$', None, 'BRU', 2, 0, E10),
    (r'^(Saxon Eastern March|Burgraviate of Nuremberg|County of Schaumburg and Holstein-Pinneberg)$', None, 'HRE', 2, 0, E10),
    (r'^(Duchy of Pomerania|Duchy of Pomerania-Stettin|Duchy of Pomerania-Wolgast)$', None, 'POM', 2, 0, E10),
    (r'^Peasant Republic of Dithmarschen$', None, 'DIT', 2, 0, E10),
    (r'^Free Imperial City of Bern$', '4', 'HRE', 2, 0, 1352), (r'^Free Imperial City of Mulhouse$', '4', 'HRE', 2, 0, E10),
    # ---- Italy ----
    (r'^(March of Tuscany)$', None, 'TSC', 2, 0, E10), (r'^(March of Verona|Lordship of Verona)$', None, 'VRN', 2, 0, E10),
    (r'^Duchy of Spoleto$', None, 'SPO', 2, 0, E10),
    (r'^(Lordship of Milan|Duchy of Milan|Milanese Corsica)$', None, 'MLS', 2, 0, E10), (r'^Golden Ambrosian Republic$', None, 'MLS', 2, 1447, 1449),
    (r'^Golden Ambrosian Republic$', None, None, 0, 1450, E10),
    (r'^(Republic of Florence)$', None, 'TUS', 2, 0, E10), (r'^(Lordship of Lucca)$', None, 'LUC', 2, 0, E10),
    (r'^(Republic of Pisa|Republic of Pisa \(1399-1406\)|Pisan Corsica)$', None, 'PIS', 2, 0, E10),
    (r'^Genoese Gazaria$', None, 'GEN', 3, 0, E10), (r'^Lordship of Oneglia \(1298-1488\)$', None, 'GEN', 2, 0, E10),
    (r'^Provence$', '4', 'FRA', 2, 1481, E10), (r'^Republic of Massa$', None, 'MAS', 2, 0, E10),
    (r'^County of Asti$', None, 'HRE', 2, 0, 1386), (r'^County of Asti$', None, 'FRA', 2, 1387, E10),
    (r'^(Lordship of Venice)$', None, 'VEN', 2, 0, E10),
    (r'^Principality of Benevento$', None, 'BEN_L', 2, 0, E10), (r'^(Duchy of Naples|Duchy of Sorrento)$', None, 'NPD', 2, 0, E10),
    (r'^Duchy of Amalfi$', None, 'AMA', 2, 0, E10), (r'^(Duchy of Gaeta|Gaeta)$', None, 'GTA', 2, 0, E10),
    (r'^Duchy of Calabria$', None, 'BYZ', 2, 0, E10), (r'^County of Sicily$', None, 'NRM', 2, 0, E10),
    (r'^Emirate of Sicily$', None, 'ESC', 2, 0, E10),
    (r'^Kingdom of Sicily$', None, 'SIC_M', 2, 0, 1281), (r'^Kingdom of Sicily$', None, 'SIC', 2, 1282, 1408), (r'^Kingdom of Sicily$', None, 'SIC_R', 3, 1409, 1478), (r'^Kingdom of Sicily$', None, 'SIC_S', 3, 1479, E10),
    (r'^Kingdom of Naples$', None, 'NAP', 2, 0, E10),
    (r'^Judicate of Arborea$', None, 'ARB', 2, 0, E10), (r'^Judicate of Cagliari$', None, 'CAG', 2, 0, E10),
    (r'^Judicate of Gallura$', None, 'GLL', 2, 0, E10), (r'^Judicate of Logudoro$', None, 'LGD', 2, 0, E10),
    (r'^Kingdom of Sardinia$', '4', 'SDR', 3, 0, 1478), (r'^Kingdom of Majorca$', '4', 'ARA', 2, 0, 1478),
    # ---- Iberia ----
    (r'^Caliphate of Córdoba', None, 'CRD', 2, 0, E10), (r'^Independent Moorish States$', None, 'TAI', 1, 0, E10),
    (r'^Emirate of Granada$', None, 'GRN', 2, 0, E10), (r'^Kingdom of León$', None, 'LEO', 2, 0, E10),
    (r'^(Kingdom of Castile|County of Castile)$', None, 'CAS', 2, 0, E10), (r'^Crown of Castile$', None, 'CAS', 2, 0, 1478),
    (r'^Crown of Castile$', None, 'ESP', 2, 1479, E10), (r'^(Kingdom of Aragon)$', None, 'ARA', 2, 0, E10),
    (r'^Crown of Aragon$', None, 'ARA', 2, 0, 1478), (r'^Crown of Aragon$', None, 'ESP', 2, 1479, E10),
    (r'^(County of Aragon|County of Sobrarbe)$', None, 'NAV', 2, 0, 1034), (r'^(County of Aragon|County of Sobrarbe)$', None, 'ARA', 2, 1035, E10),
    (r'^County of Ribagorza$', None, 'RIB', 2, 0, 1017), (r'^County of Ribagorza$', None, 'NAV', 2, 1018, 1034), (r'^County of Ribagorza$', None, 'ARA', 2, 1035, E10),
    (r'^Kingdom of Pamplona$', None, 'NAV', 2, 0, E10),
    (r'^(County of Barcelona|County of Girona|County of Osona)$', None, 'BCN', 2, 0, E10),
    (r'^(County of Besalú|Comtat de Cerdanya 950-1150|County of Conflent|County of Empúries|County of Pallars.*)$', None, 'CAT', 2, 0, E10),
    (r'^County of Roussillon$', None, 'CAT', 2, 0, 1171), (r'^County of Roussillon$', None, 'ARA', 2, 1172, 1275), (r'^County of Roussillon$', None, 'MAJ', 2, 1276, E10),
    (r'^County of Urgell$', None, 'URG', 2, 0, E10), (r'^Kingdom of Majorca$', '2', 'MAJ', 2, 0, E10),
    (r'^(Kingdom of Valencia|Principality of Catalonia)$', '4', 'ARA', 2, 0, E10),
    (r'^Kingdom of Galicia$', None, 'GLC', 2, 0, E10), (r'^Portugal$', '4', 'POR_C', 3, 0, 1138),
    # ---- Poland and the Baltic ----
    (r'^Kingdom of Poland$', '2', 'PLK', 2, 0, E10),
    (r'^(Duchy of Masovia \(1233-1313\)|Duchy of Rawa \(1313-1370\)|Duchy of Płock|Duchy of Czersk|Duchy of Rawa)$', None, 'MAZ', 2, 0, 1350),
    (r'^(Duchy of Masovia \(1233-1313\)|Duchy of Rawa \(1313-1370\)|Duchy of Płock|Duchy of Czersk|Duchy of Rawa)$', None, 'MAZ_P', 3, 1351, E10),
    (r'^Prince-Bishopric of Warmia$', None, 'TEU', 2, 0, 1465),
    # ---- the Rus', the steppe ----
    (r'^(Novgorod Republic)$', None, 'NVG', 2, 0, E10),
    (r'^(Principality of Moscow|Grand Principality of Moscow.*|Grand Duchy of Moscow|Muscovy \(1462\)|Княжество Московское)$', None, 'RUS', 2, 0, E10),
    (r'^Ростовское княжество$', None, 'VLS', 2, 0, 1327), (r'^Ростовское княжество$', None, 'RUS', 2, 1328, E10),
    (r'^Principality of Murom-Ryazan$', None, 'RYA_I', 2, 0, E10), (r'^Principality of Ryazan$', None, 'RYA_I', 2, 0, 1455),
    (r'^Principality of Tver$', None, 'TVE', 2, 0, E10),
    (r'^Mongol Empire$', None, 'MNG', 1, 0, 1241), (r'^Mongol Empire$', None, 'GOH', 1, 1242, E10),
    # ---- Byzantium, the Balkans, the Near East ----
    # OHM's records here change only every few decades and overstate (its Byzantine Empire of 1354-1453 still holds
    # most of the Balkans; its Ottoman Empire of the same years is a tenth of the real extent): priority 1, so
    # Cliopatria, which changes more often, decides wherever it has a state
    (r'^Eastern Roman Empire$', None, 'BYZ', 1, 0, E10), (r'^Byzantine Crete \(961–1205\)$', None, 'BYZ', 2, 0, E10),
    (r'^Ottoman Empire$', None, 'OTT', 1, 0, E10), (r'^Latin Empire$', None, 'LAT', 1, 0, E10),
    (r'^Empire of Nicaea$', None, 'NIC', 1, 0, E10), (r'^Empire of Trebizond$', None, 'TRE', 1, 0, E10),
    (r'^Empire of Thessalonica$', None, 'THL', 1, 0, 1223), (r'^Empire of Thessalonica$', None, 'EPI', 1, 1224, 1245),
    (r'^Empire of Thessalonica$', None, 'NIC', 1, 1246, 1260), (r'^Empire of Thessalonica$', None, 'BYZ', 1, 1261, E10),
    (r'^Principality of Achaea$', None, 'ACH', 1, 0, E10), (r'^(Duchy of Athens|Duchy of Neopatras)$', None, 'ATH', 2, 0, E10),
    (r'^Knights Hospitaller$', None, 'KHR', 2, 0, E10), (r'^Kingdom of Cyprus$', None, 'CYK', 2, 0, E10),
    (r'^Principality of Theodoro$', None, 'THD', 2, 0, E10),
    (r'^(Grand Principality of Serbia|Kingdom of Serbia|Serbian Empire)$', None, 'SRM', 1, 0, E10),
    (r'^Kingdom of Croatia$', None, 'CRO', 2, 0, E10), (r'^Grand Principality of Hungary$', None, 'HUK', 2, 0, E10),
    (r'^Principality of Antioch$', None, 'ANT', 2, 0, E10), (r'^County of Edessa$', None, 'EDE', 2, 0, E10),
    (r'^County of Tripoli$', None, 'TRP', 2, 0, E10), (r'^Seljuk Empire$', None, 'SEL', 1, 0, E10),
    (r'^Abbasid Caliphate$', None, 'ABB', 1, 0, E10), (r'^Fatimid Caliphate$', None, 'FAT', 1, 0, E10),
    (r'^Il-khanate$', None, 'ILK', 1, 0, E10), (r'^Khwarazmian Empire$', None, 'KHW', 1, 0, E10),
    (r'^Zirid Emirate$', None, 'ZIR', 1, 0, E10),
    (r'^(عثمانيه|غازي عينتاب)$', None, None, 0, 0, E10),
]

# Cliopatria names (regex, unit, from, to): the first whose years hold the record's first year applies
C10 = [
    # British Isles and Scandinavia
    (r'^(North Sea Empire|Denmark-England)$', 'NSE'), (r'^Norway-Denmark$', 'NOR'), (r'^Old Kingdom of Norway$', 'NOR'),
    (r'^Kingdom of Alba$|^Kingdom of Scotland$', 'SCO'), (r'^Strathclyde$', 'STR'), (r'^Brythons$', 'WLS', 0, 1084), (r'^Brythons$', 'GLW', 1085, E10),
    (r'^(Kingdom of the Isles|Kingdom of Mann|Viking settlements)$', 'KIS', 0, 1265), (r'^Kingdom of Mann$', 'SCO', 1266, E10),
    (r'^Viking settlements$', None), (r'^Isle of Man$', 'SCO'),
    (r'^Kingdom of Gwynedd$', 'GWY'), (r'^Kingdom of Powys.*$', 'POW'), (r'^Kingdom of (Morgannwg|Gwent)$', 'MRG'),
    (r'^Kingdom of Brycheiniog$', 'BRY'), (r'^Earldom of (Desmond|Ulster)$', 'LIR'),
    (r'^Kingdom of Denmark$|^Danish Magnates$', 'DEN'), (r'^Kingdom of Sweden$|^Scandinavian minor kingdoms$', 'SWE'),
    (r'^Icelandic Commonwealth$', 'ISL'), (r'^Jaemtland$', 'JAM'), (r'^House of Oldenburg$', 'DEN'),
    # France
    (r'^Duchy of Normandy$', 'NMD'), (r'^Duchy of Aquitaine$', 'AQU', 0, 1151), (r'^Duchy of Aquitaine$', 'AQU_E', 1152, E10),
    (r'^Duchy of Gascony$', 'AQU', 0, 1151), (r'^Duchy of Gascony$', 'AQU_E', 1152, E10),
    (r'^(County of Anjou|Angevins)$', 'ANJ', 0, 1151), (r'^County of Anjou$', 'ANJ_E', 1152, 1203), (r'^County of Anjou$', 'FRA', 1204, 1245),
    (r'^County of Anjou$', 'ANJ', 1246, 1289), (r'^County of Anjou$', 'FRA', 1290, E10),
    (r'^Angevin Empire$', 'ANJ', 0, 1151), (r'^Angevin Empire$', 'ANJ_E', 1152, E10),
    (r'^County of Maine$', 'MAE', 0, 1109), (r'^County of Maine$', 'ANJ', 1110, 1151), (r'^County of Maine$', 'ANJ_E', 1152, 1203),
    (r'^County of Maine$', 'FRA', 1204, 1245), (r'^County of Maine$', 'ANJ', 1246, 1289), (r'^County of Maine$', 'FRA', 1290, 1355),
    (r'^County of Maine$', 'ANJ', 1356, 1480), (r'^County of Maine$', 'FRA', 1481, E10),
    (r'^Duchy of Brittany$', 'BRI'), (r'^Duchy of Burgundy$', 'BUR', 0, 1362), (r'^Duchy of Burgundy$', 'BGS', 1363, 1476), (r'^Duchy of Burgundy$', 'FRA', 1477, E10),
    (r'^County of Flanders$', 'FLA', 0, 1383), (r'^County of Flanders$', 'BGS', 1384, E10),
    (r'^County of Champagne$', 'CHA', 0, 1284), (r'^County of Champagne$', 'FRA', 1285, E10),
    (r'^County of Blôis$', 'BLO', 0, 1396), (r'^County of Blôis$', 'FRA', 1397, E10),
    (r'^County of (Toulouse|Rouergue)$', 'TOU', 0, 1270), (r'^County of (Toulouse|Rouergue)$', 'FRA', 1271, E10),
    (r'^County of Vermandois$', 'VRM', 0, 1212), (r'^County of Vermandois$', 'FRA', 1213, E10),
    (r'^County of Armagnac$', 'ARG', 0, 1472), (r'^County of Armagnac$', 'FRA', 1473, E10),
    (r'^County of (Foix|Béarn)$', 'FOX'), (r'^House of Bourbon$', 'BOB'),
    (r'^County of (Vexin|Nevers|Auvergne|Périgord|Touraine|Poitou|Artois|Boulogne)$', 'FRA'),
    (r'^(Capetian House of Anjou|House of Valois-Anjou)$', 'PRV'),
    # Kingdom of Arles and the western Empire
    (r'^Kingdom of Arles$', 'ARL'), (r'^Dauphiné$', 'DAU', 0, 1349), (r'^Dauphiné$', 'FRA', 1350, E10),
    (r'^County of Savoy$', 'SAV'), (r'^Principality of Orange$', 'ORA'), (r'^Comtat Venaissin$', 'PAP'),
    (r'^Free County of Burgundy$', 'FCM', 0, 1383), (r'^Free County of Burgundy$', 'BGS', 1384, 1476),
    (r'^County of Holland$', 'HLD', 0, 1432), (r'^County of Holland$', 'BGS', 1433, E10),
    (r'^County of Brabant$', 'BRB', 0, 1429), (r'^County of Brabant$', 'BGS', 1430, E10),
    (r'^(Duchy of Luxembourg|House of Luxembourg)$', 'LUX', 0, 1442), (r'^Duchy of Luxembourg$', 'BGS', 1443, E10),
    (r'^Duchy of Lorraine$', 'LOR'),
    # the Empire
    (r'^Holy Roman Empire( Minor States)?$', 'HRE'), (r'^Duchy of Bavaria$|^House of Wittelsbach$', 'BAV'),
    (r'^House of Habsburg$|^Habsburg Monarchy$|^Duchy of Styria$', 'AUT'), (r'^House of Hohenstaufen$', 'SWA'),
    (r'^House of Ascania$|^Electorate of Saxony$', 'SAX'), (r'^(Margraviate|Electorate) of Brandenburg$', 'BRA'),
    (r'^Duchy of Bohemia$|^Kingdom of Bohemia$|^Margraviate of Moravia$', 'BOK'), (r'^Electorate of Trier$', 'TRR'),
    (r'^Patriarchate of Aquileia$', 'AQL'), (r'^Swiss Confederation$', 'SUI'), (r'^Teutonic Order$', 'TEU'),
    (r'^Livonian Brothers of the Sword$|^Livonian Conference$', 'LIV'), (r'^Pomerania$', 'POM'),
    # Italy
    (r'^Papal States$', 'PAP'), (r'^Republic of Venice$', 'VEN'), (r'^Republic of Genoa$', 'GEN'), (r'^Republic of Pisa$', 'PIS'),
    (r'^Republic of Florence$', 'TUS'), (r'^(Duchy of Milan|Ambrosian Republic)$', 'MLS'), (r'^Republic of Amalfi$', 'AMA'),
    (r'^Duchy of Naples$', 'NPD'), (r'^Duchy of Benevento$', 'BEN_L'), (r'^Principality of Salerno$', 'SLR'), (r'^Principality of Capua$', 'CPU'),
    (r'^Norman Italy$', 'NRM'), (r'^Emirate of Sicily$', 'ESC'), (r'^Kingdom of Africa$', 'SIC_M'),
    (r'^Kingdom of Sicily$', 'SIC_M', 0, 1281), (r'^Kingdom of Sicily$', 'SIC', 1282, 1408), (r'^Kingdom of Sicily$', 'SIC_R', 1409, 1478), (r'^Kingdom of Sicily$', 'SIC_S', 1479, E10),
    (r'^House of Anjou-Sicily$', 'SIC_M', 0, 1281), (r'^Kingdom of Naples$|^House of Anjou-Sicily$', 'NAP'),
    (r'^Giudicato of Arborea$', 'ARB'), (r'^Giudicato of Cagliari$', 'CAG'), (r'^Giudicato of Gallura$', 'GLL'), (r'^Giudicato of Logudoro$', 'LGD'),
    # Iberia and North Africa
    # Cliopatria keeps some taifas' outlines after the Almoravids (1086-1147) or Almohads (1147-1228) took them over:
    # those records decide nothing, so the larger empire shows
    (r'^Caliphate of Córdoba$', 'CRD', 0, 1031), (r'^Caliphate of Córdoba$', 'TAI', 1032, E10),
    (r'^Taifa of Toledo$', 'TOL', 0, 1085), (r'^Taifa of Seville$', 'SEV', 0, 1091), (r'^Taifa of Zaragoza$', 'ZAR', 0, 1110),
    (r'^Taifa of Badajoz$', 'BDJ', 0, 1094), (r'^Taifa of Valencia$', 'VLC', 0, 1093), (r'^Taifa of Valencia$', 'VLC', 1228, 1238),
    (r'^Taifa of Granada$', 'GRT', 0, 1090), (r'^Taifa of Dénia$', 'DNI', 0, 1076), (r'^Taifa of Almería$', 'ALR', 0, 1091),
    (r'^Taifa of Murcia$', 'MUR', 0, 1090), (r'^Taifa of Murcia$', 'MUR', 1144, 1172), (r'^Taifa of Murcia$', 'MUR', 1228, 1265),
    (r'^Taifa of ', 'TAI', 0, 1090), (r'^Taifa of ', 'TAI', 1144, 1172), (r'^Taifa of ', 'TAI', 1228, 1265), (r'^Taifa of ', None),
    (r'^Almoravid Dynasty$', 'ALV'), (r'^Almohad Caliphate$', 'ALH', 0, 1269), (r'^Almohad Caliphate$', 'MOR'), (r'^Emirate of Granada$', 'GRN'),
    (r'^Kingdom of León$', 'LEO'), (r'^Kingdom of Castile$', 'CAS'), (r'^Crown of Castile$', 'CAS', 0, 1478), (r'^Crown of Castile$', 'ESP', 1479, E10),
    (r'^Kingdom of Aragon$', 'ARA'), (r'^Crown of Aragon$', 'ARA', 0, 1478), (r'^Crown of Aragon$', 'ESP', 1479, E10),
    (r'^County of Ribagorza$', 'RIB', 0, 1017), (r'^County of Ribagorza$', 'NAV', 1018, 1039), (r'^County of Ribagorza$', 'ARA', 1040, E10),
    (r'^County of (Barcelona|Osona)$', 'BCN'), (r'^County of (Ampuria|Berga|Pallars.*|Rosellón)$', 'CAT'), (r'^County of Urgell$', 'URG', 0, 1412),
    (r'^County of Urgell$', 'ARA', 1413, 1478), (r'^County of Urgell$', 'ESP', 1479, E10),
    (r'^Kingdom of Navarre$', 'NAV'), (r'^Kingdom of Galicia$', 'GLC'), (r'^County of Portugal$', 'POR'), (r'^Kingdom of Portugal$|^Portuguese Empire$', 'POR'),
    (r'^Kingdom of Majorca$', 'MAJ'),
    (r'^Zirid dynasty$', 'ZIR'), (r'^Hammadid Dynasty$', 'HMD'), (r'^Fatimid Caliphate$', 'FAT'), (r'^Barghawata Conference$', 'BRG'),
    (r'^Emirate of Nekor$', 'NKR'), (r'^Hafsid Dynasty$', 'HAF'), (r'^Zayyanid dynasty$', 'TLM'), (r'^(Marinid Sultanate|Wattasid dynasty)$', 'MOR'),
    # Near East and Anatolia
    (r'^Abbasid Caliphate$', 'ABB'), (r'^Buyid Dynasty$', 'BUY'), (r'^Hamdanid Emirates$', 'JAZ'), (r'^Great Seljuk Empire$', 'SEL'),
    (r'^Sultanate of Rum$', 'RUM'), (r'^Danishmendids$', 'DSH'), (r'^Armenian Kingdom of Cilicia$', 'CIL'),
    (r'^Principality of Antioch$', 'ANT'), (r'^County of Edessa$', 'EDE'), (r'^County of Tripoli$', 'TRP'), (r'^Kingdom of Jerusalem$', 'JER'),
    (r'^Zengid dynasty$', 'ZNG'), (r'^Ayyubid Sultanate$', 'AYY'), (r'^Mamluk Sultanate$', 'MAM'), (r'^Khwarezmid Empire$', 'KHW'),
    (r'^Mongol Empire$', 'MNG', 0, 1241), (r'^Mongol Empire$', 'GOH', 1242, E10), (r'^Ilkhanate$', 'ILK'), (r'^Chobanids$', 'CHB'),
    (r'^Jalayirid Sultanate$', 'JAL'), (r'^Timurid Empire$', 'TIM'), (r'^Qara Qoyunlu$', 'QQY'), (r'^Aq Qoyunlu$', 'AQQ'),
    (r'^Bagratid Armenia$', 'ARB_A'), (r'^Kingdom of Vaspurakan$', 'VAS'), (r'^Shirvan$', 'SHI'),
    (r'^(Georgia|Kingdom of Georgia|Kingdom of the Iberians|Kingdom of Kartli|Kingdom of Kakheti|Samtskhe-Saatabago)$', 'GEO'),
    (r'^Kingdom of Imereti$', 'IME'),
    (r'^Beylik of Karaman$', 'KRM'), (r'^Germiyanids$', 'GRM'), (r'^Beylik of Aydin$', 'AYD'), (r'^Beylik of Menteshe$', 'MEN'),
    (r'^Beylik of Saruhan$', 'SRH'), (r'^Beylik of Karasi$', 'KRS'), (r'^Beylik of Hamid$', 'HMI'), (r'^Beylik of Teke$', 'TKE'),
    (r'^(Beylik of Isfendiyar|Beylik of Sinop|Kastamonu)$', 'CND'), (r'^Beylik of Dulkadir$', 'DUL'), (r'^Ramadanid Emirate$', 'RMD'),
    (r'^(Ahi Republic|Eshrefids)$', 'BEY'), (r'^Ottoman Empire$', 'OTT'),
    # Byzantium and the Balkans
    (r'^Byzantine Empire$|^Commune of the Zealots$', 'BYZ'), (r'^Latin Empire$', 'LAT', 0, 1260), (r'^Latin Empire$', None),
    (r'^Nicaean Empire$', 'NIC', 0, 1260), (r'^Nicaean Empire$', 'BYZ'),
    (r'^Kingdom of Thessalonica$', 'THL'), (r'^Empire of Thessalonica$', 'EPI'), (r'^(Despotate of Epirus|Thessaly|House of Tocco)$', 'EPI'),
    (r'^Empire of Trebizond$', 'TRE'), (r'^Principality of Achaea$', 'ACH'), (r'^(Duchy of Athens|Catalan Company)$', 'ATH'),
    (r'^(Negroponte)$', 'VEN'), (r'^Duchy of the Archipelago$', 'ARC'), (r'^Domain of Rhodes$', 'BYZ'),
    (r'^Kingdom of Cyprus$', 'CYK'), (r'^Principality of Theodoro$', 'THD'),
    (r'^(First|Second) Bulgarian Empire$', 'BGE'), (r'^Despotate of Vidin$', 'VID'), (r'^Despotate of Dobruja$', 'DOB'),
    (r'^(Grand Principality of Serbia|Kingdom of Serbia|Serbian Empire|Serbian Despots|Kingdom of Syrmia)$', 'SRM'),
    (r'^(Great Principality of Duklja|Kingdom of Duklja)$', 'DUK'), (r'^Duchy of Saint Sava$', 'HRZ'),
    (r'^(Banate|Kingdom) of Bosnia$', 'BOS'), (r'^Kingdom of Croatia$', 'CRO'),
    (r'^(Albanian Principalities|Principality of Valona.*|Despotate of Arta)$', 'ALP'), (r'^Republic of Ragusa$', 'RAG'),
    (r'^Principality of Wallachia$', 'WAL_I', 0, 1416), (r'^Principality of Wallachia$', 'WAL', 1417, E10),
    (r'^Principality of Moldavia$', 'MOL_I', 0, 1455), (r'^Principality of Moldavia$', 'MOL', 1456, E10),
    (r'^(Principality|Kingdom) of Hungary$', 'HUK'),
    # Poland, the Baltic
    (r'^Kingdom of Poland$|^House of Jagiellon$', 'PLK'), (r'^Duchy of Greater Poland$|^Duchy of Kalisz$', 'GPL'),
    (r'^(Duchy of Sandomierz|Grand Duchy of Kraków|Duchy of Łęczyca)$', 'LPL'),
    (r'^(Duchy of (Silesia|Opole|Wrocław|Głogów|Legnica|Jawor|Bytom|Racibórz))$', 'SIL'),
    (r'^Duchy of Masovia$', 'MAZ', 0, 1350), (r'^Duchy of Masovia$', 'MAZ_P', 1351, E10), (r'^Duchy of Kuyavia$', 'KUY'),
    (r'^Duchies of Poland$', None), (r'^Grand Duchy of Lithuania$', 'LIT'),
    # the Rus' and the steppe
    (r"^Kievan Rus'$", 'KIE'), (r'^Principality of Kiev$', 'PKV'), (r'^Principality of Chernigov$', 'CHN'),
    (r'^Principality of Pereyaslavl$', 'PYS'),
    (r'^Principality of (Rostov-Suzdal|Beloozero)$', 'VLS'), (r'^Principality of Vladimir-Suzdal$', 'VLS', 0, 1327),
    (r'^Principality of Vladimir-Suzdal$', 'RUS', 1328, E10), (r'^Nizhny Novgorod$', 'NNO'),
    (r'^Novgorod Republic$', 'NVG'), (r'^Pskov Republic$', 'PSK'),
    (r'^Principality of (Polotsky|Minsk|Vitebsk|Drutsk|Jersika|Koknese)$', 'PLT'), (r'^Principality of Smolensk$', 'SMO'),
    (r'^Principality of (Halych|Peremyshl|Terebovlia)$', 'HLC'), (r'^Principality of Volhynia$', 'VOL'),
    (r'^(Principality of Galicia-Volhynia|Galicia-Volhynia)$', 'GVO'), (r'^Principality of (Turov and Pinsk|Turov|Pinsk)$', 'TPI'),
    (r'^Tver$', 'TVE'), (r'^Principality of Ryazan$|^Ryazan$', 'RYA_I', 0, 1455), (r'^Ryazan$', 'RYA', 1456, E10),
    (r'^Grand Principality of Moscow$', 'RUS'),
    (r'^Volga Bulgaria$', 'VBU'), (r'^Oghuz Turks$', 'OGZ'), (r'^(Cuman-Kipchak Confederation|Kimek-Kipchak confederation|Halych-Volhynia occupation)$', 'CUM'),
    (r'^Golden Horde$', 'GHO', 1450, E10),   # from 1450 Cliopatria's Golden Horde is the rump OHM calls the Great Horde
    (r'^(Golden Horde|Blue Horde|White Horde)$', 'GOH'), (r'^Crimean Khanate$', 'CRI_I', 0, 1474), (r'^Crimean Khanate$', 'CRI', 1475, E10),
    (r'^Khanate of Kazan$', 'KZN'), (r'^Astrakhan Khanate$', 'AST'), (r'^Nogai Horde$', 'NOG'), (r'^Qasim Khanate$', 'QAS'),
    # not states, or outside the map's scope
    (r'^(Hashemite Arab Federation|Ghaznavid Empire|Delhi Sultanate|Kazakh Khanate)$', None),
]

# the map's first year for this era
Y0_10 = 1000
