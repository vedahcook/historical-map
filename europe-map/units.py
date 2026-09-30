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
    if u in NEW20: u = sovereign20(u, year)
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
    if year < 1906: return u
    # 1906 onward
    u = CS20.get(name, u)
    if name == 'Bulgaria' and year >= 1908: u = 'BUL_I'
    if name == 'Turkey (Ottoman Empire)' and year >= 1923: u = 'TUR'
    if name in ('Serbia', 'Montenegro') and status == 'occupied': u = 'O_AUT_SRB_I' if name == 'Serbia' else 'O_AUT_MNE'
    if name == 'German Federal Republic': u = 'GER_FR' if status == 'occupied' else ('FRG' if year < 1990 else 'GER')
    if name == 'German Democratic Republic': u = 'GER_SU' if status == 'occupied' else 'GDR'
    if name == 'Iceland': u = 'DEN' if status == 'colony' else ('O_USA_ISL' if status == 'occupied' else 'ISL')
    if name == 'Malta': u = 'GBR' if status == 'colony' else 'MLT'
    if name == 'Tunisia': u = 'TUN_F' if status == 'protectorate' else 'TUN_I'
    if name == 'Finland': u = 'FIN_I'
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


def clio_unit(name, from_year=0):
    if name.startswith('('): return None          # umbrella groupings
    if from_year >= 1906:
        u = CLIO20.get(name)
        if u is not None: return u or None
    for rx, u in _CR:
        if rx.search(name): return u
    return None


_OLD_UNITS = set(UNITS)

# =====================================================================================
# 1900-2026
# =====================================================================================
# Two kinds of dependent territory are drawn differently:
#   stripes    self-governing under an overlord, a protectorate, mandate or colony, or a
#              client state set up by another power (overlord = UNITS[u][1])
#   crosshatch occupied by another power, annexed without international recognition, or
#              held by a breakaway government with another power's backing (KIND[u] == 'occ')
# DEJURE[u] is the country an occupied area belonged to in law; alternative borders are
# compared against it, because the sources differ on whether to show occupations.
KIND, DEJURE = {}, {}

def _u(key, name, ov, fam, occ=None):
    UNITS[key] = (name, ov, fam)
    if occ: KIND[key] = 'occ'; DEJURE[key] = occ

for k, n, ov, fam in [
    ('TUR', 'Turkey', None, 'OTT'), ('BUL_I', 'Bulgaria', None, 'BUL'), ('FIN_I', 'Finland', None, 'FIN'),
    ('POL_I', 'Poland', None, 'POL'), ('POL_R', 'Kingdom of Poland (German-backed)', 'GER', 'POL'),
    ('EST', 'Estonia', None, 'EST'), ('LVA', 'Latvia', None, 'LVA'), ('LTU', 'Lithuania', None, 'LTU'),
    ('BLR', 'Belarus', None, 'BLR'), ('UKR', 'Ukraine', None, 'UKR'), ('MDA', 'Moldova', None, 'MDA'),
    ('ARM', 'Armenia', None, 'ARM'), ('AZE', 'Azerbaijan', None, 'AZE'), ('KAZ', 'Kazakhstan', None, 'KAZ'),
    ('UKR_S', 'Soviet Ukraine', 'RUS', 'UKR'), ('BLR_S', 'Soviet Belarus', 'RUS', 'BLR'), ('GEO_S', 'Soviet Georgia', 'RUS', 'GEO'),
    ('ARM_S', 'Soviet Armenia', 'RUS', 'ARM'), ('AZE_S', 'Soviet Azerbaijan', 'RUS', 'AZE'), ('TSF', 'Transcaucasian SFSR', 'RUS', 'AZE'),
    ('WHT', 'South Russia (White government)', None, 'WHT'), ('MRNC', 'Mountain Republic', None, 'CAU'),
    ('CSK', 'Czechoslovakia', None, 'CSK'), ('CZE', 'Czech Republic', None, 'CSK'), ('SVK', 'Slovakia', None, 'SVK'),
    ('SVK_W', 'Slovak Republic (German client)', 'GER', 'SVK'), ('HUN', 'Hungary', None, 'HUN'),
    ('YUG', 'Yugoslavia', None, 'SRB'), ('HRV', 'Croatia', None, 'HRV'), ('SVN', 'Slovenia', None, 'SVN'),
    ('BIH', 'Bosnia and Herzegovina', None, 'BIH'), ('MKD', 'North Macedonia', None, 'MKD'), ('KOS', 'Kosovo', None, 'KOS'),
    ('NDH', 'Independent State of Croatia (Axis client)', 'GER', 'HRV'), ('BIH_A', 'Bosnia and Herzegovina (Austro-Hungarian)', 'AUT', 'AUT'),
    ('ALB', 'Albania', None, 'ALB'), ('KOR', 'Korçë (French-protected)', 'FRA', 'ALB'),
    ('ISL', 'Iceland', None, 'ISL'), ('IRL', 'Ireland', None, 'IRL'), ('VAT', 'Vatican City', None, 'VAT'),
    ('FRG', 'West Germany', None, 'PRU'), ('GDR', 'East Germany', None, 'GDR'), ('WBE', 'West Berlin', 'FRG', 'PRU'),
    ('RSI', 'Italian Social Republic (German client)', 'GER', 'SAR'), ('DOD', 'Italian Aegean Islands', 'ITA', 'DOD'),
    ('DAN', 'Danzig', None, 'DAN'), ('FIU', 'Fiume', None, 'FIU'), ('MEM', 'Memel Territory (Allied-run)', 'FRA', 'MEM'),
    ('SAA_L', 'Saar (League of Nations)', None, 'SAA'), ('SAA', 'Saar Protectorate', 'FRA', 'SAA'),
    ('TRI', 'Free Territory of Trieste', None, 'TRI'),
    ('CYP_B', 'Cyprus (British)', 'GBR', 'GBR'), ('CYP_I', 'Cyprus', None, 'CYP'), ('MLT', 'Malta', None, 'MLT'),
    ('MOR_F', 'Morocco (French protectorate)', 'FRA', 'MOR'), ('MOR_S', 'Morocco (Spanish protectorate)', 'ESP', 'MOR'),
    ('TNG', 'Tangier', None, 'TNG'), ('RIF', 'Republic of the Rif', None, 'RIF'), ('TUN_I', 'Tunisia', None, 'TUN'),
    ('ALG_I', 'Algeria', None, 'ALG'), ('SYR_M', 'Syria (French mandate)', 'FRA', 'SYR'), ('SYR', 'Syria', None, 'SYR'),
    ('LEB_M', 'Lebanon (French mandate)', 'FRA', 'LEB'), ('LEB', 'Lebanon', None, 'LEB'),
    ('IRQ_M', 'Iraq (British mandate)', 'GBR', 'IRQ'), ('IRQ', 'Iraq', None, 'IRQ'), ('USA', 'United States', None, 'USA'),
]:
    _u(k, n, ov, fam)

# named occupation regimes and breakaway states (drawn crosshatched)
for k, n, ov, fam, dj in [
    ('GGV', 'General Government', 'GER', 'POL', 'POL_I'), ('BOH', 'Protectorate of Bohemia and Moravia', 'GER', 'CSK', 'CSK'),
    ('OST', 'Reichskommissariat Ostland', 'GER', 'LTU', 'RUS'), ('RKU', 'Reichskommissariat Ukraine', 'GER', 'UKR', 'RUS'),
    ('BNF', 'German-occupied Belgium and northern France', 'GER', 'BEL', 'BEL'),
    ('SRB_O', 'German-occupied Serbia', 'GER', 'SRB', 'YUG'), ('AUT_ANX', 'Austria (annexed by Germany)', 'GER', 'AUT', 'AUT'),
    ('EST_SSR', 'Estonian SSR (Soviet-annexed)', 'RUS', 'EST', 'EST'), ('LVA_SSR', 'Latvian SSR (Soviet-annexed)', 'RUS', 'LVA', 'LVA'),
    ('LTU_SSR', 'Lithuanian SSR (Soviet-annexed)', 'RUS', 'LTU', 'LTU'),
    ('GER_US', 'American zone of Germany', 'USA', 'PRU', 'GER'), ('GER_UK', 'British zone of Germany', 'GBR', 'PRU', 'GER'),
    ('GER_FR', 'French zone of Germany', 'FRA', 'PRU', 'GER'), ('GER_SU', 'Soviet zone of Germany', 'RUS', 'PRU', 'GER'),
    ('AUT_US', 'American zone of Austria', 'USA', 'AUT', 'AUT'), ('AUT_UK', 'British zone of Austria', 'GBR', 'AUT', 'AUT'),
    ('AUT_FR', 'French zone of Austria', 'FRA', 'AUT', 'AUT'), ('AUT_SU', 'Soviet zone of Austria', 'RUS', 'AUT', 'AUT'),
    ('TRA', 'Trieste Zone A (Allied-run)', 'GBR', 'TRI', 'TRI'), ('TRB', 'Trieste Zone B (Yugoslav-run)', 'YUG', 'TRI', 'TRI'),
    ('NCY', 'Northern Cyprus', 'TUR', 'CYP', 'CYP_I'), ('TRN', 'Transnistria', 'RUS', 'MDA', 'MDA'),
    ('ABK', 'Abkhazia', 'RUS', 'GEO', 'GEO'), ('SOS', 'South Ossetia', 'RUS', 'GEO', 'GEO'), ('ART', 'Artsakh (Nagorno-Karabakh)', 'ARM', 'AZE', 'AZE'),
    ('DLR', 'Donetsk and Luhansk "people’s republics"', 'RUS', 'UKR', 'UKR'), ('UKR_O', 'Russian-occupied Ukraine', 'RUS', 'UKR', 'UKR'),
]:
    _u(k, n, ov, fam, dj)

# Generic occupation units, one per (occupier, occupied country): O_<occupier>_<country>.
ADJ = {'GER': 'German', 'AUT': 'Austro-Hungarian', 'BUL_I': 'Bulgarian', 'BUL': 'Bulgarian', 'ITA': 'Italian', 'HUN': 'Hungarian',
       'RUS': 'Soviet', 'GBR': 'British', 'USA': 'American', 'FRA': 'French', 'ROM': 'Romanian', 'GRE': 'Greek', 'TUR': 'Turkish',
       'FIN_I': 'Finnish', 'BEL': 'Belgian', 'YUG': 'Yugoslav', 'ALB': 'Albanian', 'SRB_I': 'Serbian'}
def occ_unit(occupier, country, annexed=False):
    key = ('A_' if annexed else 'O_') + occupier + '_' + country
    if key not in UNITS:
        cname = UNITS[country][0]
        name = f'{cname} (annexed by {UNITS[occupier][0]})' if annexed else f'{ADJ.get(occupier, UNITS[occupier][0])}-occupied {cname}'
        _u(key, name, occupier, UNITS[country][2], country)
    return key

# pairs that get a unit up front (so KEYS is fixed before assignment)
for a, b in [('GER', 'BEL'), ('GER', 'FRA'), ('GER', 'LUX'), ('GER', 'POL'), ('AUT', 'POL'), ('GER', 'RUS'), ('GER', 'UKR'), ('AUT', 'UKR'),
             ('GER', 'BLR'), ('GER', 'EST'), ('GER', 'LVA'), ('GER', 'LTU'), ('AUT', 'SRB_I'), ('BUL_I', 'SRB_I'), ('AUT', 'MNE'), ('GER', 'ROM'),
             ('AUT', 'ROM'), ('BUL_I', 'ROM'), ('AUT', 'ITA'), ('AUT', 'ALB'), ('ITA', 'ALB'), ('FRA', 'ALB'), ('GBR', 'OTT'), ('FRA', 'OTT'),
             ('GRE', 'OTT'), ('ITA', 'OTT'), ('FRA', 'GER'), ('GBR', 'GER'), ('USA', 'GER'), ('BEL', 'GER'), ('ROM', 'HUN'), ('YUG', 'HUN'),
             ('GER', 'POL_I'), ('GER', 'CSK'), ('GER', 'NOR'), ('GER', 'DEN'), ('GER', 'NLD'), ('ITA', 'FRA'), ('GER', 'YUG'), ('ITA', 'YUG'),
             ('BUL_I', 'YUG'), ('HUN', 'YUG'), ('GER', 'GRE'), ('ITA', 'GRE'), ('BUL_I', 'GRE'), ('ROM', 'RUS'), ('FIN_I', 'RUS'), ('HUN', 'RUS'),
             ('GER', 'ITA'), ('GER', 'HUN'), ('GER', 'ALB'), ('GER', 'MON'), ('ITA', 'MON'), ('GER', 'GBR'), ('GBR', 'ISL'), ('USA', 'ISL'),
             ('GBR', 'DEN'), ('RUS', 'EST'), ('RUS', 'LVA'), ('RUS', 'LTU'), ('ITA', 'MNE'), ('GER', 'MNE'), ('GER', 'DOD'), ('RUS', 'PER'), ('GBR', 'PER'),
             ('RUS', 'UKR')]:
    occ_unit(a, b)
for a, b in [('GER', 'CSK'), ('GER', 'POL_I'), ('GER', 'FRA'), ('GER', 'LUX'), ('GER', 'BEL'), ('GER', 'LTU'), ('GER', 'YUG'), ('ITA', 'YUG'),
             ('ITA', 'FRA'), ('ITA', 'GRE'), ('HUN', 'CSK'), ('HUN', 'ROM'), ('HUN', 'YUG'), ('BUL_I', 'YUG'), ('BUL_I', 'GRE'),
             ('ALB', 'YUG'), ('GER', 'ITA'), ('RUS', 'FIN_I'), ('HUN', 'RUS')]:
    occ_unit(a, b, annexed=True)

# OHM roles for 1900-2026. Priority 4 = a named occupation regime (beats the country record under it).
_R20 = [
    # occupation regimes and breakaway states
    (r'^Generalgouvernement$', '3', 'GGV', 4), (r'^Protectorate of Bohemia and Moravia$', '3', 'BOH', 4),
    (r'^Reichskommissariat Ostland$', '3', 'OST', 4), (r'^Reichskommissariat Ukraine$', '3', 'RKU', 4), (r'^Bezirk Bialystok$', '3', 'O_GER_POL_I', 4),
    (r'^Military Administration in Belgium and Northern France$', None, 'BNF', 4), (r'^Territory of the Military Commander in Serbia$', None, 'SRB_O', 4),
    (r'^Governorate of Montenegro$', None, 'O_ITA_MNE', 4), (r'^German-occupied territory of Montenegro$', None, 'O_GER_MNE', 4),
    (r'^Italian protectorate of Albania$', None, 'O_ITA_ALB', 4), (r'^German occupation of Albania$', None, 'O_GER_ALB', 4),
    (r'^German occupation of Italy$', None, 'O_GER_ITA', 4), (r'^Operational Zone of the (Alpine Foothills|Adriatic Littoral)$', '4', 'A_GER_ITA', 5),
    (r'^German occupation of the Dodecanese$', None, 'O_GER_DOD', 4), (r'^Italian occupation of Corsica$', '4', 'O_ITA_FRA', 4),
    (r'^Occupied Monaco$', None, 'O_ITA_MON', 4, 1942, 1943), (r'^Occupied Monaco$', None, 'O_GER_MON', 4, 1944, 1944),
    (r'^German Occupation Zone-Denmark$', None, 'O_GER_DEN', 4),
    (r'^(State of Austria|Ostmark|Alpen- und Donau-Reichsgaue)$', '3', 'AUT_ANX', 4),
    (r'^Estonia SSR$', '3', 'EST_SSR', 3), (r'^Latvian Soviet Socialist Republic$', '3', 'LVA_SSR', 3), (r'^Lithuanian SSR$', '3', 'LTU_SSR', 3),
    (r'^American occupation zone in Germany$', None, 'GER_US', 4, 1945, 1948), (r'^British occupation zone in Germany$', None, 'GER_UK', 4, 1945, 1948),
    (r'^American Occupation Zone in Austria$', '3', 'AUT_US', 4), (r'^British Occupation Zone in Austria$', '3', 'AUT_UK', 4),
    (r'^French Occupation Zone in Austria$', '3', 'AUT_FR', 4), (r'^Soviet Occupation Zone in Austria$', '3', 'AUT_SU', 4),
    (r'^Zona A$', '3', 'TRA', 4), (r'^Zona B$', '3', 'TRB', 4), (r'^Free Territory of Trieste$', None, 'TRI', 1),
    (r'^Northern Cyprus$', '4', 'NCY', 4), (r'^(Republic of Artsakh|Արցախի Հանրապետություն)$', '3', 'ART', 4, 1994, 2023),
    (r'^Republic of Crimea$', '4', 'UKR_O', 4, 2014, 2021),
    # client states, protectorates, mandates, colonies (stripes)
    (r'^Regency Kingdom of Poland$', None, 'POL_R', 3), (r'^General Government of Warsaw$', None, 'O_GER_POL', 4),
    (r'^General Government of Lublin$', None, 'O_AUT_POL', 4), (r'^(Slovak State|Slovak Republic)$', '2', 'SVK_W', 3),
    (r'^Independent State of Croatia$', None, 'NDH', 3), (r'^Italian Social Republic$', None, 'RSI', 3),
    (r'^Condominium of Bosnia and Herzegovina$', '3', 'BIH_A', 3), (r'^Autonomous Province of Korçë$', '3', 'KOR', 3),
    (r'^Italian Islands of the Aegean$', None, 'DOD', 3), (r'^Klaipėda Region$', None, 'MEM', 3),
    (r'^(British Occupation of Cyprus|British Cyprus)$', None, 'CYP_B', 3),
    (r'^French protectorate in Morocco$', None, 'MOR_F', 3), (r'^Spanish protectorate in Morocco$', None, 'MOR_S', 3),
    (r'^Saar Protectorate$', None, 'SAA', 3), (r'^Territory of the Saar Basin$', '3', 'SAA_L', 3), (r'^West Berlin$', '3', 'WBE', 3),
    (r'^(State of Aleppo|State of Damascus|Syrian Federation|State of Syria|Alawite State|Syrian Republic)$', None, 'SYR_M', 3, 1900, 1945),
    (r'^Syrian Republic$', None, 'SYR', 2, 1946, 9999), (r'^(United Arab Republic|Syrian Arab Republic|Syria)$', None, 'SYR', 2),
    (r'^(State of Greater Lebanon|Lebanese Republic)$', None, 'LEB_M', 3), (r'^Lebanon$', None, 'LEB', 2),
    (r'^Mandatory Iraq$', None, 'IRQ_M', 3), (r'^(Hashemite Kingdom of Iraq|Iraq)$', None, 'IRQ', 2),
    (r'^Ukrainian SSR$', '2', 'UKR_S', 3), (r'^Ukrainian SSR$', '3', 'UKR_S', 3, 1900, 1922), (r'^Byelorussian SSR$', '3', 'BLR_S', 3, 1900, 1922),
    (r'^SSR of Georgia$', '2', 'GEO_S', 3), (r'^SSR of Armenia$', '2', 'ARM_S', 3), (r'^Azerbaijan SSR$', None, 'AZE_S', 3, 1900, 1922),
    (r'^Abkhazia SSR$', '3', 'GEO_S', 3), (r'^FUSSR of Transcaucasia$', '2', 'TSF', 3),
    # Soviet republics inside the USSR (1923-1991) are part of it
    (r'^(Ukrainian SSR|Byelorussian SSR|Azerbaijan SSR|Georgian SSR|Armenian SSR|Kazakh SSR|Moldavian SSR|Karelo-Finnish Soviet Socialist Republic|Transcaucasian SFSR|Russian Soviet Federative Socialist Republic|Dagestan SSR|Republic of Moldova)$', '3', 'RUS', 2),
    # countries
    (r'^(Russian Republic|Russian Soviet Federative Socialist Republic|Soviet Union|Russia)$', '2', 'RUS', 2),
    (r'^(Central|Northwestern|Southern|Volga|North Caucasian|Crimean) Federal District$', '3', 'RUS', 2),
    (r'^(State of Turkey|Turkey|Türkiye)$', '2', 'TUR', 2), (r'^(Tsardom of Bulgaria|People\'s Republic of Bulgaria|Bulgaria)$', '2', 'BUL_I', 2),
    (r'^Finland$', '2', 'FIN_I', 2), (r'^Poland$', '2', 'POL_I', 2), (r'^Estonia$', '2', 'EST', 2), (r'^Latvia$', '2', 'LVA', 2),
    (r'^Lithuania$', '2', 'LTU', 2), (r'^(Belarusian People\'s Republic|Belarus)$', '2', 'BLR', 2), (r'^Ukraine$', '2', 'UKR', 2),
    (r'^Moldova$', '2', 'MDA', 2), (r'^Armenia$', '2', 'ARM', 2), (r'^Azerbaijan$', '2', 'AZE', 2), (r'^Georgia$', '2', 'GEO', 2),
    (r'^Kazakhstan$', '2', 'KAZ', 2), (r'^Government of South Russia$', None, 'WHT', 2),
    (r'^Mountainous Republic of the Northern Caucasus$', None, 'MRNC', 2),
    (r'^(Czechoslovakia|Czechoslovak Republic|Czechoslovak Socialist Republic|Czechoslovak Federative Republic|Czech and Slovak Federative Republic)$', '2', 'CSK', 2),
    (r'^(Czech Republic|Slovakia)$', '3', 'CSK', 2), (r'^Czech Republic$', '2', 'CZE', 2), (r'^Slovakia$', '2', 'SVK', 2),
    (r'^(Kingdom of Hungary|Hungarian Republic|Hungarian People\'s Republic|Hungary)$', '2', 'HUN', 2),
    (r'^(Kingdom of Serbs, Croats and Slovenes|Kingdom of Yugoslavia|Democratic Federal Yugoslavia|FPR of Yugoslavia|SFR of Yugoslavia|Yugoslavia|Serbia and Montenegro)$', '2', 'YUG', 2),
    (r'^(Province of Bosnia and Herzegovina|Province of Croatia and Slavonia|Province of Slovenia|Republic of Serbia|Montenegro)$', '3', 'YUG', 2),
    (r'^Serbia$', '2', 'SRB_I', 2), (r'^Montenegro$', '2', 'MNE', 2), (r'^Kingdom of Montenegro$', '2', 'MNE', 2),
    (r'^Croatia$', '2', 'HRV', 2), (r'^Slovenia$', '2', 'SVN', 2), (r'^Bosnia and Herzegovina$', '2', 'BIH', 2),
    (r'^(FYR Macedonia|North Macedonia)$', '2', 'MKD', 2), (r'^Kosovo$', '2', 'KOS', 2),
    (r'^(Principality of Albania|Albanian Republic|Albanian Kingdom|Albania|Democratic Government of Albania|People\'s Republic of Albania|People\'s Socialist Republic of Albania)$', '2', 'ALB', 2),
    (r'^(Kingdom of Iceland|Iceland)$', '2', 'ISL', 2), (r'^(Irish Free State|Ireland)$', '2', 'IRL', 2), (r'^Vatican City$', None, 'VAT', 2),
    (r'^Austria$', '2', 'AUT', 2), (r'^(Free State of Prussia)$', '3', 'GER', 2), (r'^West Germany$', '2', 'FRG', 2),
    (r'^East Germany$', '2', 'GDR', 2), (r'^Germany$', '2', 'GER', 2),
    (r'^(France|French State)$', '2', 'FRA', 2), (r'^Akrotiri and Dhekelia$', None, 'GBR', 2), (r'^United Kingdom$', '2', 'GBR', 2),
    (r'^British (Dependent|Overseas) Territories$', '3', 'GBR', 2), (r'^Greece$', '2', 'GRE', 2), (r'^Portugal$', '2', 'POR', 2),
    (r'^(Kingdom of Romania|Romanian People\'s Republic|Socialist Republic of Romania|Romania)$', '2', 'ROM', 2),
    (r'^Cyprus$', '2', 'CYP_I', 2), (r'^Malta$', '2', 'MLT', 2), (r'^Morocco$', '2', 'MOR', 2), (r'^Tangier International Zone$', None, 'TNG', 2),
    (r'^Republic of the Rif$', None, 'RIF', 2), (r'^Tunisia$', '2', 'TUN_I', 2), (r'^Algeria$', '2', 'ALG_I', 2), (r'^Iran$', '2', 'PER', 2),
    (r'^Free City of Danzig$', '2', 'DAN', 2), (r'^Free State of Fiume$', None, 'FIU', 2), (r'^Greenland$', None, 'DEN', 2),
]
_R20_ROLES = [(re.compile(x[0]), x[1], x[2], x[3], x[4] if len(x) > 4 else 1900, x[5] if len(x) > 5 else 9999) for x in _R20]
# the 19th-century roles stop in 1905 unless nothing newer applies
ROLES[:] = _R20_ROLES + ROLES

# de jure owner of the client states, for comparing sources
DEJURE.update({'SVK_W': 'CSK', 'NDH': 'YUG', 'RSI': 'ITA', 'POL_R': 'POL_I', 'WBE': 'FRG'})


def sovereign20(u, year):
    """Sovereignty for comparing sources, 1900 onward (see sovereign())."""
    if u in DEJURE: return sovereign20(DEJURE[u], year)
    if u in ('UKR_S', 'BLR_S', 'GEO_S', 'ARM_S', 'AZE_S', 'TSF'): return 'RUS'
    if u in ('MOR_F', 'MOR_S'): return 'MOR'
    if u == 'SYR_M': return 'SYR'
    if u == 'LEB_M': return 'LEB'
    if u == 'IRQ_M': return 'IRQ'
    if u in ('CYP_B', 'CYP'): return 'GBR' if year < 1960 else 'CYP_I'
    if u == 'BIH_A': return 'AUT'
    if u == 'KOR': return 'ALB'
    if u in ('FRG', 'GER'): return 'GER'
    if u == 'CZE': return 'CZE'
    if u in ('SAA', 'SAA_L'): return 'GER' if year < 1947 else 'SAA'
    if u == 'DOD': return 'ITA'
    if u == 'MEM': return 'LTU'
    return u


CS20 = {'Albania': 'ALB', 'Austria': 'AUT', 'Azerbaijan': 'AZE', 'Belarus (Byelorussia)': 'BLR', 'Bosnia-Herzegovina': 'BIH',
        'Croatia': 'HRV', 'Czech Republic': 'CZE', 'Czechoslovakia': 'CSK', 'Danzig': 'DAN', 'Estonia': 'EST', 'Georgia': 'GEO',
        'Hungary': 'HUN', 'Ireland': 'IRL', 'Kazakhstan': 'KAZ', 'Kosovo': 'KOS', 'Latvia': 'LVA', 'Lithuania': 'LTU',
        'Macedonia (FYROM/North Macedonia)': 'MKD', 'Moldova': 'MDA', 'Poland': 'POL_I', 'Serbia': 'SRB_I', 'Slovakia': 'SVK',
        'Slovenia': 'SVN', 'Ukraine': 'UKR', 'Yugoslavia': 'YUG', 'Armenia': 'ARM'}
NEW20 = set(UNITS) - set(_OLD_UNITS)


# ---------- occupations read from Cliopatria (1914-1946) ----------
# Cliopatria draws each power's area of control year by year, occupied land included. Where it
# puts an area under one of these powers while OHM shows the country that held it in law, and the
# pair is a documented occupation for that year, the map shows the area as occupied.
CLIO_OCCUPIER = {'German Empire': 'GER', 'Nazi Germany': 'GER', 'Austria-Hungary': 'AUT', 'Principality of Bulgaria': 'BUL_I',
                 'Kingdom of Bulgaria': 'BUL_I', 'Kingdom of Italy': 'ITA', 'Hungarian Republic': 'HUN',
                 'Union of Soviet Socialist Republics': 'RUS', 'United States of America': 'USA', '(British Empire)': 'GBR',
                 'Kingdom of Great Britain': 'GBR', 'French Third Republic': 'FRA', 'Kingdom of Romania': 'ROM',
                 'First Hellenic Republic': 'GRE', 'Kingdom of Greece': 'GRE', 'Republic of Finland': 'FIN_I', 'Kingdom of Belgium': 'BEL',
                 'Yugoslavia': 'YUG'}
# (occupier, country OHM shows) -> (first, last year, July 1)
OCC_PAIRS = [   # (occupier, country OHM shows, first year, last year), July 1
    ('GER', 'BEL', 1915, 1918),
    ('GER', 'FRA', 1915, 1918),
    ('GER', 'LUX', 1915, 1918),
    ('GER', 'POL', 1915, 1918),
    ('AUT', 'POL', 1915, 1918),
    ('GER', 'RUS', 1915, 1918),
    ('GER', 'UKR', 1918, 1918),
    ('AUT', 'UKR', 1918, 1918),
    ('GER', 'BLR', 1918, 1918),
    ('GER', 'EST', 1918, 1918),
    ('GER', 'LVA', 1918, 1918),
    ('GER', 'LTU', 1918, 1918),
    ('AUT', 'SRB_I', 1916, 1918),
    ('BUL_I', 'SRB_I', 1916, 1918),
    ('AUT', 'MNE', 1916, 1918),
    ('GER', 'ROM', 1917, 1918),
    ('AUT', 'ROM', 1917, 1918),
    ('BUL_I', 'ROM', 1917, 1918),
    ('AUT', 'ITA', 1918, 1918),
    ('AUT', 'ALB', 1916, 1918),
    ('ITA', 'ALB', 1915, 1920),
    ('FRA', 'ALB', 1917, 1920),
    ('FRA', 'OTT', 1919, 1921),
    ('GRE', 'OTT', 1919, 1922),
    ('ITA', 'OTT', 1919, 1921),
    ('GER', 'POL_I', 1940, 1944),
    ('GER', 'NOR', 1940, 1944),
    ('GER', 'DEN', 1940, 1944),
    ('GER', 'NLD', 1940, 1944),
    ('GER', 'BEL', 1940, 1944),
    ('GER', 'LUX', 1940, 1944),
    ('GER', 'FRA', 1940, 1944),
    ('ITA', 'FRA', 1940, 1943),
    ('GER', 'YUG', 1941, 1944),
    ('ITA', 'YUG', 1941, 1943),
    ('BUL_I', 'YUG', 1941, 1944),
    ('HUN', 'YUG', 1941, 1944),
    ('GER', 'GRE', 1941, 1944),
    ('ITA', 'GRE', 1941, 1943),
    ('BUL_I', 'GRE', 1941, 1944),
    ('GER', 'RUS', 1941, 1944),
    ('ROM', 'RUS', 1941, 1944),
    ('FIN_I', 'RUS', 1941, 1944),
    ('HUN', 'RUS', 1941, 1944),
    ('GER', 'ITA', 1944, 1945),
    ('GER', 'HUN', 1944, 1944),
    ('GER', 'ALB', 1944, 1944),
    ('ITA', 'ALB', 1939, 1943),
    ('GER', 'MON', 1944, 1944),
    ('ITA', 'MON', 1943, 1943),
    ('GER', 'GBR', 1940, 1944),
    ('GBR', 'ISL', 1940, 1941),
    ('GBR', 'DEN', 1940, 1945),
    ('RUS', 'EST', 1940, 1940),
    ('RUS', 'LVA', 1940, 1940),
    ('RUS', 'LTU', 1940, 1940),
    ('GER', 'DOD', 1944, 1944),
]
# Land a power held only during the Second World War (neither before nor after) was annexed without
# lasting recognition; the map shows it crosshatched as annexed.
ANNEXERS = {'GER', 'ITA', 'HUN', 'BUL_I', 'ROM'}
for a, b in [('GER', 'DAN'), ('HUN', 'RUS'), ('BUL_I', 'ROM'), ('GER', 'AUT'), ('HUN', 'AUT')]:
    occ_unit(a, b, annexed=True)
NEW20 |= {k for k in UNITS if k.startswith(('O_', 'A_'))}


# Cliopatria names from 1906 on (used only where OHM and CShapes have nothing); '' = skip
CLIO20 = {'French Africa': 'FRA', "People's Democratic Republic of Algeria": 'ALG_I', 'Republic of Tunisia': 'TUN_I', 'Morocco': 'MOR',
          'Republic of Turkey': 'TUR', 'Ottoman Empire': 'OTT', 'Qajar Dynasty': 'PER', 'Pahlavi Dynasty': 'PER', 'Islamic Republic of Iran': 'PER',
          'Kingdom of Iraq': 'IRQ', 'Iraqi Republic': 'IRQ', 'Republic of Iraq': 'IRQ', 'Syria': 'SYR', 'Republic of Syria': 'SYR',
          'Second Syrian Republic': 'SYR', "Ba'athist Syria": 'SYR', 'United Arab Republic': 'SYR', 'French Mandate for Syria and Lebanon': 'SYR_M',
          'Lebanon': 'LEB', 'Republic of Cyprus': 'CYP_I', 'Turkish Republic of Northern Cyprus': 'NCY', 'Malta': 'MLT',
          'Russian Empire': 'RUS', 'Russian Republic': 'RUS', 'Union of Soviet Socialist Republics': 'RUS', 'Russian Federation': 'RUS',
          'Kazakhstan': 'KAZ', 'Georgia': 'GEO', 'Republic of Armenia': 'ARM', 'Armenia': 'ARM', 'Republic of Azerbaijan': 'AZE',
          'Azerbaijan Democratic Republic': 'AZE', 'German Empire': 'GER', 'Weimar Republic': 'GER', 'Nazi Germany': 'GER',
          'Federal Republic of Germany': 'FRG', 'Federated Republic of Germany': 'GER', 'German Democratic Republic': 'GDR',
          'Kingdom of Italy': 'ITA', 'Republic of Italy': 'ITA', 'French Third Republic': 'FRA', 'French Fourth Republic': 'FRA',
          'French Fifth Republic': 'FRA', 'Vichy France': 'FRA', 'Francoist Spain': 'ESP', 'Kingdom of Spain': 'ESP',
          'Second Spanish Republic': 'ESP', 'Spanish Nationalists': 'ESP', 'Estado Novo': 'POR', 'Portuguese Republic': 'POR', 'Portugal': 'POR',
          'Kingdom of Greece': 'GRE', 'Third Hellenic Republic': 'GRE', 'First Hellenic Republic': 'GRE', 'Greek junta': 'GRE',
          'Kingdom of Bulgaria': 'BUL_I', "People's Republic of Bulgaria": 'BUL_I', 'Republic of Bulgaria': 'BUL_I', 'Principality of Bulgaria': 'BUL_I',
          'Kingdom of Romania': 'ROM', 'Socialist Republic of Romania': 'ROM', 'Romania': 'ROM', 'Hungarian Republic': 'HUN',
          "Hungarian People's Republic": 'HUN', 'Hungary': 'HUN', 'Czechoslovakia': 'CSK', 'Czech Republic': 'CZE', 'Slovakia': 'SVK',
          'Second Polish Republic': 'POL_I', 'Republic of Poland': 'POL_I', 'Yugoslavia': 'YUG', 'Socialist Federal Republic of Yugoslavia': 'YUG',
          'Serbia-Montenegro': 'YUG', 'Serbia': 'SRB_I', 'Montenegro': 'MNE', 'Republic of Croatia': 'HRV', 'Republic of Slovenia': 'SVN',
          'Bosnia and Herzegovina': 'BIH', 'Former Yugoslav Republic of Macedonia': 'MKD', 'Kosovo': 'KOS', 'Albania': 'ALB',
          'Republic of Albania': 'ALB', "People's Socialist Republic of Albania": 'ALB', 'Independent State of Croatia': 'NDH',
          'Republic of Austria': 'AUT', 'Second Republic of Austria': 'AUT', 'Austria-Hungary': 'AUT', 'Swiss Confederation': 'SUI',
          'Kingdom of Belgium': 'BEL', 'Netherlands': 'NLD', 'Luxembourg': 'LUX', 'Denmark': 'DEN', 'Kingdom of Norway': 'NOR',
          'Kingdom of Sweden': 'SWE', 'Republic of Finland': 'FIN_I', 'Kingdom of Iceland': 'ISL', 'Republic of Iceland': 'ISL',
          'Irish Free State': 'IRL', 'Éire': 'IRL', 'Kingdom of Great Britain': 'GBR', 'Republic of Estonia': 'EST', 'Estonia': 'EST',
          'Republic of Latvia': 'LVA', 'Republic of Lithuania': 'LTU', 'Kingdom of Lithuania': 'LTU', 'Republic of Belarus': 'BLR',
          'Ukraine': 'UKR', "Ukrainian People's Republic": 'UKR', 'Republic of Moldova': 'MDA', 'Free City of Danzig': 'DAN',
          'Principality of Monaco': 'MON', 'Kingdom of Monaco': 'MON', 'Principality of Andorra': 'AND', 'Tangier International Zone': 'TNG',
          'Republic of the Rif': 'RIF', 'Cretan State': 'CRT', 'Montenegro ': 'MNE', 'Greenland': 'DEN', 'Denmark-Norway': 'DEN',
          'United Kingdoms of Sweden and Norway': 'SWE', 'Kingdom of Portugal': 'POR', 'Principality of Monaco ': 'MON',
          'Russian-occupied territories': '', 'Chechen Republic': 'RUS', 'Mujahideen': '', 'Polish Armed Forces': '', 'Serbs': '',
          'Hungarian Nationalists': '', 'Yugoslav Partisans': '', 'Spanish Nationalists ': '', 'State of Israel': '', 'Kingdom of Hejaz': '',
          'Arab Federation': 'IRQ', "Arab Socialist Ba'ath Party": '', 'British Africa': '', 'British Colonial Empire': '',
          'British Overseas Territories': 'GBR', 'United States of America': '', 'Republics of the Soviet Union': 'RUS',
          'United Principalities of Moldavia and Wallachia': 'ROM', 'Kingdom of Great Britain ': 'GBR', 'Republic of Cyprus ': 'CYP_I',
          'Swiss Confederation ': 'SUI', 'Kingdom of Norway ': 'NOR'}
