"""Which country (display unit) each source record belongs to.

A unit is what the map colors: one country, or a self-governing territory under an
overlord (drawn hatched). Records from OHM, CShapes-Europe and Cliopatria are mapped
to the same unit keys so they can be compared.

OHM roles (priority decides which record wins where records overlap):
  3  self-governing under an overlord (Serbia before 1878, Finland, Congress Poland ...)
  2  a country, or a piece of one (Austrian crown lands, Prussian provinces ...)
  1  an umbrella (Holy Roman Empire and its circles, Sweden-Norway union record)
"""
import re

# key: (display name, overlord key or None, color family)
# Units sharing a color family never exist at the same time (e.g. Prussia -> Germany).
UNITS = {
    'FRA': ('France', None, 'FRA'), 'GBR': ('United Kingdom', None, 'GBR'), 'IRL': ('Kingdom of Ireland', None, 'IRL'),
    'ESP': ('Spain', None, 'ESP'), 'POR': ('Portugal', None, 'POR'), 'AUT': ('Austria', None, 'AUT'),
    'PRU': ('Prussia', None, 'PRU'), 'GER': ('Germany', None, 'PRU'), 'RUS': ('Russia', None, 'RUS'),
    'OTT': ('Ottoman Empire', None, 'OTT'), 'SWE': ('Sweden', None, 'SWE'), 'NOR': ('Norway', None, 'NOR'),
    'DEN': ('Denmark', None, 'DEN'), 'NLD': ('Netherlands', None, 'NLD'), 'BEL': ('Belgium', None, 'BEL'),
    'LUX': ('Luxembourg', None, 'LUX'), 'SUI': ('Switzerland', None, 'SUI'), 'SAR': ('Sardinia', None, 'SAR'),
    'ITA': ('Italy', None, 'SAR'), 'NAP': ('Naples', None, 'NAP'), 'SIC': ('Sicily', None, 'SIC'),
    'PAP': ('Papal States', None, 'PAP'), 'TUS': ('Tuscany', None, 'TUS'), 'PAR': ('Parma', None, 'PAR'),
    'MOD': ('Modena', None, 'MOD'), 'LUC': ('Lucca', None, 'LUC'), 'MAS': ('Massa and Carrara', None, 'MAS'),
    'GEN': ('Genoa', None, 'GEN'), 'NIT': ('Napoleonic Italy', None, 'NIT'), 'GRE': ('Greece', None, 'GRE'),
    'SRB': ('Serbia', 'OTT', 'SRB'), 'MNE': ('Montenegro', None, 'MNE'), 'WAL': ('Wallachia', 'OTT', 'ROM'),
    'MOL': ('Moldavia', 'OTT', 'MOL'), 'ROM': ('Romania', None, 'ROM'), 'BUL': ('Bulgaria', 'OTT', 'BUL'),
    'ERU': ('Eastern Rumelia', 'OTT', 'ERU'), 'ION': ('Ionian Islands', 'GBR', 'ION'), 'ION_S': ('Septinsular Republic', 'OTT', 'ION'), 'CRT': ('Crete', 'OTT', 'CRT'),
    'CYP': ('Cyprus (British-run)', 'OTT', 'GBR'), 'BAV': ('Bavaria', None, 'BAV'), 'WUR': ('Württemberg', None, 'WUR'),
    'BAD': ('Baden', None, 'BAD'), 'SAX': ('Saxony', None, 'SAX'), 'HAN': ('Hanover', None, 'HAN'),
    'HKA': ('Hesse-Kassel', None, 'HKA'), 'HDA': ('Hesse-Darmstadt', None, 'HDA'), 'NAS': ('Nassau', None, 'NAS'),
    'BRU': ('Brunswick', None, 'BRU'), 'OLD': ('Oldenburg', None, 'OLD'), 'MKS': ('Mecklenburg-Schwerin', None, 'MKS'),
    'MKST': ('Mecklenburg-Strelitz', None, 'MKST'), 'HAM': ('Hamburg', None, 'HAM'), 'BRE': ('Bremen', None, 'BRE'),
    'LUB': ('Lübeck', None, 'LUB'), 'FRK': ('Frankfurt', None, 'FRK'), 'KRA': ('Kraków', None, 'KRA'),
    'DAN': ('Danzig', None, 'DAN'), 'WAR': ('Duchy of Warsaw', None, 'WAR'), 'POL': ('Kingdom of Poland', 'RUS', 'POL'),
    'FIN': ('Finland', 'RUS', 'FIN'), 'WES': ('Westphalia', None, 'WES'), 'BERG': ('Berg', None, 'BERG'),
    'ANH': ('Anhalt', None, 'ANH'), 'LIP': ('Lippe', None, 'LIP'), 'SCH': ('Schaumburg-Lippe', None, 'SCH'),
    'WALD': ('Waldeck', None, 'WALD'), 'REU': ('Reuss', None, 'REU'), 'SWB': ('Schwarzburg', None, 'SWB'),
    'SXW': ('Saxe-Weimar', None, 'SXW'), 'SXA': ('Saxe-Altenburg', None, 'SXA'), 'SXC': ('Saxe-Coburg', None, 'SXC'),
    'SXM': ('Saxe-Meiningen', None, 'SXM'), 'SXO': ('Other Saxon duchies', None, 'SXO'), 'HOH': ('Hohenzollern', None, 'HOH'),
    'HHO': ('Hesse-Homburg', None, 'HHO'), 'LIE': ('Liechtenstein', None, 'LIE'), 'ISE': ('Isenburg', None, 'ISE'),
    'LEY': ('Leyen', None, 'LEY'), 'ASC': ('Aschaffenburg / Frankfurt', None, 'ASC'), 'REG': ('Regensburg', None, 'REG'),
    'ARE': ('Arenberg', None, 'ARE'), 'NEU': ('Neuchâtel', None, 'NEU'), 'VAL': ('Valais', None, 'VAL'),
    'RAG': ('Ragusa', None, 'RAG'), 'SMR': ('San Marino', None, 'SMR'), 'AND': ('Andorra', None, 'AND'),
    'MON': ('Monaco', None, 'MON'), 'GAR': ("Garibaldi's Sicily", None, 'GAR'), 'UPC': ('Central Italy', None, 'UPC'),
    'SMK': ('Republic of San Marco', None, 'SMK'), 'MIL': ('Provisional Milan', None, 'MIL'), 'HRE': ('Holy Roman Empire', None, 'HRE'),
    'SHC': ('Schleswig-Holstein', None, 'SHC'), 'MOR': ('Morocco', None, 'MOR'), 'ALG': ('Algiers', 'OTT', 'ALG'),
    'TUN': ('Tunis', 'OTT', 'TUN'), 'PER': ('Persia', None, 'PER'), 'GEO': ('Georgia', None, 'GEO'),
    'CAU': ('Caucasus peoples', None, 'CAU'), 'EGY': ('Egypt', 'OTT', 'EGY'), 'SAL': ('Salzburg', None, 'SAL'),
    'WRZ': ('Würzburg', None, 'WRZ'), 'BEN': ('Benevento', None, 'BEN'), 'PON': ('Pontecorvo', None, 'PON'),
    'ELB': ('Elba', None, 'ELB'), 'PIO': ('Piombino', None, 'PIO'), 'COS': ('Cospaia', None, 'COS'),
    'MRS': ('Neutral Moresnet', None, 'MRS'), 'MLT': ('Malta', None, 'MLT'), 'RHC': ('Confederation of the Rhine', None, 'RHC'),
}

# ---------- OHM ----------
# (regex on the English name, level or None for any, unit, priority, valid-from year, valid-to year)
# A role only counts for July-1 samples in [from, to].
_R = [
    # umbrellas
    (r'^Holy Roman Empire$', None, 'HRE', 1), (r'Circle$', '3', 'HRE', 1), (r'^Sweden–Norway$', None, 'SWE', 1),
    (r'^Austrian Circle$', '3', 'AUT', 2), (r'^Burgundian Circle$', '3', None, 0),
    # self-governing under an overlord
    (r'^Principality of Serbia$', '3', 'SRB', 3), (r'^Principality of Serbia$', '2', 'SRB', 3, 1867, 1878),
    (r'^Principality of Serbia$', '2', 'SRB_I', 2, 1879, 9999),
    (r'^Principality of Wallachia$', '3', 'WAL', 3), (r'^Principality of Moldavia$', '3', 'MOL', 3),
    (r'^United Romanian Principalities$', '3', 'ROM_V', 3), (r'^Bulgaria$', '3', 'BUL', 3), (r'^Eastern Rumelia$', '4', 'ERU', 3),
    (r'^Grand Duchy of Finland$', '3', 'FIN', 3), (r'^Kingdom of Poland$', '2', 'POL', 3), (r'^Cretan State$', None, 'CRT', 3),
    (r'^Septinsular Republic$', None, 'ION_S', 3), (r'^United States of the Ionian Islands$', None, 'ION', 3),
    (r'^Cyprus Protectorate$', None, 'CYP', 3), (r'^French protectorate of Tunisia$', None, 'TUN_F', 3),
    (r'^Norway$', '3', 'NOR', 2), (r'^Sweden$', '3', 'SWE', 2),
    # countries
    (r'^(French Republic.*|French Empire|Kingdom of France|Second French Empire|French Alger|French Algeria)$', None, 'FRA', 2),
    (r'^French Malta$', None, 'FRA', 2),
    (r'^(Kingdom of Great Britain|United Kingdom of Great Britain and Ireland|Gibraltar|Guernsey|Jersey|Isle of Man|Heligoland|British Protectorate of Malta|Crown Colony of Malta)$', None, 'GBR', 2),
    (r'^Kingdom of Ireland$', None, 'IRL', 2), (r'^Spain$', None, 'ESP', 2), (r'^Kingdom of Portugal$', None, 'POR', 2),
    (r'^(Austrian Empire|Austria-Hungary)$', '2', 'AUT', 2),
    (r'^(Cisleithania|Transleithania|Kingdom of Hungary|Kingdom of Croatia|Kingdom of Slavonia|Galicia and Lodomeria|West Galicia|Kingdom of Illyria|Kingdom of Lombardy-Venetia|Military Frontier|Voivodeship of Serbia and Banat of Temes|Lands of the Bohemian Crown)$', '3', 'AUT', 2),
    (r'^Kingdom of Prussia$', '2', 'PRU', 2), (r'^Kingdom of Prussia$', '3', 'GER', 2),
    (r'^(North German Confederation|German Reich)$', None, 'GER', 2),
    (r'^Russian Empire$', None, 'RUS', 2), (r'^Ottoman Empire$', None, 'OTT', 2), (r'^Sweden$', '2', 'SWE', 2),
    (r'^Norway$', '2', 'NOR', 2), (r'^(Denmark|Denmark–Norway)$', None, 'DEN', 2), (r'^(Kingdom of Denmark|Kingdom of Norway)$', '3', 'DEN', 2),
    (r'^(Batavian Commonwealth|Batavian Republic|Kingdom of Holland|Kingdom of the Netherlands|Sovereign Principality of the United Netherlands|United Netherlands)$', None, 'NLD', 2),
    (r'^(Netherlands|Belgium|Duchy of Limburg)$', '3', 'NLD', 2), (r'^Duchy of Limburg$', '2', 'NLD', 2),
    (r'^Belgium$', '2', 'BEL', 2), (r'^(Duchy of Luxembourg|Grand Duchy of Luxembourg|Luxembourg)$', None, 'LUX', 2),
    (r'^(Helvetic Republic|Swiss Confederation|Switzerland)$', None, 'SUI', 2), (r'^Valais Republic$', None, 'VAL', 2),
    (r'^Kingdom of Sardinia$', None, 'SAR', 2), (r'^Italy$', None, 'ITA', 2),
    (r'^(Kingdom of Naples|Kingdom of the Two Sicilies|Parthenopean Republic.*)$', None, 'NAP', 2), (r'^Kingdom of Sicily$', None, 'SIC', 2),
    (r'^(Papal States|Roman Republic)$', None, 'PAP', 2), (r'^Principality of Benevento \(Papal\)$', None, 'PAP', 2),
    (r'^Duchy of Pontecorvo$', None, 'PAP', 2),
    (r'^Principality of Benevento \(Napoleonic\)$', None, 'BEN', 2), (r'^(Principality|Republic) of Pontecorvo.*$', None, 'PON', 2),
    (r'^(Grand Duchy of Tuscany|Kingdom of Etruria)$', None, 'TUS', 2), (r'^Duchy of Parma and Piacenza$', None, 'PAR', 2),
    (r'^Duchy of Modena and Reggio$', None, 'MOD', 2), (r'^(Duchy of Lucca|Principality of Lucca and Piombino|Republic of Lucca)$', None, 'LUC', 2),
    (r'^Duchy of Massa and Carrara$', None, 'MAS', 2), (r'^(Ligurian Republic|Republic of Genoa)$', None, 'GEN', 2),
    (r'^(Cisalpine Republic|Italian Republic|Kingdom of Italy)$', None, 'NIT', 2), (r'^Principality of Piombino$', None, 'PIO', 2),
    (r'^Principality of Elba$', None, 'ELB', 2), (r'^Dictatorship of Garibaldi$', None, 'GAR', 2),
    (r'^United Provinces of Central Italy$', None, 'UPC', 2), (r'^Republic of San Marco$', None, 'SMK', 2),
    (r'^Provisional government of Milan$', None, 'MIL', 2), (r'^San Marino$', None, 'SMR', 2), (r'^Republic of Cospaia$', None, 'COS', 2),
    (r'^Kingdom of Greece$', None, 'GRE', 2), (r'^Kingdom of Serbia$', None, 'SRB_I', 2),
    (r'^(Prince-Bishopric of Montenegro|Principality of Montenegro)$', None, 'MNE', 2),
    (r'^Kingdom of Romania$', None, 'ROM', 2), (r'^United Romanian Principalities$', '2', 'ROM', 2),
    (r'^Republic of Ragusa$', None, 'RAG', 2), (r'^Knights Hospitaller$', None, 'MLT', 2),
    (r'^Kingdom of Bavaria$', '2', 'BAV', 2), (r'^Württemberg$', '2', 'WUR', 2), (r'^Baden$', '2', 'BAD', 2),
    (r'^(Electorate of Saxony|Kingdom of Saxony)$', '2', 'SAX', 2), (r'^Hanover$', '2', 'HAN', 2),
    (r'^Electorate of Hesse$', '2', 'HKA', 2), (r'^(Grand Duchy of Hesse|Hesse)$', '2', 'HDA', 2), (r'^Nassau$', None, 'NAS', 2),
    (r'^Brunswick$', '2', 'BRU', 2), (r'^(Duchy of Oldenburg|Oldenburg)$', '2', 'OLD', 2),
    (r'^(Duchy|Grand Duchy) of Mecklenburg-Schwerin$', '2', 'MKS', 2), (r'^(Duchy|Grand Duchy) of Mecklenburg-Strelitz$', '2', 'MKST', 2),
    (r'^Free and Hanseatic City of Hamburg$', '2', 'HAM', 2), (r'^Bremen$', '2', 'BRE', 2),
    (r'^Free and Hanseatic City of Lübeck$', '2', 'LUB', 2), (r'^Frankfur', None, 'FRK', 2), (r'^Free City of Cracow$', None, 'KRA', 2),
    (r'^Free City of Danzig$', None, 'DAN', 2), (r'^Duchy of Warsaw$', None, 'WAR', 2), (r'^Kingdom of Westphalia$', None, 'WES', 2),
    (r'^Grand Duchy of Berg$', None, 'BERG', 2), (r'^Duchy of Anhalt', '2', 'ANH', 2), (r'^Principality of Lippe$', None, 'LIP', 2),
    (r'^Schaumburg-Lippe$', '2', 'SCH', 2), (r'^(Waldeck|Waldeck-Pyrmont|Pyrmont)$', '2', 'WALD', 2),
    (r'^Principality of Reuss', '2', 'REU', 2), (r'^Principality of Schwarzburg', '2', 'SWB', 2),
    (r'^Saxe-Weimar-Eisenach$', '2', 'SXW', 2), (r'^Saxe-Altenburg$', '2', 'SXA', 2), (r'^Saxe-Coburg and Gotha$', '2', 'SXC', 2),
    (r'^Saxe-Meiningen$', '2', 'SXM', 2), (r'^Hohenzollern-', '2', 'HOH', 2), (r'^Hesse-Homburg$', None, 'HHO', 2),
    (r'^Liechtenstein$', '2', 'LIE', 2), (r'^Principality Isenburg$', None, 'ISE', 2), (r'^Principality of Leyen$', None, 'LEY', 2),
    (r'^Principality of Aschaffenburg$', '2', 'ASC', 2), (r'^Principality of Regensburg$', '2', 'REG', 2),
    (r'^Duchy of Arenberg-Meppen$', '2', 'ARE', 2), (r'^Principality of Neuchâtel$', '2', 'NEU', 2),
    (r'^Andorra$', None, 'AND', 2), (r'^Monaco$', None, 'MON', 2), (r'^Neutral Moresnet$', None, 'MRS', 2),
    (r'^(Alawi Sultanate)$', None, 'MOR', 2), (r'^Captaincy General of the Azores$', None, 'POR', 2), (r'^Regency of Algiers$', None, 'ALG', 2),
    (r'^(Qajar Iran|Persia)$', None, 'PER', 2), (r'^Kingdom of Kartli-Kakheti$', None, 'GEO', 2),
    # level-4 members of the Holy Roman Empire (count only up to 1806)
    (r'^Electorate of Saxony$', '4', 'SAX', 2, 1795, 1806), (r'^Hanover$', '4', 'HAN', 2, 1795, 1805), (r'^Bremen-Verden$', '4', 'HAN', 2, 1795, 1805),
    (r'^(Hesse-Kassel|Electorate of Hesse)$', '4', 'HKA', 2, 1795, 1806), (r'^Margraviate of Baden$', '4', 'BAD', 2, 1795, 1806),
    (r'^Hesse-Darmstadt$', '4', 'HDA', 2, 1795, 1806), (r'^Duchy of Mecklenburg-Schwerin$', '4', 'MKS', 2, 1795, 1806),
    (r'^Duchy of Mecklenburg-Strelitz$', '4', 'MKST', 2, 1795, 1806), (r'^Duchy of Oldenburg$', '4', 'OLD', 2, 1795, 1806),
    (r'^Brunswick-Wolfenbüttel$', '4', 'BRU', 2, 1795, 1806), (r'^(Electorate|Prince-Archbishopric) of Salzburg$', '4', 'SAL', 2, 1795, 1805),
    (r'^(Swedish Pomerania|Swedish Wismar)$', '4', 'SWE', 2, 1795, 1806), (r'^(Lippe|Principality of Lippe)$', '4', 'LIP', 2, 1795, 1806),
    (r'^Waldeck$', '4', 'WALD', 2, 1795, 1806), (r'^Schaumburg-Lippe$', '4', 'SCH', 2, 1795, 1806), (r'^Liechtenstein$', '4', 'LIE', 2, 1795, 1806),
    (r'^Nassau-Weilburg$', '4', 'NAS', 2, 1795, 1806), (r'^(Duchy|Principality) of Anhalt', '4', 'ANH', 2, 1795, 1806),
    (r'^Principality of Schwarzburg', '4', 'SWB', 2, 1795, 1806), (r'^Hohenzollern-Hechingen$', '4', 'HOH', 2, 1795, 1806),
    (r'^Principality of Regensburg$', '4', 'REG', 2, 1795, 1806), (r'^Principality of Aschaffenburg$', '4', 'ASC', 2, 1795, 1806),
    (r'^Duchy of Arenberg-Meppen$', '4', 'ARE', 2, 1795, 1806), (r'^Free and Hanseatic City of Lübeck$', '4', 'LUB', 2, 1795, 1806),
    (r'^Bremen$', '4', 'BRE', 2, 1795, 1806), (r'^Duchy of Berg$', '4', 'BERG', 2, 1795, 1806),
    (r'^Principality of Neuchâtel$', '4', 'PRU', 2, 1795, 1806),
    (r'^(Electorate of Brandenburg|Silesia|Province of (South|West|New East) Prussia|New Silesia|Netze District|Duchy of Magdeburg|County of Mark|Duchy of Cleves|Kriegs- und Domänenkammer Minden|General Directory of War and Finance in Pomerania|Principality of (Paderborn|Hildesheim)|Kammer-Deputation für Lingen und Tecklenburg)$', '4', 'PRU', 2, 1795, 1806),
    (r'^(Bohemia|Gubernium Moravia et Silesia|Tirol|Styria|Austria below the Enns|Carinthia|Duchy of Carniola|Triest|Gorizia and Gradisca|Margraviate of Istria|Venetian Province|Transylvania|Slavonian Military Frontier|Banat Military Frontier|City of Fiume and its District|Circulus .*)$', '4', 'AUT', 2, 1795, 1805),
]
ROLES = [(re.compile(x[0]), x[1], x[2], x[3], x[4] if len(x) > 4 else 0, x[5] if len(x) > 5 else 9999) for x in _R]
# any other level-4 record active 1800-1806 inside the Holy Roman Empire is one of its many small states
HRE_MINOR = re.compile(r'^(Free Imperial City|Imperial (City|Abbey|County|Lordship)|Prince-(Bishopric|Provostry)|Princely Abbey|County of|Principality of (Hohenlohe|Nassau-Orange-Fulda)|Saint Blaise|Freies Reichsdorf|Sayn-Wittgenstein|Duchy of Palatinate)')


def ohm_roles(name, level):
    """All roles a record can play, in order: list of (unit, priority, from_year, to_year).
    For a given year the first role valid in that year applies."""
    name = name or ''
    out = []
    for rx, lv, unit, pri, y0, y1 in ROLES:
        if (lv is None or lv == level) and rx.search(name):
            out.append((unit, pri, y0, y1))
    if not out and level == '4' and HRE_MINOR.search(name):
        out.append(('HRE', 2, 1795, 1806))
    return out


# a few unit keys only mark a status; they fold back into display units
FOLD = {'ROM_V': 'ROM_V', 'SRB_I': 'SRB_I', 'TUN_F': 'TUN_F'}
UNITS['ROM_V'] = ('United Principalities', 'OTT', 'ROM')
UNITS['SRB_I'] = ('Serbia', None, 'SRB')
UNITS['TUN_F'] = ('Tunisia (French protectorate)', 'FRA', 'TUN')


def sovereign(u, year):
    """The unit that holds sovereignty (used to compare sources, which disagree about
    whether self-governing territories count as their own)."""
    if u is None: return None
    ov = UNITS[u][1]
    if u in ('ROM_V', 'WAL', 'MOL', 'SRB', 'BUL', 'ERU', 'CRT', 'EGY', 'ALG', 'TUN'): return 'OTT'
    if u == 'SRB_I': return 'SRB'
    if u in ('FIN', 'POL'): return 'RUS'
    if u == 'NOR' and year < 1905: return 'SWE'
    if u == 'CYP' or u == 'ION_S': return 'OTT'
    if u == 'ION': return 'GBR'
    if u == 'LUX' and year < 1868: return 'NLD'
    if u == 'SIC' and (year <= 1805 or year >= 1815): return 'NAP'   # same Bourbon king
    if u == 'AUT_OCC': return 'OTT'
    if u == 'TUN_F': return 'TUN'
    if u == 'GER' or u == 'PRU': return 'PRU'
    if u == 'ITA' or u == 'SAR': return 'SAR'
    if u == 'SRB_I': return 'SRB'
    return u


# ---------- CShapes-Europe ----------
CS = {
    'Andorra': 'AND', 'Anhalt': 'ANH', 'Anhalt-Bernberg': 'ANH', 'Anhalt-Dessau': 'ANH', 'Austria-Hungary': 'AUT',
    'Baden': 'BAD', 'Bavaria': 'BAV', 'Belgium': 'BEL', 'Bosnia': 'AUT_OCC', 'Herzegovina': 'AUT_OCC', 'Bremen': 'BRE',
    'Bulgaria': 'BUL', 'Chechens': 'CAU', 'Circassia': 'CAU', 'Cracow': 'KRA', 'Denmark': 'DEN', 'Egypt': 'EGY',
    'France': 'FRA', 'Frankfurt': 'FRK', 'Germany': 'PRU', 'Germany (Prussia)': 'GER', 'Greece': 'GRE', 'Hanover': 'HAN',
    'Hesse-Darmstadt (Ducal': 'HDA', 'Hesse-Homburg': 'HHO', 'Hesse-Kassel (Electoral)': 'HKA', 'Hohengeroldseck': 'HGE',
    'Hohenzollern-Hechingen': 'HOH', 'Hohenzollern-Sigmaringen': 'HOH', 'Iceland': 'DEN', 'Italy': 'ITA', 'Italy/Sardinia': 'ITA',
    'Kingdom of Naples': 'NAP', 'Liechtenstein': 'LIE', 'Lippe-Detmold': 'LIP', 'Lucca': 'LUC', 'Luxembourg': 'LUX',
    'Malta': 'GBR', 'Massa': 'MAS', 'Mecklenburg-Schwerin': 'MKS', 'Mecklenburg-Strelitz': 'MKST', 'Modena': 'MOD',
    'Monaco': 'MON', 'Montenegro': 'MNE', 'Nassau': 'NAS', 'Netherlands': 'NLD', 'Norway': 'NOR', 'Oldenburg': 'OLD',
    'Ottoman Empire': 'OTT', 'Turkey (Ottoman Empire)': 'OTT', 'Papal States': 'PAP', 'Parma': 'PAR', 'Piedmont': 'SAR',
    'Portugal': 'POR', 'Reuss': 'REU', 'Romania': 'ROM', 'Rumania': 'ROM', 'Russia': 'RUS', 'Russia (Soviet Union)': 'RUS',
    'San Marino': 'SMR', 'Saxe-Altenburg': 'SXA', 'Saxe-Coburg-Gotha': 'SXC', 'Saxe-Coburg-Saalfeld': 'SXC',
    'Saxe-Gotha-Altenberg': 'SXO', 'Saxe-Hildburgchausen': 'SXO', 'Saxe-Meiningen': 'SXM', 'Saxe-Weimar': 'SXW',
    'Saxony': 'SAX', 'Schaumburg Lippe': 'SCH', 'Serbia': 'SRB_I', 'Spain': 'ESP', 'Sweden': 'SWE', 'Switzerland': 'SUI',
    'Tunisia': 'TUN', 'United Kingdom': 'GBR', 'Waldeck': 'WALD', 'Wolfenbuttel': 'BRU', 'Württemberg': 'WUR',
}
UNITS['HGE'] = ('Hohengeroldseck', None, 'HGE')
UNITS['AUT_OCC'] = ('Bosnia (Austrian-run)', 'OTT', 'AUT')


def cs_unit(name, status, year):
    u = CS.get(name)
    if u == 'PRU' and year >= 1871: u = 'GER'
    if u == 'BUL' and status == 'independent' and year < 1908: u = 'BUL'
    return u


# ---------- Cliopatria ----------
_C = [
    (r'Austria-Hungary|Austrian Empire|Habsburg Monarchy', 'AUT'), (r'Batavian Republic|Dutch Republic|^Netherlands$|United Netherlands', 'NLD'),
    (r'Beylik of Tunis', 'TUN'), (r'French|Bourbon Kingdom of France|First French Empire|Second French Empire', 'FRA'),
    (r'Caucasian Imamate|Khanates of the Caucasus|Abkhazia|Guria|Mingrelia|Svaneti|Kingdom of Imereti', 'CAU'),
    (r'Kingdom of Georgia', 'GEO'), (r'Cisalpine Republic|Cispadane Republic|Italian Republic', 'NIT'), (r'Cretan State', 'CRT'),
    (r'Denmark-Norway', 'DEN'), (r'Duchy of Anhalt', 'ANH'), (r'Duchy of Bavaria|Kingdom of Bavaria', 'BAV'), (r'Duchy of Brunswick', 'BRU'),
    (r'Duchy of Holstein', 'DEN'), (r'Duchy of Mecklenburg', 'MKS'), (r'Duchy of Modena', 'MOD'), (r'Duchy of Nassau', 'NAS'),
    (r'Duchy of Oldenburg', 'OLD'), (r'Duchy of Parma', 'PAR'), (r'Duchy of Warsaw', 'WAR'), (r'Baden', 'BAD'),
    (r'Hanover', 'HAN'), (r'Electorate of Hesse', 'HKA'), (r'Salzburg', 'SAL'), (r'Saxony', 'SAX'), (r'Württemberg', 'WUR'),
    (r'First Hellenic Republic', 'GRE'), (r'Spanish Republic|Kingdom of Spain', 'ESP'), (r'Free City of Bremen', 'BRE'),
    (r'Free City of Danzig', 'DAN'), (r'Free City of Frankfurt', 'FRK'), (r'Free City of Hamburg', 'HAM'), (r'Free City of Krakow', 'KRA'),
    (r'Free City of Lübeck', 'LUB'), (r'German Empire', 'GER'), (r'Grand Duchy of Berg', 'BERG'), (r'Grand Duchy of Hesse', 'HDA'),
    (r'Saxe-Weimar', 'SXW'), (r'Tuscany|Kingdom of Etruria', 'TUS'), (r'Würzburg', 'WRZ'), (r'Helvetic Republic|Swiss Confederation', 'SUI'),
    (r'Holy Roman Empire Minor States', 'HRE'), (r'Kingdom of Belgium', 'BEL'), (r'Kingdom of Great Britain', 'GBR'),
    (r'Kingdom of Italy', 'ITA'), (r'Monaco', 'MON'), (r'Kingdom of Naples', 'NAP'), (r'Kingdom of Norway', 'NOR'),
    (r'Kingdom of Portugal', 'POR'), (r'Kingdom of Prussia', 'PRU'), (r'Kingdom of Sardinia', 'SAR'), (r'Kingdom of Serbia', 'SRB_I'),
    (r'Kingdom of Sweden|Swedish Empire|United Kingdoms of Sweden and Norway', 'SWE'), (r'Kingdom of Westphalia', 'WES'),
    (r'Two Sicilies', 'NAP'), (r'Ligurian Republic|Republic of Genoa', 'GEN'), (r'Luxembourg', 'LUX'), (r'Montenegro', 'MNE'),
    (r'Morocco', 'MOR'), (r'Muhammad Ali', 'EGY'), (r'Ottoman Empire', 'OTT'), (r'Papal States|Roman Republic', 'PAP'),
    (r'Principality of Andorra', 'AND'), (r'Principality of Bulgaria', 'BUL'), (r'Hohenzollern', 'HOH'), (r'Lichtenberg', 'SXC'),
    (r'Liechtenstein', 'LIE'), (r'Principality of Lippe', 'LIP'), (r'Principality of Moldavia', 'MOL'), (r'Regensberg', 'REG'),
    (r'Reuss', 'REU'), (r'Schwarzburg', 'SWB'), (r'Waldeck', 'WALD'), (r'Principality of Wallachia', 'WAL'), (r'Qajar', 'PER'),
    (r'Regency of Algiers', 'ALG'), (r'Republic of Ragusa', 'RAG'), (r'San Marino', 'SMR'), (r'Republic of Venice', None),
    (r'Russian Empire|Bessarabia', 'RUS'), (r'Saxe-Altenburg', 'SXA'), (r'Saxe-Coburg', 'SXC'), (r'Saxe-Meiningen', 'SXM'),
    (r'Septinsular Republic', 'ION_S'), (r'United Principalities', 'ROM_V'), (r'Confederation of the Rhine', 'RHC'),
    (r'German Confederation', None), (r'Nationalists|^Poles$|^Serbs$|Republic of Baden|County of Urgell|Dutch East Indies|French Africa|French Equatorial', None),
]
_CR = [(re.compile(a), b) for a, b in _C]


def clio_unit(name):
    if name.startswith('('): return None          # umbrella groupings
    for rx, u in _CR:
        if rx.search(name): return u
    return None
