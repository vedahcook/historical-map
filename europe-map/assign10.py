# Corrections for the medieval map (1000-1499), run by assign.py with ERA=medieval in the same namespace
# (def_u, def_src, ohm_u, ohm_pri, cl_u, fix(), fix_multi(), rec_mask(), KI, YEARS, YA, x, y, pts, faces, is_land, farea...).
import pickle as _pk
isin10 = lambda *ks: np.isin(def_u, [KI[k] for k in ks])
yr = lambda a, b: (YA >= a) & (YA <= b)
jy = lambda y: YEARS.index(y)

def rec_geom_mask(name, start):
    """Faces inside the OHM record of this name that starts with this date (any year)."""
    m = np.zeros(NF, bool)
    for rid, r in R.items():
        if rid in P and r['t'].get('n') == name and r['t']['s'].startswith(start):
            m |= shapely.contains_xy(P[rid], pts[:, 0], pts[:, 1])
    return m[:, None]

# ---------- the British Isles ----------
IRE = (x < -5.4) & (y > 51.3) & (y < 55.5)
fix('gaelic-ireland', 'GAE', IRE & (def_u == NONE),
    'Neither source draws the Gaelic kingdoms of the north and west of Ireland (Ulster, Connacht and others) in every year. The map shows the parts of Ireland no source assigns as Gaelic Irish kingdoms.',
    [['Gaelic Ireland', 'https://en.wikipedia.org/wiki/Gaelic_Ireland']])
fix('lordship-of-ireland', 'LIR', IRE & yr(1171, 1499) & isin10('ENG'),
    'Cliopatria draws the English crown’s part of Ireland as part of the Kingdom of England. From 1171 it was the Lordship of Ireland, held by the English king but separate from England, so the map shows it on its own.',
    [['Lordship of Ireland', 'https://en.wikipedia.org/wiki/Lordship_of_Ireland']])
# ---------- France ----------
fix('gascony-homage', 'AQU_E', (x > -2.5) & (y < 47.2) & yr(1204, 1336) & isin10('ENG'),
    'Cliopatria draws Gascony as part of the Kingdom of England. Until the Hundred Years’ War began in 1337, the English kings held it as dukes of Aquitaine, vassals of the French king, so the map shows it striped in France’s color. From 1337 the English king claimed the French crown himself.',
    [['Duchy of Aquitaine', 'https://en.wikipedia.org/wiki/Duchy_of_Aquitaine'], ['Treaty of Paris (1259)', 'https://en.wikipedia.org/wiki/Treaty_of_Paris_(1259)']])
fix('gascony-1337', 'ENG', yr(1337, 1499) & isin10('AQU_E'),
    'From 1337 the English king claimed the French crown himself and no longer held Gascony as the French king’s vassal (the Treaty of Brétigny of 1360 gave it to him in full sovereignty), so the map shows English-held land in France as England until it was lost in 1453.',
    [['Hundred Years’ War', 'https://en.wikipedia.org/wiki/Hundred_Years%27_War'], ['Treaty of Brétigny', 'https://en.wikipedia.org/wiki/Treaty_of_Br%C3%A9tigny']])
fix('anjou', 'ANJ', (x < 3.2) & (y > 46.5) & isin10('PRV'),
    'Cliopatria draws the lands of the Angevin princes (the House of Anjou) as one entity, taking in both Anjou and Maine in France and Provence in the Empire. The map shows the French part as the County (later Duchy) of Anjou, a fief of the French crown, and the rest as Provence.',
    [['Anjou', 'https://en.wikipedia.org/wiki/Anjou'], ['House of Valois-Anjou', 'https://en.wikipedia.org/wiki/House_of_Valois-Anjou']])
fix('anjou-lorraine', 'LOR', (x > 4.5) & (y > 47.8) & isin10('PRV'),
    'Cliopatria counts the Duchies of Lorraine and Bar, held by René of Anjou and his heirs, among the lands of the House of Anjou. The map shows them as Lorraine.',
    [['René of Anjou', 'https://en.wikipedia.org/wiki/Ren%C3%A9_of_Anjou']])
fix('provence-1481', 'FRA', (x > 4.5) & (x < 7.8) & (y > 42.9) & (y < 44.6) & yr(1482, 1499) & ((def_u == NONE) | isin10('PRV')),
    'Provence passed to the French crown on the death of its last Angevin count in December 1481.',
    [['County of Provence', 'https://en.wikipedia.org/wiki/County_of_Provence']])
lor = rec_geom_mask('Duchy of Lorraine', '1480')
fix('lorraine', 'LOR', lor & yr(1101, 1479) & isin10('HRE'),
    'Neither source draws the Duchy of Lorraine between 1100 and 1480, so it shows as the Holy Roman Empire. The duchy existed throughout; the map uses OHM’s outline of 1480, which leaves out the Duchy of Bar and the bishoprics of Metz, Toul and Verdun.',
    [['Duchy of Lorraine', 'https://en.wikipedia.org/wiki/Duchy_of_Lorraine']])
# ---------- the Empire ----------
fix('arles', 'ARL', (x > 4.2) & (x < 8.3) & (y > 43.0) & (y < 47.9) & yr(1033, 1378) & isin10('HRE'),
    'OHM draws the Kingdom of Burgundy (Arles) only up to 1032 and from 1190, and between those years shows its land as the Holy Roman Empire. The kingdom passed to the emperors in 1033 but stayed a kingdom of its own within the Empire, so the map shows the land the Empire held directly there as the Kingdom of Arles.',
    [['Kingdom of Arles', 'https://en.wikipedia.org/wiki/Kingdom_of_Arles']])
bav0 = rec_geom_mask('Duchy of Bavaria', '0962')
fix('bavaria-1101', 'BAV', bav0 & yr(1101, 1179) & isin10('HRE'),
    'OHM’s record of the Duchy of Bavaria stops in 1100 and Cliopatria’s starts in 1260, so between them it shows as the Holy Roman Empire. The duchy existed throughout, under the Welf dukes and from 1180 the Wittelsbachs. For 1101-79 the map uses OHM’s outline of 1100 (Austria appears as its own duchy from 1156).',
    [['Duchy of Bavaria', 'https://en.wikipedia.org/wiki/Duchy_of_Bavaria']])
bav1 = np.zeros(NF, bool)
for i_, p_ in enumerate(F['cl']):
    if p_['Name'] == 'Duchy of Bavaria' and p_['FromYear'] == 1260: bav1[F['in_cl'][i_]] = True
fix('bavaria-1180', 'BAV', bav1[:, None] & yr(1180, 1259) & isin10('HRE'),
    'Neither source draws the Duchy of Bavaria between 1180, when it passed to the Wittelsbachs without Styria, and 1260. The map uses Cliopatria’s outline of 1260 for those years.',
    [['Duchy of Bavaria', 'https://en.wikipedia.org/wiki/Duchy_of_Bavaria'], ['House of Wittelsbach', 'https://en.wikipedia.org/wiki/House_of_Wittelsbach']])
fix('wittelsbach-brandenburg', 'BRA', (y > 51.0) & yr(1323, 1374) & isin10('BAV'),
    'Cliopatria draws the Margraviate of Brandenburg as part of Bavaria while the Wittelsbach dukes of Bavaria also held it (1323-73). It stayed a separate state, so the map shows it as Brandenburg.',
    [['Margraviate of Brandenburg', 'https://en.wikipedia.org/wiki/Margraviate_of_Brandenburg']])
fix('franconian-hohenzollern', 'HRE', (y < 50.6) & yr(1415, 1499) & isin10('BRA'),
    'Cliopatria counts the Hohenzollerns’ Franconian lands (Ansbach and Kulmbach-Bayreuth) as part of Brandenburg. They were separate principalities of the Empire, so the map shows them as the Empire’s smaller states.',
    [['Principality of Ansbach', 'https://en.wikipedia.org/wiki/Principality_of_Ansbach']])
aut = rec_geom_mask('Duchy of Austria', '1254')
fix('austria-1156', 'AUT', aut & yr(1156, 1253) & isin10('HRE', 'BAV'),
    'OHM’s record of the Duchy of Austria starts in 1254, and Cliopatria does not draw it. Austria became a duchy separate from Bavaria in 1156 (the Privilegium Minus); for 1156-1253 the map uses OHM’s outline of 1254.',
    [['Privilegium Minus', 'https://en.wikipedia.org/wiki/Privilegium_Minus'], ['Duchy of Austria', 'https://en.wikipedia.org/wiki/Duchy_of_Austria']])
fix('habsburg-netherlands', 'HNL', (x < 7.2) & (y > 49.3) & yr(1477, 1499) & isin10('AUT'),
    'Cliopatria counts the Burgundian Netherlands, inherited by Mary of Burgundy and her husband Maximilian of Habsburg in 1477, among the lands of the House of Habsburg. The map shows them as the Habsburg Netherlands, as in the 1500s.',
    [['Burgundian Netherlands', 'https://en.wikipedia.org/wiki/Burgundian_Netherlands']])
j49 = jy(1449)
for u0 in ('HUK', 'BOK'):
    fix('ladislaus-' + u0, u0, yr(1450, 1458) & isin10('AUT') & (def_u[:, [j49]] == KI[u0]),
        'Cliopatria draws Austria, Hungary and Bohemia as one Habsburg realm while the young Ladislaus the Posthumous was king of all three (to 1457). They were separate kingdoms, so the map keeps Hungary and Bohemia as their own.',
        [['Ladislaus the Posthumous', 'https://en.wikipedia.org/wiki/Ladislaus_the_Posthumous']])
# ---------- Italy ----------
SICILY = (x > 12.3) & (x < 15.7) & (y > 36.6) & (y < 38.35)
MAINLAND_S = (x > 13.0) & (y > 37.9) & (y < 42.3) & ~SICILY
fix('naples-1282', 'NAP', ~SICILY & (y > 37.9) & (x > 7.0) & yr(1282, 1302) & isin10('SIC'),
    'OHM’s Kingdom of Naples starts with the Peace of Caltabellotta (1302). The mainland had been a separate kingdom under the Angevin kings since the Sicilian Vespers of 1282, when Sicily itself went to the house of Aragon; the Angevins went on calling it the Kingdom of Sicily.',
    [['Sicilian Vespers', 'https://en.wikipedia.org/wiki/Sicilian_Vespers'], ['Kingdom of Naples', 'https://en.wikipedia.org/wiki/Kingdom_of_Naples']])
fix('naples-1442', 'NAP', MAINLAND_S & yr(1442, 1458) & isin10('ARA'),
    'OHM counts the Kingdom of Naples as part of the Crown of Aragon while Alfonso V ruled both (1442-58). Naples stayed a separate kingdom, and went to Alfonso’s son Ferdinand on his death.',
    [['Alfonso V of Aragon', 'https://en.wikipedia.org/wiki/Alfonso_V_of_Aragon']])
fix('norman-apulia', 'NRM', (x > 14.5) & (x < 18.6) & (y > 37.9) & (y < 42.0) & ~SICILY & yr(1072, 1129) & isin10('BYZ'),
    'The Normans took the last Byzantine city in southern Italy, Bari, in April 1071. The sources keep parts of Apulia and Calabria Byzantine after that.',
    [['Siege of Bari', 'https://en.wikipedia.org/wiki/Siege_of_Bari']])
rag = np.zeros(NF, bool)
for p_, g_ in _pk.load(open('../early/clio.pkl', 'rb')):
    if p_['Name'] == 'Republic of Ragusa': rag |= shapely.contains_xy(g_, pts[:, 0], pts[:, 1])
fix('ragusa', 'RAG', rag[:, None] & yr(1358, 1499),
    'Neither source draws the Republic of Ragusa (Dubrovnik) in the right place before 1429. It was independent of Venice from the Treaty of Zadar (1358), under the nominal overlordship of Hungary; the map uses Cliopatria’s outline of 1429.',
    [['Republic of Ragusa', 'https://en.wikipedia.org/wiki/Republic_of_Ragusa'], ['Treaty of Zadar', 'https://en.wikipedia.org/wiki/Treaty_of_Zadar']])
fix('athens-acciaioli', 'ATH', (x > 19.0) & yr(1385, 1457) & isin10('TUS'),
    'Cliopatria counts the Duchy of Athens as part of the Republic of Florence while the Florentine Acciaioli family ruled it (1388-1458). It was a separate duchy, so the map shows it as Athens.',
    [['Duchy of Athens', 'https://en.wikipedia.org/wiki/Duchy_of_Athens']])
fix('athens-1458', 'OTT', (x > 19.0) & yr(1458, 1499) & isin10('TUS'),
    'Cliopatria keeps Athens Florentine after 1458. The Ottomans took Athens in 1456-58 and the rest of the duchy by 1460.',
    [['Duchy of Athens', 'https://en.wikipedia.org/wiki/Duchy_of_Athens']])
# ---------- Iberia ----------
fix('lisbon-1094', 'ALV', (x < -8.3) & (y > 38.4) & (y < 39.4) & yr(1095, 1146) & isin10('LEO', 'POR_C'),
    'OHM keeps Lisbon and Santarém Leonese after 1093. The Almoravids took them back in 1094-95 and held Lisbon until the siege of 1147.',
    [['Siege of Lisbon', 'https://en.wikipedia.org/wiki/Siege_of_Lisbon']])
# ---------- Byzantium and the east ----------
MOREA = (x > 21.0) & (x < 23.4) & (y > 36.3) & (y < 38.3)
fix('byzantium-1453', 'OTT', ((yr(1454, 1499) & ~MOREA) | yr(1460, 1499)) & isin10('BYZ'),
    'Cliopatria keeps a Byzantine state until 1474. Constantinople fell to the Ottomans on May 29, 1453; the last Byzantine territory, the Despotate of the Morea, fell in 1460.',
    [['Fall of Constantinople', 'https://en.wikipedia.org/wiki/Fall_of_Constantinople'], ['Despotate of the Morea', 'https://en.wikipedia.org/wiki/Despotate_of_the_Morea']])
fix('vladimir', 'VLS', (y > 55.8) & yr(1100, 1240) & isin10('RYA_I'),
    'Cliopatria’s outline of the Principality of Ryazan reaches north of the Oka to Vladimir. Vladimir was the capital of the Principality of Vladimir-Suzdal.',
    [['Vladimir-Suzdal', 'https://en.wikipedia.org/wiki/Vladimir-Suzdal']])
fix('lithuania-1450', 'LIT', yr(1450, 1499) & isin10('PLK') & (def_u[:, [j49]] == KI['LIT']) & (ohm_u == NONE),
    'Cliopatria draws Poland and Lithuania as one Jagiellonian realm from 1450, when Casimir IV was both king of Poland and grand duke of Lithuania. The two stayed separate states until the Union of Lublin (1569), so the map keeps Lithuania as its own, with its extent of 1449.',
    [['Casimir IV Jagiellon', 'https://en.wikipedia.org/wiki/Casimir_IV_Jagiellon']])

# ---------- coastal slivers ----------
# Cliopatria's coastlines are coarse, so thin strips of coast between its outline and the map's coastline have no holder,
# or only one of OHM's coarse records (priority 1). Each such piece under 1,500 km2 takes the holder it shares the most
# border with, if holders make up at least half of its land border.
COARSE = {KI[k] for k in ('BYZ', 'OTT', 'LAT', 'NIC', 'THL', 'EPI', 'ACH', 'ABB', 'FAT', 'SEL', 'ZIR', 'ILK', 'KHW', 'MNG', 'GOH', 'TAI', 'TRE', 'SRM', 'FRA', 'HRE', 'ARL')}
small = is_land & (farea < 1500)
cand_all = small[:, None] & ((def_u == NONE) | ((def_src == 0) & (ohm_pri == 1) & np.isin(def_u, list(COARSE)) & (cl_u == NONE)))
tree10 = shapely.STRtree(faces)
nbr = {}
for i in np.where(small)[0]:
    fb = faces[i].boundary
    near = tree10.query(faces[i], predicate='intersects')
    near = near[(near != i) & is_land[near]]
    if not len(near): continue
    L = shapely.length(shapely.intersection(fb, shapely.boundary(np.array([faces[k] for k in near], dtype=object))))
    keep = L > 0
    nbr[i] = (near[keep], L[keep])
fill = np.full((NF, NY), NONE, np.int16)
cache = {}
for j in range(NY):
    col, cand = def_u[:, j].copy(), cand_all[:, j].copy()
    key = hash(col.tobytes()) ^ hash(cand.tobytes())
    if key in cache: fill[:, j] = cache[key]; continue
    out = np.full(NF, NONE, np.int16)
    for _ in range(3):
        changed = False
        for i in np.where(cand & (out == NONE))[0]:
            if i not in nbr: continue
            near, L = nbr[i]
            u = np.where(cand[near] & (out[near] == NONE), NONE, np.where(out[near] != NONE, out[near], col[near]))
            held = u != NONE
            if L[held].sum() < 0.5 * L.sum() or not held.any(): continue
            tot = {}
            for uu, ll in zip(u[held].tolist(), L[held].tolist()): tot[uu] = tot.get(uu, 0) + ll
            out[i] = max(tot, key=tot.get); changed = True
        if not changed: break
    fill[:, j] = cache[key] = out
fill[fill == def_u] = NONE
fix_multi('coast', fill,
    'Cliopatria’s coastlines are drawn roughly, so thin strips of coast fall outside its outlines. Each strip under 1,500 km² goes to the state it borders most.',
    [['Cliopatria (Seshat)', 'https://github.com/Seshat-Global-History-Databank/cliopatria']])

print('corrections', [(f['id'], f['n']) for f in FIX])
