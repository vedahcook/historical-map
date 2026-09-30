"""Units, OHM roles and Cliopatria names for 1500-1799 (the early era).

Loaded by units.py: UNITS15 is added to UNITS, R15 goes in front of the later roles (so it wins for
the early years it covers), C15 in front of the later Cliopatria names. Every role here stops by 1799,
unless the name only occurs before 1800, so the 1800-2026 map is unaffected.

Choices:
  - The Holy Roman Empire's circles and its many small members show as the Empire itself (HRE);
    its larger members show as their own states when OHM or Cliopatria draws them.
  - Kingdoms ruled from Madrid or Vienna through a viceroy or governor (Spanish Naples, Sicily,
    Sardinia and Milan; the Spanish and Austrian Netherlands; Austrian Naples and Milan) are drawn
    striped, under that overlord.
  - Poland and Lithuania are separate until the Union of Lublin (1569), then one Commonwealth.
  - Norway is part of Denmark-Norway throughout, as it is in the later map until 1814.
"""
E = 1799   # last year of the early era

# key: (display name, overlord key or None, color family)
UNITS15 = {
    # British Isles
    'ENG': ('England', None, 'GBR'), 'SCO': ('Scotland', None, 'SCO'), 'CMW': ('Commonwealth of England', None, 'CMW'),
    'GAE': ('Gaelic Irish lordships', None, 'GAE'), 'ICC': ('Confederate Ireland', None, 'ICC'),
    # France, Iberia, Low Countries, Switzerland
    'BRI': ('Brittany', None, 'BRI'), 'NAV': ('Navarre', None, 'NAV'),
    'HNL': ('Habsburg Netherlands', None, 'HNL'), 'SNL': ('Spanish Netherlands', 'ESP', 'HNL'), 'ANL': ('Austrian Netherlands', 'AUT', 'HNL'),
    'FCO': ('Franche-Comté', 'ESP', 'FCO'), 'GEL': ('Guelders', None, 'GEL'), 'LGE': ('Liège', None, 'LGE'),
    'BOU': ('Bouillon', None, 'BOU'), 'ORA': ('Orange', None, 'ORA'), 'GVA': ('Geneva', None, 'GVA'), 'GRI': ('Three Leagues', None, 'GRI'),
    'MUL': ('Mulhouse', None, 'MUL'), 'LOR': ('Lorraine', None, 'LOR'),
    # Italy and the Mediterranean
    'VEN': ('Venice', None, 'VEN'), 'MLS': ('Milan', None, 'MLN'), 'MIL_F': ('Milan (French)', 'FRA', 'MLN'),
    'MIL_S': ('Milan (Spanish)', 'ESP', 'MLN'), 'MIL_A': ('Milan (Austrian)', 'AUT', 'MLN'),
    'NAP_S': ('Naples (Spanish)', 'ESP', 'NAP'), 'NAP_A': ('Naples (Austrian)', 'AUT', 'NAP'),
    'SIC_S': ('Sicily (Spanish)', 'ESP', 'SIC'), 'SIC_V': ('Sicily (Savoyard)', 'SAV', 'SIC'), 'SIC_A': ('Sicily (Austrian)', 'AUT', 'SIC'),
    'SDS': ('Sardinia (Spanish)', 'ESP', 'SDS'), 'SDA': ('Sardinia (Austrian)', 'AUT', 'SDS'),
    'SAV': ('Savoy', None, 'SAR'), 'SIE': ('Siena', None, 'SIE'), 'MAN': ('Mantua', None, 'MAN'), 'MIR': ('Mirandola', None, 'MIR'),
    'GUA': ('Guastalla', None, 'GUA'), 'NOV': ('Novellara', None, 'NOV'), 'CST': ('Castro', None, 'CST'), 'SLZ': ('Saluzzo', None, 'SLZ'),
    'ITM': ('Imperial fiefs in Italy', None, 'ITM'), 'NOL': ('Noli', None, 'NOL'), 'ARC': ('Duchy of the Archipelago', 'VEN', 'ARC'),
    'COR': ('Corsica', None, 'COR'),
    # Central Europe
    'BOK': ('Bohemia', None, 'BOK'), 'HUK': ('Hungary', None, 'HUK'), 'TRS': ('Transylvania', 'OTT', 'TRS'), 'UHU': ('Upper Hungary (Thököly)', 'OTT', 'UHU'),
    'BRA': ('Brandenburg', None, 'PRU'), 'JUL': ('Jülich-Cleves-Berg', None, 'JUL'), 'PAL': ('Palatinate', None, 'PAL'),
    'POM': ('Pomerania', None, 'POM'), 'KOL': ('Electorate of Cologne', None, 'KOL'), 'MAI': ('Electorate of Mainz', None, 'MAI'),
    'TRR': ('Electorate of Trier', None, 'TRR'), 'MUN': ('Münster', None, 'MUN'), 'BAM': ('Bamberg', None, 'BAM'),
    'HGO': ('Holstein-Gottorp', None, 'HGO'), 'DIT': ('Dithmarschen', None, 'DIT'), 'EFR': ('East Frisia', None, 'EFR'),
    # Poland, the Baltic, Russia and the steppe
    'PLK': ('Kingdom of Poland', None, 'PLC'), 'LIT': ('Grand Duchy of Lithuania', None, 'LIT'), 'PLC': ('Polish–Lithuanian Commonwealth', None, 'PLC'),
    'DPR': ('Duchy of Prussia', 'PLK', 'DPR'), 'TEU': ('Teutonic Order', None, 'TEU'), 'LIV': ('Livonian Confederation', None, 'LIV'),
    'CRL': ('Courland', 'PLC', 'CRL'), 'KZN': ('Khanate of Kazan', None, 'KZN'), 'AST': ('Khanate of Astrakhan', None, 'AST'),
    'NOG': ('Nogai Horde', None, 'NOG'), 'GHO': ('Great Horde', None, 'GHO'), 'RYA': ('Ryazan', 'RUS', 'RYA'), 'PSK': ('Pskov', None, 'PSK'),
    'QAS': ('Qasim Khanate', 'RUS', 'QAS'), 'CRI': ('Crimean Khanate', 'OTT', 'CRI'), 'CRI_I': ('Crimean Khanate', None, 'CRI'),
    'ZAP': ('Zaporozhian Host', None, 'ZAP'), 'DON': ('Don Cossacks', None, 'DON'), 'KLM': ('Kalmyk Khanate', None, 'KLM'),
    # the Ottoman frontier, Persia, the Caucasus, North Africa
    'MAM': ('Mamluk Sultanate', None, 'MAM'), 'AQQ': ('Aq Qoyunlu', None, 'AQQ'), 'SHI': ('Shirvan', None, 'SHI'), 'IME': ('Imereti', None, 'IME'),
    'TLM': ('Tlemcen', None, 'TLM'), 'HAF': ('Hafsid Tunis', None, 'HAF'),
}

# (regex on the English name, level or None for any, unit, priority, from, to)
R15 = [
    # ---- umbrellas and the Empire ----
    (r'^Kalmar Union$', '2', 'DEN', 1, 0, E), (r'^Austrian Circle$', '3', 'AUT', 2, 0, E),
    (r'^Burgundian Circle$', '3', 'SNL', 2, 0, 1713), (r'^Burgundian Circle$', '3', 'ANL', 2, 1714, 1794),
    # ---- British Isles ----
    (r'^Kingdom of England$', '2', 'ENG', 2, 0, E), (r'^(Commonwealth|Commonwealth of England, Scotland and Ireland)$', '2', 'CMW', 2, 0, E),
    (r'^Kingdom of Scotland$', '2', 'SCO', 2, 0, E), (r'^Earldom of Orkney$', '4', 'SCO', 2, 0, E),
    (r'^Kingdom of Ireland$', '2', 'IRL', 2, 0, E), (r'^(Connacht|Leinster|Ulster|Clare)$', '4', 'IRL', 2, 0, E),
    (r'^Kingdom of (Leinster|Thomond|Desmond)$', '2', 'GAE', 2, 0, E), (r'^Irish Catholic Confederation$', '2', 'ICC', 2, 0, E),
    (r'^(Isle of Man|Guernsey|Jersey)$', '2', 'ENG', 2, 0, 1706), (r'^(Isle of Man|Guernsey|Jersey)$', '2', 'GBR', 2, 1707, E),
    (r'^(Pale of Calais)$', '3', 'ENG', 2, 0, E), (r'^Berwick-upon-Tweed$', '4', 'ENG', 2, 0, 1706), (r'^Dunkirk$', '4', 'ENG', 2, 1659, 1662),
    (r'^English Tangier$', '2', 'ENG', 2, 0, E), (r'^Gibraltar$', '2', 'GBR', 2, 0, E), (r'^Kingdom of Great Britain$', '2', 'GBR', 2, 0, E),
    # ---- France ----
    (r'^Kingdom of France$', '2', 'FRA', 2, 0, E), (r'^Duchy of Brittany$', '3', 'BRI', 2, 0, 1531),
    (r'^French Corsica$', '4', 'FRA', 2, 0, E), (r'^Corsican Republic$', '2', 'COR', 2, 0, E),
    (r'^County of Asti$', '4', 'FRA', 2, 0, 1530),
    # ---- Iberia and North Africa ----
    (r'^Spain$', '2', 'ESP', 2, 0, E), (r'^Kingdom of Navarre$', '2', 'NAV', 2, 0, E), (r'^Kingdom of Portugal$', '2', 'POR', 2, 0, E),
    (r'^Portuguese Ceuta$', '2', 'POR', 2, 0, E), (r'^Couto Misto$', None, None, 0, 0, E),
    (r'^(Mazalquivir|Oran|Peñón de Vélez de la Gomera|Peñón de Argel|Peñón de Alhucemas|Cazaza|Larache|La Mamora|Spanish Tunis)$', '4', 'ESP', 2, 0, E),
    (r'^Kingdom of Sardinia$', '4', 'SDS', 2, 0, 1707), (r'^Kingdom of Sardinia$', '4', 'SDA', 2, 1708, 1719),
    (r'^Kingdom of Majorca$', '4', 'ESP', 2, 0, E),
    (r'^Alawi Sultanate$', '2', 'MOR', 2, 0, E), (r'^Regency of Algiers$', '2', 'ALG', 2, 0, E),
    # ---- Low Countries ----
    (r'^Spanish Netherlands$', '2', 'SNL', 2, 0, E), (r'^Republic of the Seven United Netherlands$', '2', 'NLD', 2, 0, E),
    (r'^(County of Holland|County of Zeeland|Lordship of Utrecht|Lordship of Friesland|Lordship of Overijssel|Lordship of Groningen|Land of Drenthe|Friesland)$', '4', 'HNL', 2, 0, 1555),
    (r'^(County of Holland|County of Zeeland|Lordship of Utrecht|Lordship of Friesland|Lordship of Overijssel|Lordship of Groningen|Land of Drenthe)$', '4', 'SNL', 2, 1556, 1580),
    (r'^(County of Holland|County of Zeeland|Holland|Lordship of Utrecht|Lordship of Friesland|Lordship of Overijssel|Lordship of Groningen|Land of Drenthe)$', '4', 'NLD', 2, 1581, E),
    (r'^(County of Hainaut|County of Namur|Duchy of Luxembourg|Lordship of Mechelen|Cambrésis|County of Artois|Duchy of Limburg|Duchy of Brabant|County of Flanders|Bailiwick of Tournai|Landen van Overmaas)$', '4', 'HNL', 2, 0, 1555),
    (r'^(County of Hainaut|County of Namur|Duchy of Luxembourg|Lordship of Mechelen|Cambrésis|County of Artois|Duchy of Limburg|Duchy of Brabant|County of Flanders|Bailiwick of Tournai|Duchy of Upper Guelders)$', '4', 'SNL', 2, 1556, 1713),
    (r'^(County of Hainaut|County of Namur|Duchy of Luxembourg|Lordship of Mechelen|Duchy of Limburg|Duchy of Brabant|County of Flanders|Bailiwick of Tournai|Austrian Upper Guelders)$', '4', 'ANL', 2, 1714, 1794),
    (r'^Duchy of Guelders$', '4', 'GEL', 2, 0, 1542), (r'^Duchy of Guelders$', '4', 'HNL', 2, 1543, 1555), (r'^Duchy of Guelders$', '4', 'SNL', 2, 1556, 1580),
    (r'^Prince-Bishopric of Utrecht$', '4', 'HRE', 2, 0, 1527),
    (r'^Prince-Bishopric of Liège$', '4', 'LGE', 2, 0, E), (r'^Duchy of Bouillon$', '4', 'LGE', 2, 0, E),
    (r'^Sovereign Duchy of Bouillon$', '2', 'BOU', 2, 0, E), (r'^Principality of Orange$', '4', 'ORA', 2, 0, E),
    (r'^Free County of Burgundy$', '4', 'HNL', 2, 0, 1555), (r'^Free County of Burgundy$', '4', 'FCO', 2, 1556, 1678),
    (r'^Prussian \(Upper\) Guelders$', '4', 'PRU', 2, 0, E),
    # ---- Switzerland ----
    (r'^Swiss Confederacy$', '2', 'SUI', 2, 0, E), (r'^(Free Imperial City of Bern|Landgraviate of Thurgau)$', '4', 'SUI', 2, 0, E),
    (r'^Republic of Geneva$', None, 'GVA', 2, 0, E), (r'^Republic of Mulhouse$', None, 'MUL', 2, 0, E),
    (r'^Free State of the Three Leagues$', '3', 'GRI', 2, 0, E), (r'^Republic of the Seven Tithings$', '2', 'VAL', 2, 0, E),
    (r'^Principality of Neuchâtel$', '2', 'NEU', 2, 0, E), (r'^Principality of Neuchâtel$', '4', 'NEU', 2, 0, E),
    # ---- Italy ----
    (r'^Republic of Venice$', '2', 'VEN', 2, 0, E),
    (r'^(Kingdom of Candia|Venetian Cyprus|Venetian rule in the Ionian Islands|Kingdom of the Morea)$', '4', 'VEN', 2, 0, E),
    (r'^Duchy of the Archipelago$', '4', 'ARC', 3, 0, E),
    (r'^Duchy of Milan$', '4', 'MIL_F', 3, 0, 1511), (r'^Duchy of Milan$', '4', 'MLS', 3, 1512, 1514), (r'^Duchy of Milan$', '4', 'MIL_F', 3, 1515, 1521),
    (r'^Duchy of Milan$', '4', 'MLS', 3, 1522, 1535), (r'^(Duchy of Milan|State of Milan)$', '4', 'MIL_S', 3, 1536, 1706),
    (r'^Duchy of Milan$', '2', 'MIL_A', 3, 1707, E), (r'^Provincia di Lodi$', '4', 'MIL_A', 3, 0, E),
    (r'^(Republic of Genoa|Genoese Corsica)$', None, 'GEN', 2, 0, E), (r'^(Republic of Noli)$', None, 'NOL', 2, 0, E),
    (r'^(Duchy of Florence|Grand Duchy of Tuscany)$', None, 'TUS', 2, 0, E), (r'^Republic of Siena$', '4', 'SIE', 2, 0, E),
    (r'^Republic of Lucca$', None, 'LUC', 2, 0, E),
    (r'^(Margraviate of Mantua|Duchy of Mantua)$', None, 'MAN', 2, 0, E),
    (r'^(Duchy of Ferrara|Duchy of Modena and Reggio)$', None, 'MOD', 2, 0, E), (r'^Duchy of Parma and Piacenza$', None, 'PAR', 2, 0, E),
    (r'^Duchy of Massa and Carrara$', None, 'MAS', 2, 0, E), (r'^Duchy of Mirandola$', None, 'MIR', 2, 0, E),
    (r'^(County|Duchy) of Guastalla$', None, 'GUA', 2, 0, E), (r'^County of Novellara and Bagnolo$', None, 'NOV', 2, 0, E),
    (r'^(Lordship|Principality) of Piombino$', None, 'PIO', 2, 0, E), (r'^Duchy of Castro$', '4', 'CST', 2, 0, E),
    (r'^Marquisate of Saluzzo$', '4', 'SLZ', 2, 0, 1548),
    (r'^(County of Vernio|County of Santa Fiora|County of Sovana|County of Pitigliano)$', '4', 'ITM', 2, 0, E),
    (r'^Papal States$', '2', 'PAP', 2, 0, E), (r'^(Lordship of Rimini|Republic of Ancona)$', '3', 'PAP', 2, 0, E),
    (r'^Principality of Benevento \(Papal\)$', '3', 'BEN', 2, 0, E), (r'^Duchy of Pontecorvo$', '3', 'PON', 2, 0, E),
    (r'^Republic of Cospaia$', '2', 'COS', 2, 0, E), (r'^San Marino$', '2', 'SMR', 2, 0, E),
    (r'^Kingdom of Naples$', None, 'NAP', 2, 0, 1503), (r'^Kingdom of Naples$', None, 'NAP_S', 3, 1504, 1706),
    (r'^Kingdom of Naples$', None, 'NAP_A', 3, 1707, 1734), (r'^Kingdom of Naples$', None, 'NAP', 2, 1735, E),
    (r'^Neapolitan Republic \(1647–1648\)$', '2', 'NAP', 2, 0, E),
    (r'^Kingdom of Sicily$', None, 'SIC_S', 3, 0, 1713), (r'^Kingdom of Sicily$', None, 'SIC_V', 3, 1714, 1719),
    (r'^Kingdom of Sicily$', None, 'SIC_A', 3, 1720, 1734), (r'^Kingdom of Sicily$', None, 'SIC', 2, 1735, E),
    (r'^Savoyard state$', '3', 'SAV', 2, 0, 1719), (r'^Duchy of Savoy$', '4', 'SAV', 2, 0, 1719), (r'^Principality of Oneglia$', '3', 'SAV', 2, 0, 1719),
    (r'^(Savoyard state|Duchy of Savoy|Principality of Oneglia)$', None, 'SAR', 2, 1720, E), (r'^Kingdom of Sardinia$', '2', 'SAR', 2, 0, E),
    (r'^(Knights Hospitaller|Monastic State of the Order of Malta)$', '2', 'MLT', 2, 0, E),
    (r'^Republic of Ragusa$', '2', 'RAG', 2, 0, E),
    # ---- Holy Roman Empire: larger members ----
    (r'^(Bohemia|Moravia|Duchy of Krnov/Jägerndorf|Lands of the Bohemian Crown)$', None, 'BOK', 2, 0, 1526),
    (r'^(Bohemia|Moravia|Duchy of Krnov/Jägerndorf|Lands of the Bohemian Crown|Austrian Silesia|Further Austria|Sundgau|Triest|Duchy of Carniola|Gorizia and Gradisca)$', None, 'AUT', 2, 1527, E),
    (r'^Sundgau$', '4', 'AUT', 2, 0, 1526), (r'^(Triest|Duchy of Carniola)$', '4', 'AUT', 2, 0, 1526),
    (r'^(Duchy of Bavaria|Electorate of Bavaria)$', '4', 'BAV', 2, 0, E), (r'^Principality of Palatinate-Sulzbach$', '4', 'PAL', 2, 0, E),
    (r'^Duchy of Palatinate-Zweibrücken$', '4', 'PAL', 2, 0, E),
    (r'^Brandenburg$', '3', 'BRA', 2, 0, 1700), (r'^Brandenburg-Prussia$', '3', 'BRA', 2, 0, 1700), (r'^(Brandenburg|Brandenburg-Küstrin|Lordship of Ruppin)$', '4', 'BRA', 2, 0, 1700),
    (r'^Electorate of Brandenburg$', '4', 'BRA', 2, 0, 1700), (r'^(Electorate of Brandenburg|Duchy of Magdeburg|Minden-Ravensberg|Silesia|Netze District|Province of East Prussia|General Directory of War and Finance in Pomerania|Kriegs- und Domänenkammer Minden|Kammer-Deputation für Lingen und Tecklenburg)$', '4', 'PRU', 2, 1701, 1794),
    (r'^Duchy of Magdeburg$', '4', 'BRA', 2, 0, 1700), (r'^Minden-Ravensberg$', '4', 'BRA', 2, 0, 1700),
    (r'^Kingdom of Prussia$', '2', 'PRU', 2, 0, E),
    (r'^Duchy of Prussia$', '3', 'DPR', 3, 0, 1656), (r'^Duchy of Prussia$', '4', 'DPR', 3, 0, 1656), (r'^Duchy of Prussia$', None, 'BRA', 2, 1657, 1700),
    (r'^State of the Teutonic Order$', '2', 'TEU', 2, 0, E),
    (r'^(Duchy of Cleves|County of Mark|Duchy of Berg|County of Ravensberg)$', '4', 'JUL', 2, 0, 1613),
    (r'^(Duchy of Cleves|County of Mark|County of Ravensberg)$', '4', 'BRA', 2, 1614, 1700), (r'^Duchy of Berg$', '4', 'PAL', 2, 1614, 1794),
    (r'^(Duchy of Cleves|County of Mark)$', '4', 'PRU', 2, 1701, 1794),
    (r'^Duchy of Pomerania$', '4', 'POM', 2, 0, E), (r'^(Swedish Pomerania|Swedish Wismar|Duchy of Estonia|Swedish Livonia|Swedish Ingria.*)$', None, 'SWE', 2, 0, 1794),
    (r'^(Bremen-Verden|Principality of Verden)$', '4', 'SWE', 2, 0, 1714), (r'^(Bremen-Verden|Principality of Verden)$', '4', 'HAN', 2, 1715, 1794),
    (r'^Electorate of Cologne$', '4', 'KOL', 2, 0, E), (r'^Electorate of Mainz$', '4', 'MAI', 2, 0, E),
    (r'^(Prince-Bishopric of Münster|Munster)$', '4', 'MUN', 2, 0, E), (r'^Prince-Bishopric of Würzburg$', '4', 'WRZ', 2, 0, E),
    (r'^Prince-Bishopric of Bamberg$', '4', 'BAM', 2, 0, E), (r'^Prince-Archbishopric of Salzburg$', '4', 'SAL', 2, 0, E),
    (r'^Hanover$', '4', 'HAN', 2, 0, 1794), (r'^Hesse-Kassel$', '4', 'HKA', 2, 0, 1794), (r'^Hesse-Darmstadt$', '4', 'HDA', 2, 0, 1794),
    (r'^(Margraviate of Baden-Durlach|Margraviate of Baden-Baden|Margraviate of Baden)$', '4', 'BAD', 2, 0, 1794),
    (r'^Nassau-Weilburg$', '4', 'NAS', 2, 0, 1794), (r'^County of Nassau-Saarbrücken$', '4', 'NAS', 2, 0, E),
    (r'^(Waldeck)$', '4', 'WALD', 2, 0, 1794), (r'^Lippe$', '4', 'LIP', 2, 0, 1794), (r'^Schaumburg-Lippe$', '4', 'SCH', 2, 0, 1794),
    (r'^Principality of Anhalt-', '4', 'ANH', 2, 0, 1794), (r'^(County|Principality) of Schwarzburg', '4', 'SWB', 2, 0, 1794),
    (r'^(Duchy of Saxe-Weissenfels|Duchy of Saxe-Zeitz|Principality of Saxe-Querfurt|Electorate of Saxony)$', '4', 'SAX', 2, 0, 1794),
    (r'^Duchy of Saxony$', '4', 'SXO', 2, 0, E),
    (r'^Duchy of Mecklenburg-Schwerin$', '4', 'MKS', 2, 0, 1794), (r'^Duchy of Mecklenburg-Strelitz$', '4', 'MKST', 2, 0, 1794),
    (r'^County of Oldenburg$', '4', 'OLD', 2, 0, 1666), (r'^County of Oldenburg$', '4', 'DEN', 2, 1667, E), (r'^Duchy of Oldenburg$', '4', 'OLD', 2, 0, 1794),
    (r'^(County of East Frisia|Principality of East Frisia)$', '4', 'EFR', 2, 0, 1743),
    (r'^Duchy of Schleswig-Holstein-Gottorp$', None, 'HGO', 2, 0, E), (r'^Bauernrepublik Dithmarschen$', '4', 'DIT', 2, 0, E),
    (r'^Duchy of Schleswig$', '4', 'DEN', 2, 0, E),
    (r'^Free and Hanseatic City of Lübeck$', '4', 'LUB', 2, 0, 1794), (r'^Bremen$', '4', 'BRE', 2, 0, 1794),
    (r'^Liechtenstein$', '4', 'LIE', 2, 0, 1794), (r'^Hohenzollern-Hechingen$', '4', 'HOH', 2, 0, 1794),
    (r'^County of Hohengeroldseck$', '4', 'HGE', 2, 0, E),
    (r'^(Duchy of Lorraine|Duchy of Bar)$', '4', 'LOR', 2, 0, E),
    (r'^(Duchy of Upper Guelders)$', '4', 'SNL', 2, 0, E),
    # ---- Scandinavia ----
    (r'^(Kingdom of Denmark|Kingdom of Norway|Denmark–Norway)$', None, 'DEN', 2, 0, E), (r'^(Iceland|Faroe Islands|Bornholm County)$', '4', 'DEN', 2, 0, E),
    (r'^(Kingdom of Sweden|Swedish Empire|Sweden)$', None, 'SWE', 2, 0, E),
    # ---- Poland, the Baltic, Russia ----
    (r'^Royal Prussia$', '3', 'PLK', 2, 0, E),
    (r'^(Kraków|Sandomierz|Kalisz|Sieradz|Łęczyca|Poznań|Inowrocław|Brześć Kujawski|Płock|Rawa|Lublin|Masovian|Ruthenian|Bełz|Podolian|Chełmno|Malbork|Pomeranian) Voivodeship', '4', 'PLK', 2, 0, 1568),
    (r'^(Vilnius|Trakai|Podlaskie|Volhynian|Bracław.*|Chernihiv.*) Voivodeship|^Duchy of Samogitia$', '4', 'LIT', 2, 0, 1568),
    (r'Voivodeship|^Duchy of Samogitia$|^Duchy of Siewierz$|^Prince-Bishopric of Warmia$', '4', 'PLC', 2, 1569, 1795),
    (r'^Duchy of Siewierz$|^Prince-Bishopric of Warmia$', '4', 'PLK', 2, 0, 1568),
    (r'^(Poland-Lithuania|Crown of the Kingdom of Poland|Grand Duchy of Lithuania)$', None, 'PLC', 2, 0, E),
    (r'^Duchy of Courland and Semigallia$', '2', 'CRL', 3, 0, E),
    (r'^(Archbishopric of Riga|Bishopric of Courland|Bishopric of Dorpat|Bishopric of Ösel-Wiek)$', '2', 'LIV', 2, 0, E),
    (r'^Grand Principality of Moscow$', '2', 'RUS', 2, 0, E), (r'^Tsardom of Russia$', '2', 'RUS', 2, 0, E), (r'^Russian Empire$', '2', 'RUS', 2, 0, E),
    (r'^(Shelonskaya Pyatina|Vodskaya Pyatina)$', '4', 'RUS', 2, 0, E), (r'Governorate$|Viceroyalty$', '4', 'RUS', 2, 0, 1794),
    (r'^Principality of Ryazan$', '2', 'RYA', 3, 0, E), (r'^Qasim Khanate$', '3', 'QAS', 3, 0, E),
    (r'^Khanate of Qazan$', '2', 'KZN', 2, 0, E), (r'^Khanate of Astrakhan$', None, 'AST', 2, 0, E), (r'^Nogai Horde$', '2', 'NOG', 2, 0, E),
    (r'^Great Horde$', '2', 'GHO', 2, 0, E),
    (r'^Crimean Khanate$', '4', 'CRI', 3, 0, 1773), (r'^Crimean Khanate$', '2', 'CRI_I', 2, 0, E),
    (r'^Zaporoże$', '3', 'ZAP', 2, 0, E),
    # ---- Ottoman Empire and its neighbors ----
    (r'^Ottoman Empire$', '2', 'OTT', 2, 0, E), (r'^(Eyalet of Cyprus|Eyalet of Crete|Eyalet of the Morea|Rumelia Eyalet|Temeşvar Eyâlet)$', '4', 'OTT', 2, 0, E),
    (r'^Principality of Wallachia$', '3', 'WAL', 3, 0, E), (r'^Prince-Bishopric of Montenegro$', '2', 'MNE', 2, 0, E),
    (r'^Kingdom of Hungary$', '2', 'HUK', 2, 0, E), (r'^(Kingdom of Slavonia|Circulus .*)$', None, 'HUK', 2, 0, E),
    (r'^(Transylvania|Banat of Temeswar|Slavonian Military Frontier|Banat Military Frontier|City of Fiume and its District|Galicia and Lodomeria|West Galicia|Bukovina)$', None, 'AUT', 2, 0, E),
    (r'^Mamluk Sultanate$', '2', 'MAM', 2, 0, E),
    (r'^(Afsharid Empire|Zandiyeh|Qajar Iran)$', '2', 'PER', 2, 0, E), (r'^(Erivan Khanate|Nakhichevan Khanate)$', '4', 'PER', 2, 0, E),
    (r'^Kingdom of Kartli-Kakheti$', '2', 'GEO', 2, 0, E),
    # French provinces and other subdivisions: the country record decides
    (r'^(County of Maine|County of Angoulême|County of Vendôme|County of La Marche|Duchy of Nemours|Provence|Roussillon|the Dauphiné|Alsace|Franche-Comté|Lorraine and Barrois|Three Bishoprics|French Flanders|County of Saint-Pol)$', '4', None, 0, 0, E),
    (r'^(Señorío de Vizcaya|Guipúzcoa|Lordship of Oñate|Kingdom of Córdoba|Navarre|Menorca|Margraviate of Istria|Jämtland|Härjedalen|Debatable Lands)$', '4', None, 0, 0, E),
    (r'^(County of Molise|Terra di Lavoro|Aprutium .*|Principato Ultra|Principatus Ulterior)$', '4', None, 0, 0, E),
]

# any other level-4 record in the Empire: one of its many small states
import re
HRE_MINOR15 = re.compile(r'^(Free Imperial City|Imperial (City|Abbey|County|Lordship)|Prince-(Bishopric|Archbishopric|Provostry)|Princely Abbey|'
                         r'Freies Reichsdorf|County of|Lordship of|Imperial Lordship|Saint Blaise|Rhinegraviate|Wild- and Rhinegraviate|Sayn-|Principality of '
                         r'(Bayreuth|Ansbach|Hohenlohe|Salm-Salm|Hildesheim|Paderborn|Verden)|Hohenzollern-|Duchy of Arenberg)')

# Cliopatria names for polities of 1500-1799 (regex, unit); checked before the later list
C15 = [
    (r'^Kingdom of England$', 'ENG'), (r'^Commonwealth of England$', 'CMW'), (r'^Kingdom of Scotland$', 'SCO'),
    (r'^Irish Catholic Confederation$', 'ICC'), (r'^Kingdom of France$', 'FRA'), (r'^Crown of Castile$|^Crown of Aragon$|^Kingdom of Spain$|^Spanish Empire$|^Pro-Habsburg Spain$', 'ESP'),
    (r'^Iberian Union$', 'ESP'), (r'^Portuguese Empire$|^Portuguese Africa$', 'POR'),
    (r'^County of (Nevers|Auvergne|Foix|Armagnac)$|^House of Bourbon$', 'FRA'), (r'^Comtat Venaissin$', 'PAP'), (r'^Principality of Orange$', 'ORA'),
    (r'^County of Savoy$|^House of Savoy$', 'SAV'), (r'^Duchy of Lorraine$', 'LOR'), (r'^Dutch Republic$|^Union of Utrecht$', 'NLD'),
    (r'^Swiss Confederation$', 'SUI'), (r'^Republic of Florence$', 'TUS'), (r'^Duchy of Milan$', 'MLS'), (r'^Republic of Venice$', 'VEN'),
    (r'^Republic of Genoa$', 'GEN'), (r'^Papal States$', 'PAP'), (r'^Kingdom of Naples$', 'NAP'), (r'^Corsican Republic$', 'COR'),
    (r'^Habsburg Monarchy$|^House of Habsburg$|^Duchy of Styria$', 'AUT'), (r'^Kingdom of Bohemia$', 'BOK'), (r'^Kingdom of Hungary$', 'HUK'),
    (r'^Eastern Hungarian Kingdom$|^Principality of Transylvania$', 'TRS'), (r'^Principality of Upper Hungary$', 'UHU'),
    (r'^Electorate of Brandenburg$|^Brandenburg-Prussia$', 'BRA'), (r'^Duchy of Prussia$', 'DPR'), (r'^Teutonic Order$', 'TEU'),
    (r'^Electorate of Trier$', 'TRR'), (r'^Electorate of Saxony$', 'SAX'), (r'^Duchy of Bavaria$', 'BAV'), (r'^Electorate of Hanover$', 'HAN'),
    (r'^Kingdom of Prussia$', 'PRU'), (r'^Principality of Liechtenstein$', 'LIE'), (r'^Holy Roman Empire$', 'HRE'),
    (r'^House of Jagiellon$', 'PLK'), (r'^Polish-Lithuanian Commonwealth$|^Pro-Swedish Poland$', 'PLC'), (r'^Duchy of Courland$', 'CRL'),
    (r'^Livonian Conference$', 'LIV'), (r'^Kalmar Union$', 'DEN'), (r'^Denmark-Norway$', 'DEN'), (r'^Kingdom of Sweden$|^Swedish Empire$', 'SWE'),
    (r'^Grand Principality of Moscow$|^Tsardom of Russia$|^Russian Empire$', 'RUS'), (r'^Ryazan$', 'RYA'), (r'^Pskov Republic$', 'PSK'),
    (r'^Qasim Khanate$', 'QAS'), (r'^Khanate of Kazan$', 'KZN'), (r'^Astrakhan Khanate$', 'AST'), (r'^Nogai Horde$', 'NOG'), (r'^Golden Horde$', 'GHO'),
    (r'^Crimean Khanate$', 'CRI'), (r'^Zaporozhian Cossacks$', 'ZAP'), (r'^Don Cossacks$', 'DON'), (r'^Kalmyk Khanate$', 'KLM'),
    (r'^Sloboda Ukraine$', 'RUS'), (r'^Nalyvaiko Uprising$', None), (r'^Huguenots$|^Catalonia$', None),
    (r'^Kazakh Khanate$|^Small Horde$|^Timurid Empire$|^English Colonial Empire$|^British Colonial Empire$', None),
    (r'^Mamluk Sultanate$|^Beylik of Dulkadir$|^Ramadanid Emirate$', 'MAM'), (r'^Aq Qoyunlu$', 'AQQ'), (r'^Shirvan$', 'SHI'),
    (r'^Safavid Dynasty$|^Afsharid Iran$|^Zand Dynasty$|^Hotaki Dynasty$', 'PER'), (r'^Kingdom of Imereti$', 'IME'),
    (r'^Kingdom of (Georgia|Kartli|Kakheti)$', 'GEO'), (r'^Samtskhe-Saatabago$', 'GEO'),
    (r'^Zayyanid dynasty$', 'TLM'), (r'^Hafsid Dynasty$', 'HAF'), (r'^Wattasid dynasty$|^Saadi Sultanate$', 'MOR'),
    (r'^Principality of Moldavia$', 'MOL'), (r'^Principality of Wallachia$', 'WAL'), (r'^Republic of Ragusa$', 'RAG'),
    (r'^Principality of Monaco$', 'MON'), (r'^Karamanli Dynasty$', None),
]
