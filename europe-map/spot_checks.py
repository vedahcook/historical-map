"""Spot checks of the final map against well-documented facts."""
import pickle, shapely
A = pickle.load(open('assign.pkl', 'rb')); F = pickle.load(open('faces.pkl', 'rb'))
K = A['KEYS']; Y = A['YEARS']; tree = shapely.STRtree(F['faces'])
C = {'Ulcinj': (19.21, 41.93), 'Arta': (20.99, 39.16), 'Nis': (21.9, 43.32), 'Izmail': (28.83, 45.35), 'Heraklion': (25.13, 35.33), 'Podgorica': (19.26, 42.44), 'Kars': (43.1, 40.6), 'Batumi': (41.64, 41.64), 'Chambery': (5.92, 45.56), 'Schleswig': (9.57, 54.52), 'Tromso': (18.96, 69.65), 'Reykjavik': (-21.9, 64.14), 'Paris': (2.35, 48.86), 'Amsterdam': (4.9, 52.37), 'Hamburg': (9.99, 53.55), 'Venice': (12.33, 45.44), 'Rome': (12.5, 41.9),
     'Milan': (9.19, 45.46), 'Nice': (7.27, 43.7), 'Strasbourg': (7.75, 48.58), 'Brussels': (4.35, 50.85), 'Warsaw': (21.01, 52.23),
     'Krakow': (19.94, 50.06), 'Helsinki': (24.94, 60.17), 'Oslo': (10.75, 59.91), 'Belgrade': (20.46, 44.82), 'Bucharest': (26.1, 44.43),
     'Sofia': (23.32, 42.7), 'Plovdiv': (24.75, 42.14), 'Athens': (23.73, 37.98), 'Larissa': (22.42, 39.64), 'Sarajevo': (18.41, 43.86),
     'Kiel': (10.13, 54.32), 'Frankfurt': (8.68, 50.11), 'Hanover': (9.73, 52.37), 'Dresden': (13.74, 51.05), 'Munich': (11.58, 48.14),
     'Turin': (7.69, 45.07), 'Geneva': (6.14, 46.2), 'Chisinau': (28.86, 47.01), 'Tbilisi': (44.79, 41.72), 'Ljubljana': (14.51, 46.06),
     'Dubrovnik': (18.09, 42.65), 'Corfu': (19.92, 39.62), 'Valletta': (14.51, 35.9), 'Heligoland': (7.89, 54.18), 'Nicosia': (33.36, 35.17),
     'Tunis': (10.18, 36.8), 'Algiers': (3.06, 36.75), 'Lisbon': (-9.14, 38.72), 'Madrid': (-3.7, 40.42), 'Vienna': (16.37, 48.21),
     'Budapest': (19.04, 47.5), 'Prague': (14.42, 50.09), 'Stockholm': (18.07, 59.33), 'Copenhagen': (12.57, 55.68), 'Dublin': (-6.26, 53.35),
     'Naples': (14.27, 40.85), 'Palermo': (13.36, 38.12), 'Florence': (11.25, 43.77), 'Istanbul': (28.97, 41.01), 'Moscow': (37.62, 55.76),
     'Riga': (24.1, 56.95), 'Berlin': (13.4, 52.52), 'Stuttgart': (9.18, 48.78), 'Metz': (6.18, 49.12), 'Luxembourg': (6.13, 49.61)}
T2 = [('Ulcinj', 1879, 'OTT'), ('Ulcinj', 1881, 'MNE'), ('Arta', 1885, 'GRE'), ('Nis', 1877, 'OTT'), ('Nis', 1879, 'SRB_I'), ('Izmail', 1860, 'ROM_V'), ('Izmail', 1880, 'RUS'), ('Heraklion', 1897, 'OTT'), ('Heraklion', 1899, 'CRT'), ('Podgorica', 1879, 'MNE'), ('Kars', 1880, 'RUS'), ('Batumi', 1880, 'RUS'), ('Nice', 1861, 'FRA'), ('Chambery', 1861, 'FRA'), ('Chambery', 1859, 'SAR'), ('Schleswig', 1865, 'SHC'), ('Tromso', 1850, 'NOR'), ('Reykjavik', 1850, 'DEN')]
T = [('Paris', 1810, 'FRA'), ('Amsterdam', 1807, 'NLD'), ('Amsterdam', 1811, 'FRA'), ('Amsterdam', 1816, 'NLD'), ('Hamburg', 1812, 'FRA'),
     ('Hamburg', 1816, 'HAM'), ('Venice', 1810, 'NIT'), ('Venice', 1820, 'AUT'), ('Venice', 1867, 'ITA'), ('Rome', 1869, 'PAP'), ('Rome', 1871, 'ITA'),
     ('Rome', 1810, 'FRA'), ('Milan', 1858, 'AUT'), ('Milan', 1860, 'SAR'), ('Nice', 1859, 'SAR'), ('Nice', 1861, 'FRA'), ('Strasbourg', 1870, 'FRA'),
     ('Strasbourg', 1872, 'GER'), ('Metz', 1872, 'GER'), ('Brussels', 1829, 'NLD'), ('Brussels', 1832, 'BEL'), ('Brussels', 1800, 'FRA'),
     ('Warsaw', 1808, 'WAR'), ('Warsaw', 1820, 'POL'), ('Warsaw', 1870, 'RUS'), ('Warsaw', 1800, 'PRU'), ('Krakow', 1820, 'KRA'), ('Krakow', 1850, 'AUT'),
     ('Helsinki', 1805, 'SWE'), ('Helsinki', 1810, 'FIN'), ('Oslo', 1810, 'DEN'), ('Oslo', 1820, 'NOR'), ('Oslo', 1906, None),
     ('Belgrade', 1840, 'SRB'), ('Belgrade', 1880, 'SRB_I'), ('Bucharest', 1850, 'WAL'), ('Bucharest', 1870, 'ROM_V'), ('Bucharest', 1885, 'ROM'),
     ('Sofia', 1880, 'BUL'), ('Plovdiv', 1880, 'ERU'), ('Plovdiv', 1890, 'BUL'), ('Athens', 1835, 'GRE'), ('Athens', 1825, 'OTT'),
     ('Larissa', 1875, 'OTT'), ('Larissa', 1885, 'GRE'), ('Sarajevo', 1890, 'AUT_OCC'), ('Sarajevo', 1870, 'OTT'), ('Kiel', 1860, 'DEN'),
     ('Kiel', 1865, 'SHC'), ('Kiel', 1868, 'GER'), ('Frankfurt', 1860, 'FRK'), ('Frankfurt', 1868, 'GER'), ('Hanover', 1865, 'HAN'),
     ('Hanover', 1868, 'GER'), ('Dresden', 1850, 'SAX'), ('Dresden', 1868, 'GER'), ('Munich', 1868, 'BAV'), ('Munich', 1872, 'GER'),
     ('Munich', 1810, 'BAV'), ('Stuttgart', 1808, 'WUR'), ('Stuttgart', 1850, 'WUR'), ('Turin', 1805, 'FRA'), ('Turin', 1820, 'SAR'),
     ('Geneva', 1805, 'FRA'), ('Geneva', 1816, 'SUI'), ('Chisinau', 1811, 'MOL'), ('Chisinau', 1813, 'RUS'), ('Tbilisi', 1800, 'GEO'),
     ('Tbilisi', 1805, 'RUS'), ('Ljubljana', 1810, 'FRA'), ('Ljubljana', 1816, 'AUT'), ('Dubrovnik', 1805, 'RAG'), ('Dubrovnik', 1820, 'AUT'),
     ('Corfu', 1812, 'FRA'), ('Corfu', 1820, 'ION'), ('Corfu', 1870, 'GRE'), ('Valletta', 1805, 'GBR'), ('Heligoland', 1820, 'GBR'),
     ('Heligoland', 1895, 'GER'), ('Nicosia', 1880, 'CYP'), ('Tunis', 1885, 'TUN_F'), ('Algiers', 1835, 'FRA'), ('Algiers', 1825, 'ALG'),
     ('Lisbon', 1850, 'POR'), ('Madrid', 1850, 'ESP'), ('Vienna', 1810, 'AUT'), ('Vienna', 1880, 'AUT'), ('Budapest', 1850, 'AUT'),
     ('Prague', 1850, 'AUT'), ('Stockholm', 1850, 'SWE'), ('Copenhagen', 1850, 'DEN'), ('Dublin', 1800, 'IRL'), ('Dublin', 1850, 'GBR'),
     ('Naples', 1810, 'NAP'), ('Palermo', 1810, 'SIC'), ('Palermo', 1820, 'NAP'), ('Palermo', 1861, 'ITA'), ('Florence', 1850, 'TUS'),
     ('Florence', 1862, 'ITA'), ('Florence', 1808, 'FRA'), ('Istanbul', 1850, 'OTT'), ('Moscow', 1850, 'RUS'), ('Riga', 1850, 'RUS'),
     ('Berlin', 1850, 'PRU'), ('Berlin', 1880, 'GER'), ('Luxembourg', 1880, 'LUX')]
bad = 0
T = T + T2
for city, y, exp in T:
    if y > 1900: continue
    lon, lat = C[city]
    i = tree.query(shapely.Point(lon, lat), predicate='within')
    if not len(i) or not F['land'][int(i[0])]:
        land_idx = [k for k in tree.query(shapely.Point(lon, lat).buffer(0.1)) if F['land'][k]]
        i = [min(land_idx, key=lambda k: F['faces'][k].distance(shapely.Point(lon, lat)))] if land_idx else []
    if not len(i): print('no face', city); bad += 1; continue
    i = int(i[0]); j = Y.index(y); u = A['def_u'][i, j]; got = K[u] if u >= 0 else None
    if got != exp: bad += 1; print(f'MISMATCH {city} {y}: map {got}, expected {exp} (ohm {K[A["ohm_u"][i,j]] if A["ohm_u"][i,j]>=0 else None}, src {A["def_src"][i,j]})')
print(f'{len([t for t in T if t[1] <= 1900]) - bad} of {len([t for t in T if t[1] <= 1900])} checks match')
