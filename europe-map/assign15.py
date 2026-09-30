# Corrections for the early map (1500-1799), run by assign.py with ERA=early in the same namespace.

# Ottoman vassal states that OHM folds into the Empire: where OHM has the Ottoman Empire and Cliopatria
# the vassal, show the vassal (Moldavia, Transylvania, the Crimean Khanate, Ragusa)
vas = (def_u == KI['OTT']) & np.isin(cl_u, [KI[k] for k in ('MOL', 'WAL', 'CRI', 'TRS', 'UHU', 'RAG')])
fix_multi('ottoman-vassals', np.where(vas, cl_u, NONE).astype(np.int16),
    'OHM draws the Ottoman Empire over its self-governing vassal states in this period. Where Cliopatria has the vassal state, the map shows it (striped, under the Ottomans): Moldavia, Transylvania, the Crimean Khanate and Ragusa.',
    [['Cliopatria (Seshat)', 'https://github.com/Seshat-Global-History-Databank/cliopatria']])

# The Low Countries and Franche-Comté: OHM has only the Empire there for much of the period, and Cliopatria
# the whole Habsburg or Spanish monarchy. They were one Habsburg inheritance until 1555, Spanish to 1713
# (the south; Franche-Comté to 1678), then Austrian.
lc = ((x > 2.4) & (x < 7.3) & (y > 49.3) & (y < 53.7)) | ((x > 5.2) & (x < 7.2) & (y > 46.2) & (y < 48.1))
fc = (x > 5.2) & (x < 7.2) & (y > 46.2) & (y < 48.1)
hab = ((def_src == 2) | ((def_src == 0) & (def_u == KI['HRE']))) & np.isin(def_u, [KI['AUT'], KI['ESP'], KI['HRE']]) & (ohm_pri <= 1) & np.isin(cl_u, [KI['AUT'], KI['ESP']])
fix_multi('habsburg-netherlands', np.where(hab & lc & (YA <= 1555), KI['HNL'], np.where(hab & lc & ~fc & (YA <= 1713), KI['SNL'],
          np.where(hab & fc & (YA <= 1678), KI['FCO'], np.where(hab & lc & ~fc & (YA <= 1794), KI['ANL'], NONE)))).astype(np.int16),
    'In these years OHM draws only the Holy Roman Empire over the Low Countries, and Cliopatria the whole Habsburg or Spanish monarchy. The map shows them as what they were: the Habsburg Netherlands (with Franche-Comté) until Charles V divided his lands in 1555-56, then the Spanish Netherlands and Spanish Franche-Comté (to 1678), then the Austrian Netherlands from 1714.',
    [['Habsburg Netherlands', 'https://en.wikipedia.org/wiki/Habsburg_Netherlands']])

fix('franche-comte', 'FCO', fc & (def_u == KI['SNL']) & (YA <= 1678),
    'OHM counts Franche-Comté with the Spanish Netherlands, as both belonged to the Burgundian Circle of the Empire. It was a separate Spanish Habsburg province until France took it in 1674-78.',
    [['Free County of Burgundy', 'https://en.wikipedia.org/wiki/Free_County_of_Burgundy']])

# Cliopatria counts the Austrian lands as part of Charles V's Spanish Empire while he ruled both; north of the Alps
# and outside the Low Countries, a Cliopatria "Spain" is the Austrian Habsburg lands
aus = (def_src == 2) & (def_u == KI['ESP']) & (x > 9.0) & (y > 45.9) & ~lc
fix('habsburg-austria', 'AUT', aus,
    'Cliopatria counts the Austrian Habsburg lands as part of the Spanish Empire while Charles V ruled both. Charles handed Austria to his brother Ferdinand in 1521-22, so the map shows these lands as the Habsburg Monarchy.',
    [['Ferdinand I', 'https://en.wikipedia.org/wiki/Ferdinand_I,_Holy_Roman_Emperor']])

# Poland and Lithuania before the Union of Lublin (1569): Cliopatria draws the two Jagiellonian states as one;
# east of the Crown's voivodeships the land was Lithuanian
lit = (def_src == 2) & (def_u == KI['PLK']) & (x > 23.0) & (YA <= 1568)
fix('lithuania-1569', 'LIT', lit,
    'Cliopatria draws Poland and Lithuania as one Jagiellonian state before the Union of Lublin (1569). OHM has the Crown of Poland’s voivodeships; east of them, the land belonged to the Grand Duchy of Lithuania, including Podlasie, Volhynia and Kyiv, which passed to the Crown in 1569.',
    [['Union of Lublin', 'https://en.wikipedia.org/wiki/Union_of_Lublin']])

# Cliopatria's Jagiellonian state runs to 1571; from the Union of Lublin (1569) it is the Commonwealth
fix('commonwealth-1569', 'PLC', (def_src == 2) & (def_u == KI['PLK']) & (YA >= 1569),
    'Cliopatria’s record of the Jagiellonian kingdom runs to 1571. From the Union of Lublin in 1569, Poland and Lithuania formed one Commonwealth.',
    [['Union of Lublin', 'https://en.wikipedia.org/wiki/Union_of_Lublin']])

# Short overlaps where a source keeps a state a year or three after it ended
fix('aq-qoyunlu-1508', 'PER', (def_u == KI['AQQ']) & (YA > 1508),
    'Cliopatria keeps the Aq Qoyunlu until 1511. The Safavids of Iran had taken the last of their lands by 1508.',
    [['Aq Qoyunlu', 'https://en.wikipedia.org/wiki/Aq_Qoyunlu']])
fix('hungary-1527', 'TRS', (def_src == 2) & (def_u == KI['HUK']) & (YA >= 1527),
    'Cliopatria keeps a Kingdom of Hungary after the Battle of Mohács (1526). Its outline is the part held by John Zápolya, the rival of the Habsburg king Ferdinand, whose realm became the Principality of Transylvania; the rest of Hungary was Habsburg or Ottoman.',
    [['Eastern Hungarian Kingdom', 'https://en.wikipedia.org/wiki/Eastern_Hungarian_Kingdom']])
fix('bohemia-1526', 'AUT', (def_u == KI['BOK']) & (YA >= 1527),
    'Cliopatria keeps a separate Kingdom of Bohemia until 1528. Ferdinand of Habsburg was elected King of Bohemia in October 1526, after King Louis II died at Mohács.',
    [['Kingdom of Bohemia', 'https://en.wikipedia.org/wiki/Kingdom_of_Bohemia']])
fix('milan-1535', 'MIL_S', (def_u == KI['MLS']) & (YA >= 1536),
    'Cliopatria keeps the Sforza Duchy of Milan until 1539. The last Sforza duke died in November 1535, and Emperor Charles V took the duchy.',
    [['Duchy of Milan', 'https://en.wikipedia.org/wiki/Duchy_of_Milan']])
fix('lorraine-1766', 'FRA', (def_u == KI['LOR']) & (YA >= 1767),
    'A source keeps Lorraine separate until 1768. It passed to France when Duke Stanisław Leszczyński died in February 1766.',
    [['Duchy of Lorraine', 'https://en.wikipedia.org/wiki/Duchy_of_Lorraine']])
fix('luxembourg-1795', 'FRA', (def_u == KI['LUX']) & (YA >= 1795),
    'OHM shows the Duchy of Luxembourg on its own from 1795. French troops took the fortress in June 1795, and France annexed the duchy that October.',
    [['Siege of Luxembourg (1794-95)', 'https://en.wikipedia.org/wiki/Siege_of_Luxembourg_(1794%E2%80%931795)']])
fix('commonwealth-1649', 'CMW', (np.isin(def_u, [KI['ENG'], KI['IRL'], KI['ICC']]) & (YA >= 1652) & (YA <= 1659))
    | ((def_u == KI['ENG']) & (YA == 1649) & (y > 49.8) & ~((x > -4.9) & (x < -4.3) & (y > 54.0) & (y < 54.45))),
    'OHM’s record of the English republic starts in August 1649, and some sources keep parts of Ireland apart in 1652-53. England became a republic in May 1649, after the execution of Charles I; by mid-1652 Parliament’s army had taken nearly all of Ireland, and Ireland and Scotland were then ruled by the Commonwealth.',
    [['Commonwealth of England', 'https://en.wikipedia.org/wiki/Commonwealth_of_England'], ['Cromwellian conquest of Ireland', 'https://en.wikipedia.org/wiki/Cromwellian_conquest_of_Ireland']])

# Places the sources get wrong or leave empty, checked in spot_checks15.py
inbox = lambda x0, y0, x1, y1: (x > x0) & (x < x1) & (y > y0) & (y < y1)
free = def_u == NONE
men = inbox(3.78, 39.78, 4.35, 40.1) & free
fix_multi('menorca', np.where(men & (YA >= 1708) & (YA <= 1755), KI['GBR'], np.where(men & (YA >= 1756) & (YA <= 1762), KI['FRA'],
          np.where(men & (YA >= 1763) & (YA <= 1781), KI['GBR'], NONE))).astype(np.int16),
    'The sources leave Menorca blank for much of the 1700s. Britain took it in 1708 and kept it by the Treaty of Utrecht; France held it from 1756 to 1763, and Spain retook it in 1781-82.',
    [['History of Menorca', 'https://en.wikipedia.org/wiki/History_of_Menorca']])
fix('ragusa-coast', 'RAG', inbox(17.9, 42.55, 18.4, 42.8) & free,
    'OHM leaves part of the Republic of Ragusa blank before 1700. Its coastal lands around Dubrovnik are shown as Ragusan.',
    [['Republic of Ragusa', 'https://en.wikipedia.org/wiki/Republic_of_Ragusa']])
fix('ceuta-1640', 'ESP', inbox(-5.4, 35.85, -5.25, 35.93) & free & (YA >= 1641),
    'OHM leaves Ceuta blank after 1640. When Portugal broke away from Spain in 1640, Ceuta stayed with Spain, which Portugal accepted in 1668.',
    [['Ceuta', 'https://en.wikipedia.org/wiki/Ceuta#History']])
fix('oran-spanish', 'ESP', inbox(-1.3, 35.45, -0.2, 36.0) & (def_u == KI['ALG']) & (cl_u == KI['ESP']) & ((YA <= 1707) | ((YA >= 1732) & (YA <= 1791))),
    'OHM puts Oran under Algiers throughout. Spain held Oran and Mers-el-Kébir from 1509 to 1708 and again from 1732 to 1792, as Cliopatria shows.',
    [['Spanish Oran', 'https://en.wikipedia.org/wiki/Spanish_Oran']])
fix('calais-1558', 'FRA', inbox(1.4, 50.7, 2.3, 51.1) & (def_u == KI['ENG']) & (YA >= 1558),
    'Cliopatria keeps the Pale of Calais English after 1558. France took Calais in January 1558.',
    [['Siege of Calais (1558)', 'https://en.wikipedia.org/wiki/Siege_of_Calais_(1558)']])
fix('savoy-nice-1792', 'FRA', (inbox(5.6, 45.05, 7.0, 46.45) | inbox(6.85, 43.5, 7.75, 44.25)) & (def_u == KI['SAR']) & (YA >= 1793),
    'OHM keeps Savoy and Nice with the Kingdom of Sardinia until 1799. Revolutionary France took both in 1792 and annexed Savoy that November and Nice in January 1793.',
    [['County of Nice', 'https://en.wikipedia.org/wiki/County_of_Nice'], ['Duchy of Savoy', 'https://en.wikipedia.org/wiki/Duchy_of_Savoy']])
fix('ferrara-este', 'MOD', inbox(11.35, 44.62, 12.4, 45.0) & (def_u == KI['PAP']) & (YA <= 1597),
    'The sources put Ferrara in the Papal States throughout. It was ruled by the Este dukes until 1598, when the pope took it back after the main Este line died out.',
    [['Duchy of Ferrara', 'https://en.wikipedia.org/wiki/Duchy_of_Ferrara']])
fix('serbia-1718', 'AUT', inbox(16.0, 43.4, 25.0, 46.0) & np.isin(def_u, [KI['OTT'], KI['WAL']]) & (cl_u == KI['AUT']) & (YA >= 1718) & (YA <= 1739),
    'OHM keeps northern Serbia and Oltenia Ottoman or Wallachian in 1718-39. The Treaty of Passarowitz (1718) gave them to the Habsburgs, who lost them again by the Treaty of Belgrade (1739); Cliopatria shows this.',
    [['Treaty of Passarowitz', 'https://en.wikipedia.org/wiki/Treaty_of_Passarowitz']])
print('corrections', [(f['id'], f['n']) for f in FIX])
