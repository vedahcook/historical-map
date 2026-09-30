"""Spot checks of the medieval map (1000-1499) against well-documented facts. Run in the medieval era's folder.
Each check: place, year (as of July 1), and the country or countries the map may show there. Where two are allowed,
either the facts allow both (Toledo in 1100: Alfonso VI was king of both León and Castile; Besançon was a free city of the
Empire, not part of the Free County), or no source draws the smaller state (Tuscany in 1100, Carinthia after 1035,
Masovia after 1351), so the map shows the larger one."""
import pickle, shapely, sys
A = pickle.load(open('assign.pkl', 'rb')); F = pickle.load(open('faces.pkl', 'rb'))
K = A['KEYS']; Y = A['YEARS']; tree = shapely.STRtree(F['faces'])
C = {'London': (-0.13, 51.51), 'York': (-1.08, 53.96), 'Edinburgh': (-3.19, 55.95), 'Dublin': (-6.26, 53.35), 'Caernarfon': (-4.27, 53.14),
     'Douglas': (-4.48, 54.15), 'Kirkwall': (-2.96, 58.98), 'Oslo': (10.75, 59.91), 'Bergen': (5.32, 60.39), 'Stockholm': (18.07, 59.33),
     'Uppsala': (17.64, 59.86), 'Roskilde': (12.08, 55.64), 'Lund': (13.19, 55.7), 'Tallinn': (24.75, 59.44), 'Reykjavik': (-21.9, 64.1),
     'Paris': (2.35, 48.86), 'Rouen': (1.1, 49.44), 'Caen': (-0.37, 49.18), 'Bordeaux': (-0.58, 44.84), 'Poitiers': (0.34, 46.58),
     'Angers': (-0.55, 47.47), 'Le Mans': (0.2, 48.0), 'Rennes': (-1.68, 48.11), 'Dijon': (5.04, 47.32), 'Troyes': (4.07, 48.3),
     'Bruges': (3.22, 51.21), 'Ghent': (3.72, 51.05), 'Toulouse': (1.44, 43.6), 'Lyon': (4.84, 45.76), 'Avignon': (4.81, 43.95),
     'Marseille': (5.37, 43.3), 'Grenoble': (5.72, 45.19), 'Besancon': (6.02, 47.24), 'Calais': (1.86, 50.95), 'Nancy': (6.18, 48.69),
     'Strasbourg': (7.75, 48.58), 'Aachen': (6.08, 50.78), 'Cologne': (6.96, 50.94), 'Amsterdam': (4.9, 52.37), 'Brussels': (4.35, 50.85),
     'Liege': (5.57, 50.63), 'Luxembourg': (6.13, 49.61), 'Magdeburg': (11.63, 52.13), 'Goslar': (10.43, 51.9), 'Regensburg': (12.1, 49.02),
     'Munich': (11.58, 48.14), 'Vienna': (16.37, 48.21), 'Prague': (14.42, 50.08), 'Berlin': (13.4, 52.52), 'Hamburg': (9.99, 53.55),
     'Lubeck': (10.69, 53.87), 'Dresden': (13.74, 51.05), 'Zurich': (8.54, 47.37), 'Bern': (7.45, 46.95), 'Ulm': (9.99, 48.4),
     'Graz': (15.44, 47.07), 'Klagenfurt': (14.31, 46.62), 'Udine': (13.23, 46.06), 'Rome': (12.5, 41.9), 'Milan': (9.19, 45.46),
     'Venice': (12.33, 45.44), 'Genoa': (8.93, 44.41), 'Pisa': (10.4, 43.72), 'Florence': (11.25, 43.77), 'Siena': (11.33, 43.32),
     'Lucca': (10.5, 43.84), 'Verona': (10.99, 45.44), 'Padua': (11.88, 45.41), 'Naples': (14.27, 40.85), 'Salerno': (14.77, 40.68),
     'Bari': (16.87, 41.12), 'Amalfi': (14.6, 40.63), 'Palermo': (13.36, 38.12), 'Cagliari': (9.11, 39.22), 'Ajaccio': (8.74, 41.92),
     'Benevento': (14.78, 41.13), 'Cordoba': (-4.78, 37.89), 'Toledo': (-4.02, 39.86), 'Seville': (-5.98, 37.39), 'Granada': (-3.6, 37.18),
     'Zaragoza': (-0.88, 41.65), 'Valencia': (-0.38, 39.47), 'Barcelona': (2.17, 41.39), 'Leon': (-5.57, 42.6), 'Burgos': (-3.7, 42.34),
     'Santiago': (-8.54, 42.88), 'Coimbra': (-8.43, 40.21), 'Lisbon': (-9.14, 38.72), 'Pamplona': (-1.64, 42.81), 'Palma': (2.65, 39.57),
     'Murcia': (-1.13, 37.99), 'Almeria': (-2.46, 36.84), 'Badajoz': (-6.97, 38.88), 'Tunis': (10.18, 36.8), 'Kairouan': (10.1, 35.68),
     'Bejaia': (5.08, 36.75), 'Tlemcen': (-1.32, 34.88), 'Ceuta': (-5.32, 35.89), 'Tangier': (-5.81, 35.77), 'Istanbul': (28.97, 41.01),
     'Iznik': (29.72, 40.43), 'Bursa': (29.06, 40.19), 'Edirne': (26.56, 41.68), 'Thessaloniki': (22.94, 40.64), 'Athens': (23.73, 37.98),
     'Mistras': (22.37, 37.07), 'Arta': (20.99, 39.16), 'Heraklion': (25.13, 35.33), 'Rhodes': (28.22, 36.43), 'Nicosia': (33.36, 35.17),
     'Tarnovo': (25.63, 43.08), 'Ohrid': (20.8, 41.12), 'Skopje': (21.43, 42.0), 'Belgrade': (20.46, 44.82), 'Ragusa': (18.09, 42.65),
     'Zagreb': (15.98, 45.81), 'Visoko': (18.18, 43.99), 'Bucharest': (26.1, 44.43), 'Iasi': (27.59, 47.16), 'Cluj': (23.6, 46.77),
     'Buda': (19.04, 47.5), 'Bratislava': (17.11, 48.15), 'Konya': (32.49, 37.87), 'Sivas': (37.02, 39.75), 'Trabzon': (39.72, 41.0),
     'Antioch': (36.16, 36.2), 'Urfa': (38.79, 37.16), 'Tripoli': (35.84, 34.44), 'Kozan': (35.82, 37.45), 'Aleppo': (37.16, 36.2),
     'Mosul': (43.13, 36.34), 'Tbilisi': (44.79, 41.72), 'Ani': (43.57, 40.51), 'Tabriz': (46.29, 38.08), 'Kyiv': (30.52, 50.45),
     'Novgorod': (31.28, 58.52), 'Vladimir': (40.4, 56.13), 'Moscow': (37.62, 55.76), 'Tver': (35.91, 56.86), 'Smolensk': (32.05, 54.78),
     'Polotsk': (28.8, 55.49), 'Chernihiv': (31.3, 51.5), 'Halych': (24.72, 49.12), 'Lviv': (24.03, 49.84), 'Ryazan': (39.74, 54.63),
     'Pskov': (28.33, 57.82), 'Vilnius': (25.28, 54.69), 'Riga': (24.1, 56.95), 'Konigsberg': (20.51, 54.71), 'Gdansk': (18.65, 54.35),
     'Malbork': (19.03, 54.04), 'Krakow': (19.94, 50.06), 'Poznan': (16.93, 52.41), 'Wroclaw': (17.04, 51.11), 'Warsaw': (21.01, 52.23),
     'Plock': (19.7, 52.55), 'Szczecin': (14.55, 53.43), 'Kazan': (49.1, 55.8), 'Bolghar': (49.05, 54.98), 'Feodosia': (35.38, 45.03),
     'Bakhchysarai': (33.86, 44.75), 'Winchester': (-1.31, 51.06)}
T = [
    # British Isles
    ('London', 1000, 'ENG'), ('London', 1025, 'NSE'), ('London', 1050, 'ENG'), ('London', 1070, 'ENG'), ('London', 1300, 'ENG'),
    ('York', 1000, 'ENG'), ('Winchester', 1100, 'ENG'), ('Edinburgh', 1050, 'SCO'), ('Edinburgh', 1200, 'SCO'), ('Edinburgh', 1400, 'SCO'),
    ('Dublin', 1000, 'DUB'), ('Dublin', 1200, 'LIR'), ('Dublin', 1400, 'LIR'), ('Caernarfon', 1200, 'GWY'), ('Caernarfon', 1300, 'ENG'),
    ('Douglas', 1100, 'KIS'), ('Douglas', 1300, 'SCO'), ('Douglas', 1400, 'ENG'), ('Kirkwall', 1100, 'ORK'), ('Kirkwall', 1480, 'SCO'),
    # Scandinavia
    ('Oslo', 1100, 'NOR'), ('Oslo', 1450, 'DEN'), ('Bergen', 1200, 'NOR'), ('Stockholm', 1300, 'SWE'), ('Uppsala', 1100, 'SWE'),
    ('Roskilde', 1100, 'DEN'), ('Lund', 1100, 'DEN'), ('Lund', 1400, 'DEN'), ('Tallinn', 1230, 'DEN'), ('Tallinn', 1400, ('LIV', 'TEU')),
    ('Reykjavik', 1100, 'ISL'), ('Reykjavik', 1300, 'NOR'), ('Reykjavik', 1450, 'DEN'),
    # France
    ('Paris', 1000, 'FRA'), ('Paris', 1300, 'FRA'), ('Rouen', 1000, 'NMD'), ('Rouen', 1100, 'NMD'), ('Rouen', 1170, 'NMD_E'),
    ('Rouen', 1250, 'FRA'), ('Rouen', 1430, 'ENG'), ('Rouen', 1470, 'FRA'), ('Caen', 1080, 'NMD_E'),
    ('Bordeaux', 1000, 'AQU'), ('Bordeaux', 1200, 'AQU_E'), ('Bordeaux', 1300, 'AQU_E'), ('Bordeaux', 1400, ('ENG', 'AQU_E')), ('Bordeaux', 1460, 'FRA'),
    ('Poitiers', 1100, 'AQU'), ('Poitiers', 1180, ('AQU_E', 'ANJ_E')), ('Poitiers', 1250, 'FRA'), ('Angers', 1100, 'ANJ'), ('Angers', 1180, 'ANJ_E'),
    ('Angers', 1250, ('ANJ', 'FRA')), ('Le Mans', 1000, 'MAE'), ('Le Mans', 1180, 'ANJ_E'), ('Rennes', 1100, 'BRI'), ('Rennes', 1400, 'BRI'),
    ('Rennes', 1499, 'BRI'), ('Dijon', 1100, 'BUR'), ('Dijon', 1400, 'BGS'), ('Dijon', 1490, 'FRA'), ('Troyes', 1100, 'CHA'), ('Troyes', 1300, 'FRA'),
    ('Bruges', 1100, 'FLA'), ('Bruges', 1250, 'FLA'), ('Bruges', 1450, 'BGS'), ('Bruges', 1490, 'HNL'), ('Ghent', 1200, 'FLA'),
    ('Toulouse', 1100, 'TOU'), ('Toulouse', 1300, 'FRA'), ('Lyon', 1100, ('ARL', 'HRE')), ('Avignon', 1100, 'ARL'), ('Marseille', 1150, 'ARL'), ('Lyon', 1400, ('FRA', 'BOB')), ('Avignon', 1360, 'PAP'),
    ('Marseille', 1300, ('PRV', 'ARL')), ('Marseille', 1490, 'FRA'), ('Grenoble', 1200, 'DAU'), ('Grenoble', 1400, 'FRA'),
    ('Besancon', 1200, ('FCM', 'ARL', 'HRE')), ('Besancon', 1450, ('BGS', 'HRE')), ('Calais', 1400, 'ENG'), ('Calais', 1450, 'ENG'), ('Nancy', 1300, 'LOR'),
    # Low Countries and the Empire
    ('Strasbourg', 1300, 'HRE'), ('Aachen', 1100, ('HRE', 'LLO')), ('Cologne', 1300, ('KOL', 'HRE')), ('Amsterdam', 1300, 'HLD'),
    ('Amsterdam', 1450, 'BGS'), ('Amsterdam', 1490, 'HNL'), ('Brussels', 1300, 'BRB'), ('Brussels', 1450, 'BGS'), ('Brussels', 1490, 'HNL'),
    ('Liege', 1300, ('LGE', 'HRE')), ('Luxembourg', 1300, 'LUX'), ('Luxembourg', 1460, 'BGS'),
    ('Magdeburg', 1000, 'SXD'), ('Goslar', 1100, 'SXD'), ('Regensburg', 1000, 'BAV'), ('Munich', 1300, 'BAV'), ('Vienna', 1100, ('BAV', 'AUT', 'HRE')),
    ('Vienna', 1200, 'AUT'), ('Vienna', 1300, 'AUT'), ('Vienna', 1487, 'HUK'), ('Vienna', 1495, 'AUT'), ('Prague', 1000, 'BOK'), ('Prague', 1400, 'BOK'),
    ('Berlin', 1300, 'BRA'), ('Berlin', 1450, 'BRA'), ('Hamburg', 1100, 'SXD'), ('Lubeck', 1300, ('LUB', 'HRE')), ('Dresden', 1300, ('SAX', 'HRE')),
    ('Zurich', 1300, ('HRE', 'AUT')), ('Zurich', 1400, 'SUI'), ('Bern', 1400, 'SUI'), ('Ulm', 1100, 'SWA'), ('Graz', 1400, 'AUT'),
    ('Klagenfurt', 1050, ('CAR', 'HRE')), ('Udine', 1300, 'AQL'), ('Udine', 1450, 'VEN'),
    # Italy
    ('Rome', 1000, 'PAP'), ('Rome', 1300, 'PAP'), ('Milan', 1100, 'HRE'), ('Milan', 1400, 'MLS'), ('Milan', 1450, 'MLS'), ('Milan', 1499, 'MLS'),
    ('Venice', 1000, 'VEN'), ('Venice', 1300, 'VEN'), ('Genoa', 1200, 'GEN'), ('Pisa', 1200, 'PIS'), ('Pisa', 1420, 'TUS'),
    ('Florence', 1100, ('TSC', 'HRE')), ('Florence', 1300, 'TUS'), ('Siena', 1300, 'SIE'), ('Lucca', 1300, 'LUC'), ('Verona', 1300, 'VRN'),
    ('Verona', 1420, 'VEN'), ('Padua', 1420, 'VEN'), ('Naples', 1000, 'NPD'), ('Naples', 1100, 'NPD'), ('Naples', 1200, 'SIC_M'),
    ('Naples', 1300, 'NAP'), ('Naples', 1450, 'NAP'), ('Salerno', 1050, 'SLR'), ('Salerno', 1100, 'NRM'), ('Bari', 1000, 'BYZ'), ('Bari', 1100, 'NRM'),
    ('Amalfi', 1000, 'AMA'), ('Palermo', 1000, 'ESC'), ('Palermo', 1100, 'NRM'), ('Palermo', 1200, 'SIC_M'), ('Palermo', 1300, 'SIC'),
    ('Palermo', 1450, 'SIC_R'), ('Cagliari', 1100, 'CAG'), ('Cagliari', 1300, 'PIS'), ('Cagliari', 1400, 'SDR'), ('Ajaccio', 1100, 'PIS'),
    ('Ajaccio', 1300, 'GEN'), ('Benevento', 1100, ('BEN', 'NRM')),
    # Iberia and North Africa
    ('Cordoba', 1000, 'CRD'), ('Cordoba', 1100, 'ALV'), ('Cordoba', 1200, 'ALH'), ('Cordoba', 1300, 'CAS'), ('Toledo', 1050, 'TOL'),
    ('Toledo', 1100, ('CAS', 'LEO')), ('Seville', 1050, 'SEV'), ('Seville', 1100, 'ALV'), ('Seville', 1200, 'ALH'), ('Seville', 1300, 'CAS'),
    ('Granada', 1050, 'GRT'), ('Granada', 1100, 'ALV'), ('Granada', 1300, 'GRN'), ('Granada', 1491, 'GRN'), ('Granada', 1495, 'ESP'),
    ('Zaragoza', 1050, 'ZAR'), ('Zaragoza', 1150, 'ARA'), ('Valencia', 1050, 'VLC'), ('Valencia', 1250, 'ARA'), ('Barcelona', 1000, 'BCN'),
    ('Barcelona', 1200, 'ARA'), ('Barcelona', 1300, 'ARA'), ('Barcelona', 1480, 'ESP'), ('Leon', 1000, 'LEO'), ('Leon', 1250, 'CAS'),
    ('Burgos', 1000, ('CAS', 'LEO')), ('Burgos', 1200, 'CAS'), ('Santiago', 1000, 'LEO'), ('Coimbra', 1000, 'CRD'), ('Coimbra', 1100, ('POR_C', 'LEO')),
    ('Coimbra', 1200, 'POR'), ('Lisbon', 1100, 'ALV'), ('Lisbon', 1200, 'POR'), ('Pamplona', 1100, ('NAV', 'ARA')), ('Pamplona', 1200, 'NAV'),
    ('Palma', 1250, 'ARA'), ('Palma', 1300, 'MAJ'), ('Murcia', 1300, 'CAS'), ('Almeria', 1050, 'ALR'), ('Almeria', 1300, 'GRN'), ('Badajoz', 1050, 'BDJ'),
    ('Tunis', 1000, ('ZIR', 'FAT')), ('Tunis', 1200, 'ALH'), ('Tunis', 1300, 'HAF'), ('Kairouan', 1100, 'ZIR'), ('Bejaia', 1100, 'HMD'),
    ('Tlemcen', 1100, 'ALV'), ('Tlemcen', 1300, 'TLM'), ('Ceuta', 1450, 'POR'), ('Tangier', 1480, 'POR'),
    # Byzantium and the Balkans
    ('Istanbul', 1000, 'BYZ'), ('Istanbul', 1210, 'LAT'), ('Istanbul', 1300, 'BYZ'), ('Istanbul', 1460, 'OTT'), ('Iznik', 1100, 'BYZ'),
    ('Iznik', 1220, 'NIC'), ('Iznik', 1340, 'OTT'), ('Bursa', 1340, 'OTT'), ('Edirne', 1300, 'BYZ'), ('Edirne', 1380, 'OTT'),
    ('Thessaloniki', 1000, 'BYZ'), ('Thessaloniki', 1210, 'THL'), ('Thessaloniki', 1300, 'BYZ'), ('Thessaloniki', 1440, 'OTT'),
    ('Athens', 1300, 'ATH'), ('Athens', 1470, 'OTT'), ('Mistras', 1300, 'BYZ'), ('Mistras', 1470, 'OTT'), ('Arta', 1250, 'EPI'),
    ('Heraklion', 1000, 'BYZ'), ('Heraklion', 1300, 'VEN'), ('Rhodes', 1350, 'KHR'), ('Nicosia', 1300, 'CYK'), ('Nicosia', 1490, 'VEN'),
    ('Tarnovo', 1000, ('BYZ', 'BGE')), ('Tarnovo', 1250, 'BGE'), ('Tarnovo', 1400, 'OTT'), ('Ohrid', 1000, 'BGE'), ('Ohrid', 1100, 'BYZ'),
    ('Skopje', 1000, 'BGE'), ('Skopje', 1300, 'SRM'), ('Skopje', 1400, 'OTT'), ('Belgrade', 1300, ('SRM', 'HUK')), ('Belgrade', 1450, 'HUK'),
    ('Ragusa', 1400, 'RAG'), ('Zagreb', 1050, 'CRO'), ('Zagreb', 1200, 'HUK'), ('Visoko', 1300, 'BOS'), ('Visoko', 1470, 'OTT'),
    ('Bucharest', 1400, 'WAL_I'), ('Bucharest', 1450, 'WAL'), ('Iasi', 1400, 'MOL_I'), ('Iasi', 1480, 'MOL'), ('Cluj', 1300, 'HUK'),
    ('Buda', 1300, 'HUK'), ('Bratislava', 1300, 'HUK'),
    # Anatolia and the Near East
    ('Konya', 1000, 'BYZ'), ('Konya', 1150, 'RUM'), ('Konya', 1250, 'RUM'), ('Konya', 1350, ('KRM', 'ILK')), ('Konya', 1480, 'OTT'),
    ('Sivas', 1150, 'DSH'), ('Sivas', 1300, 'ILK'), ('Trabzon', 1300, 'TRE'), ('Trabzon', 1470, 'OTT'), ('Antioch', 1000, 'BYZ'),
    ('Antioch', 1100, 'ANT'), ('Antioch', 1300, 'MAM'), ('Urfa', 1100, 'EDE'), ('Urfa', 1150, 'ZNG'), ('Tripoli', 1150, 'TRP'),
    ('Tripoli', 1300, 'MAM'), ('Kozan', 1200, 'CIL'), ('Aleppo', 1200, 'AYY'), ('Aleppo', 1300, 'MAM'), ('Mosul', 1100, 'SEL'),
    ('Mosul', 1300, 'ILK'), ('Tbilisi', 1150, 'GEO'), ('Ani', 1000, 'ARB_A'), ('Tabriz', 1300, 'ILK'), ('Tabriz', 1450, 'QQY'),
    # the Rus', Poland, the Baltic, the steppe
    ('Kyiv', 1000, 'KIE'), ('Kyiv', 1200, 'PKV'), ('Kyiv', 1300, ('GOH', 'PKV')), ('Kyiv', 1400, 'LIT'), ('Novgorod', 1100, ('NVG', 'KIE')),
    ('Novgorod', 1300, 'NVG'), ('Novgorod', 1490, 'RUS'), ('Vladimir', 1200, 'VLS'), ('Moscow', 1400, 'RUS'), ('Tver', 1400, 'TVE'),
    ('Tver', 1490, 'RUS'), ('Smolensk', 1200, 'SMO'), ('Smolensk', 1450, 'LIT'), ('Polotsk', 1100, 'PLT'), ('Polotsk', 1400, 'LIT'),
    ('Chernihiv', 1100, 'CHN'), ('Halych', 1150, 'HLC'), ('Lviv', 1300, 'GVO'), ('Lviv', 1400, 'PLK'), ('Ryazan', 1200, 'RYA_I'),
    ('Pskov', 1400, 'PSK'), ('Vilnius', 1300, 'LIT'), ('Riga', 1250, ('LIV', 'TEU')), ('Konigsberg', 1300, 'TEU'), ('Gdansk', 1350, 'TEU'),
    ('Gdansk', 1480, 'PLK'), ('Malbork', 1400, 'TEU'), ('Malbork', 1470, 'PLK'), ('Krakow', 1000, 'PLK'), ('Krakow', 1200, 'LPL'),
    ('Krakow', 1350, 'PLK'), ('Poznan', 1200, 'GPL'), ('Wroclaw', 1200, 'SIL'), ('Wroclaw', 1400, 'BOK'), ('Warsaw', 1400, ('MAZ_P', 'MAZ', 'PLK')),
    ('Plock', 1200, ('MAZ', 'LPL')), ('Szczecin', 1300, 'POM'), ('Kazan', 1460, 'KZN'), ('Bolghar', 1100, 'VBU'), ('Bolghar', 1300, 'GOH'),
    ('Feodosia', 1300, 'GEN'), ('Feodosia', 1480, ('OTT', 'CRI')), ('Bakhchysarai', 1460, ('CRI_I', 'THD')), ('Bakhchysarai', 1490, 'CRI'),
]
bad = 0
for city, y, exp in T:
    lon, lat = C[city]
    i = tree.query(shapely.Point(lon, lat), predicate='within')
    if not len(i) or not F['land'][int(i[0])]:
        land_idx = [k for k in tree.query(shapely.Point(lon, lat).buffer(0.1)) if F['land'][k]]
        i = [min(land_idx, key=lambda k: F['faces'][k].distance(shapely.Point(lon, lat)))] if land_idx else []
    if not len(i): print('no face', city); bad += 1; continue
    i = int(i[0]); j = Y.index(y); u = A['def_u'][i, j]; got = K[u] if u >= 0 else None
    if got not in (exp if isinstance(exp, tuple) else (exp,)):
        bad += 1
        o, c = A['ohm_u'][i, j], A['cl_u'][i, j]
        print(f'MISMATCH {city} {y}: map {got}, expected {exp} (ohm {K[o] if o >= 0 else None}, clio {K[c] if c >= 0 else None}, src {A["def_src"][i, j]})')
print(f'{len(T) - bad} of {len(T)} checks match')
