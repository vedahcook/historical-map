"""Spot checks of the early map (1500-1799) against well-documented facts. Run in the early era's folder.
Each check: place, year (as of July 1), and the country or countries the map may show there."""
import pickle, shapely
A = pickle.load(open('assign.pkl', 'rb')); F = pickle.load(open('faces.pkl', 'rb'))
K = A['KEYS']; Y = A['YEARS']; tree = shapely.STRtree(F['faces'])
C = {'Granada': (-3.6, 37.18), 'Naples': (14.27, 40.85), 'Milan': (9.19, 45.46), 'Palermo': (13.36, 38.12), 'Cagliari': (9.11, 39.22),
     'Brussels': (4.35, 50.85), 'Amsterdam': (4.9, 52.37), 'Lille': (3.06, 50.63), 'Besancon': (6.02, 47.24), 'Strasbourg': (7.75, 48.58),
     'Nancy': (6.18, 48.69), 'Buda': (19.04, 47.5), 'Belgrade': (20.46, 44.82), 'Vienna': (16.37, 48.21), 'Prague': (14.42, 50.08),
     'Krakow': (19.94, 50.06), 'Vilnius': (25.28, 54.69), 'Warsaw': (21.01, 52.23), 'Konigsberg': (20.51, 54.71), 'Riga': (24.1, 56.95),
     'Tallinn': (24.75, 59.44), 'Stockholm': (18.07, 59.33), 'Helsinki': (24.94, 60.17), 'Oslo': (10.75, 59.91), 'Malmo': (13.0, 55.6),
     'Kazan': (49.1, 55.8), 'Astrakhan': (48.03, 46.35), 'Smolensk': (32.05, 54.78), 'Kyiv': (30.52, 50.45), 'Bakhchysarai': (33.86, 44.75),
     'Istanbul': (28.97, 41.01), 'Rhodes': (28.22, 36.43), 'Valletta': (14.51, 35.9), 'Nicosia': (33.36, 35.17), 'Heraklion': (25.13, 35.33),
     'Corfu': (19.92, 39.62), 'Ragusa': (18.09, 42.65), 'Algiers': (3.06, 36.75), 'Oran': (-0.64, 35.7), 'Ceuta': (-5.32, 35.89),
     'Lisbon': (-9.14, 38.72), 'Gibraltar': (-5.35, 36.14), 'Mahon': (4.27, 39.89), 'Dublin': (-6.26, 53.35), 'Edinburgh': (-3.19, 55.95),
     'Calais': (1.86, 50.95), 'Pamplona': (-1.64, 42.81), 'Rennes': (-1.68, 48.11), 'Geneva': (6.14, 46.2), 'Bern': (7.45, 46.95),
     'Chambery': (5.92, 45.57), 'Nice': (7.27, 43.7), 'Turin': (7.69, 45.07), 'Florence': (11.25, 43.77), 'Siena': (11.33, 43.32),
     'Lucca': (10.5, 43.84), 'Mantua': (10.79, 45.16), 'Modena': (10.93, 44.65), 'Parma': (10.33, 44.8), 'Ferrara': (11.62, 44.84),
     'Bologna': (11.34, 44.49), 'Venice': (12.33, 45.44), 'Ajaccio': (8.74, 41.92), 'Munich': (11.58, 48.14), 'Dresden': (13.74, 51.05),
     'Berlin': (13.4, 52.52), 'Heidelberg': (8.69, 49.41), 'Mainz': (8.27, 50.0), 'Trier': (6.64, 49.75), 'Hanover': (9.73, 52.37),
     'Kassel': (9.48, 51.31), 'Szczecin': (14.55, 53.43), 'Gdansk': (18.65, 54.35), 'Lviv': (24.03, 49.84), 'Chernihiv': (31.3, 51.5),
     'Iasi': (27.59, 47.16), 'Bucharest': (26.1, 44.43), 'Aleppo': (37.16, 36.2), 'Damascus': (36.29, 33.5), 'Moscow': (37.62, 55.76),
     'Paris': (2.35, 48.86), 'Madrid': (-3.7, 40.42), 'Copenhagen': (12.57, 55.68), 'Rome': (12.5, 41.9), 'Liege': (5.57, 50.63),
     'Luxembourg': (6.13, 49.61), 'Tunis': (10.18, 36.8), 'Cluj': (23.6, 46.77), 'Bratislava': (17.11, 48.15), 'Novgorod': (31.28, 58.52),
     'Pskov': (28.33, 57.82), 'Ryazan': (39.74, 54.63)}
T = [('Granada', 1500, 'ESP'), ('Madrid', 1600, 'ESP'), ('Paris', 1600, 'FRA'), ('Moscow', 1600, 'RUS'), ('Rome', 1600, 'PAP'),
     ('Naples', 1500, 'NAP'), ('Naples', 1510, 'NAP_S'), ('Naples', 1720, 'NAP_A'), ('Naples', 1740, 'NAP'),
     ('Milan', 1505, 'MIL_F'), ('Milan', 1530, 'MLS'), ('Milan', 1600, 'MIL_S'), ('Milan', 1720, 'MIL_A'),
     ('Palermo', 1600, 'SIC_S'), ('Palermo', 1715, 'SIC_V'), ('Palermo', 1725, 'SIC_A'), ('Palermo', 1740, 'SIC'),
     ('Cagliari', 1600, ('SDS', 'ESP')), ('Cagliari', 1716, 'SDA'), ('Cagliari', 1725, 'SAR'),
     ('Brussels', 1520, 'HNL'), ('Brussels', 1600, 'SNL'), ('Brussels', 1750, 'ANL'), ('Brussels', 1796, 'FRA'),
     ('Amsterdam', 1600, 'NLD'), ('Amsterdam', 1700, 'NLD'), ('Lille', 1660, 'SNL'), ('Lille', 1670, 'FRA'),
     ('Besancon', 1660, 'FCO'), ('Besancon', 1680, 'FRA'), ('Strasbourg', 1690, 'FRA'), ('Nancy', 1700, 'LOR'), ('Nancy', 1770, 'FRA'),
     ('Buda', 1520, 'HUK'), ('Buda', 1600, 'OTT'), ('Buda', 1700, 'AUT'), ('Belgrade', 1600, 'OTT'), ('Belgrade', 1725, 'AUT'), ('Belgrade', 1745, 'OTT'),
     ('Vienna', 1600, 'AUT'), ('Prague', 1500, 'BOK'), ('Prague', 1600, 'AUT'), ('Bratislava', 1600, 'AUT'),
     ('Krakow', 1500, 'PLK'), ('Krakow', 1600, 'PLC'), ('Warsaw', 1796, 'PRU'), ('Vilnius', 1500, 'LIT'), ('Vilnius', 1600, 'PLC'), ('Vilnius', 1796, 'RUS'),
     ('Konigsberg', 1500, 'TEU'), ('Konigsberg', 1600, 'DPR'), ('Konigsberg', 1710, 'PRU'),
     ('Riga', 1500, ('LIV', 'TEU')), ('Riga', 1600, 'PLC'), ('Riga', 1650, 'SWE'), ('Riga', 1725, 'RUS'), ('Tallinn', 1600, 'SWE'), ('Tallinn', 1725, 'RUS'),
     ('Stockholm', 1600, 'SWE'), ('Helsinki', 1700, 'SWE'), ('Oslo', 1600, 'DEN'), ('Copenhagen', 1600, 'DEN'), ('Malmo', 1600, 'DEN'), ('Malmo', 1670, 'SWE'),
     ('Kazan', 1500, 'KZN'), ('Kazan', 1560, 'RUS'), ('Astrakhan', 1500, ('AST', 'GHO')), ('Astrakhan', 1560, 'RUS'),
     ('Novgorod', 1500, 'RUS'), ('Pskov', 1500, 'PSK'), ('Pskov', 1520, 'RUS'), ('Ryazan', 1500, 'RYA'), ('Ryazan', 1530, 'RUS'),
     ('Smolensk', 1500, 'LIT'), ('Smolensk', 1520, 'RUS'), ('Smolensk', 1620, 'PLC'), ('Smolensk', 1670, 'RUS'),
     ('Kyiv', 1600, 'PLC'), ('Kyiv', 1690, 'RUS'), ('Chernihiv', 1510, 'RUS'), ('Chernihiv', 1630, 'PLC'),
     ('Bakhchysarai', 1600, 'CRI'), ('Bakhchysarai', 1790, 'RUS'), ('Istanbul', 1500, 'OTT'),
     ('Rhodes', 1500, 'MLT'), ('Rhodes', 1530, 'OTT'), ('Valletta', 1600, 'MLT'), ('Nicosia', 1500, 'VEN'), ('Nicosia', 1580, 'OTT'),
     ('Heraklion', 1600, 'VEN'), ('Heraklion', 1680, 'OTT'), ('Corfu', 1600, 'VEN'), ('Ragusa', 1600, 'RAG'),
     ('Algiers', 1530, 'ALG'), ('Oran', 1520, 'ESP'), ('Oran', 1720, 'ALG'), ('Oran', 1740, 'ESP'), ('Ceuta', 1500, 'POR'), ('Ceuta', 1700, 'ESP'),
     ('Tunis', 1500, 'HAF'), ('Lisbon', 1550, 'POR'), ('Lisbon', 1600, ('POR', 'ESP')), ('Lisbon', 1700, 'POR'),
     ('Gibraltar', 1720, 'GBR'), ('Mahon', 1720, 'GBR'), ('Mahon', 1760, 'FRA'), ('Mahon', 1790, 'ESP'),
     ('Dublin', 1600, 'IRL'), ('Dublin', 1655, 'CMW'), ('Edinburgh', 1600, 'SCO'), ('Edinburgh', 1710, 'GBR'),
     ('Calais', 1550, 'ENG'), ('Calais', 1560, 'FRA'), ('Pamplona', 1500, 'NAV'), ('Pamplona', 1520, 'ESP'), ('Rennes', 1500, 'BRI'), ('Rennes', 1540, 'FRA'),
     ('Geneva', 1600, 'GVA'), ('Bern', 1600, 'SUI'), ('Chambery', 1600, 'SAV'), ('Chambery', 1725, 'SAR'), ('Nice', 1600, 'SAV'), ('Nice', 1795, 'FRA'), ('Chambery', 1795, 'FRA'),
     ('Turin', 1600, 'SAV'), ('Turin', 1725, 'SAR'), ('Florence', 1500, 'TUS'), ('Siena', 1500, 'SIE'), ('Siena', 1560, 'TUS'), ('Lucca', 1600, 'LUC'),
     ('Mantua', 1600, 'MAN'), ('Mantua', 1720, ('MIL_A', 'AUT')), ('Modena', 1600, 'MOD'), ('Parma', 1600, 'PAR'), ('Ferrara', 1500, 'MOD'), ('Ferrara', 1600, 'PAP'),
     ('Bologna', 1600, 'PAP'), ('Venice', 1600, 'VEN'), ('Venice', 1798, 'AUT'), ('Ajaccio', 1600, 'GEN'), ('Ajaccio', 1760, 'COR'), ('Ajaccio', 1770, 'FRA'),
     ('Munich', 1600, 'BAV'), ('Dresden', 1600, 'SAX'), ('Berlin', 1600, 'BRA'), ('Berlin', 1710, 'PRU'), ('Heidelberg', 1600, 'PAL'),
     ('Mainz', 1600, 'MAI'), ('Trier', 1600, 'TRR'), ('Hanover', 1750, 'HAN'), ('Kassel', 1600, 'HKA'), ('Liege', 1600, 'LGE'), ('Liege', 1796, 'FRA'),
     ('Luxembourg', 1600, 'SNL'), ('Luxembourg', 1750, 'ANL'), ('Luxembourg', 1796, 'FRA'),
     ('Szczecin', 1600, 'POM'), ('Szczecin', 1660, 'SWE'), ('Szczecin', 1730, 'PRU'), ('Gdansk', 1600, 'PLC'), ('Gdansk', 1796, 'PRU'),
     ('Lviv', 1600, 'PLC'), ('Lviv', 1780, 'AUT'), ('Iasi', 1600, 'MOL'), ('Bucharest', 1650, 'WAL'), ('Cluj', 1650, 'TRS'), ('Cluj', 1720, 'AUT'),
     ('Aleppo', 1500, 'MAM'), ('Aleppo', 1520, 'OTT')]
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
        bad += 1; print(f'MISMATCH {city} {y}: map {got}, expected {exp} (ohm {K[A["ohm_u"][i,j]] if A["ohm_u"][i,j]>=0 else None}, clio {K[A["cl_u"][i,j]] if A["cl_u"][i,j]>=0 else None}, src {A["def_src"][i,j]})')
print(f'{len(T) - bad} of {len(T)} checks match')
