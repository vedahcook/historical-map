# Corrections for the early map (1500-1799), run by assign.py with ERA=early in the same namespace.

# Ottoman vassal states that OHM folds into the Empire: where OHM has the Ottoman Empire and Cliopatria
# the vassal, show the vassal (Moldavia, Transylvania, the Crimean Khanate, Ragusa)
vas = (def_u == KI['OTT']) & np.isin(cl_u, [KI[k] for k in ('MOL', 'WAL', 'CRI', 'TRS', 'UHU', 'RAG')])
fix_multi('ottoman-vassals', np.where(vas, cl_u, NONE).astype(np.int16),
    'OHM draws the Ottoman Empire over its self-governing vassal states in this period. Where Cliopatria has the vassal state, the map shows it (striped, under the Ottomans): Moldavia, Transylvania, the Crimean Khanate and Ragusa.',
    [['Cliopatria (Seshat)', 'https://github.com/Seshat-Global-History-Databank/cliopatria']])
print('corrections', [(f['id'], f['n']) for f in FIX])

# The Low Countries and Franche-Comté: OHM has only the Empire there for much of the period, and Cliopatria
# the whole Habsburg or Spanish monarchy. They were one Habsburg inheritance until 1555, Spanish to 1713
# (the south; Franche-Comté to 1678), then Austrian.
lc = ((x > 2.4) & (x < 7.3) & (y > 49.3) & (y < 53.7)) | ((x > 5.2) & (x < 7.2) & (y > 46.2) & (y < 48.1))
fc = (x > 5.2) & (x < 7.2) & (y > 46.2) & (y < 48.1)
hab = (def_src == 2) & np.isin(def_u, [KI['AUT'], KI['ESP'], KI['HRE']]) & (ohm_pri <= 1) & np.isin(cl_u, [KI['AUT'], KI['ESP']])
fix_multi('habsburg-netherlands', np.where(hab & lc & (YA <= 1555), KI['HNL'], np.where(hab & lc & ~fc & (YA <= 1713), KI['SNL'],
          np.where(hab & fc & (YA <= 1678), KI['FCO'], np.where(hab & lc & ~fc & (YA <= 1794), KI['ANL'], NONE)))).astype(np.int16),
    'In these years OHM draws only the Holy Roman Empire over the Low Countries, and Cliopatria the whole Habsburg or Spanish monarchy. The map shows them as what they were: the Habsburg Netherlands (with Franche-Comté) until Charles V divided his lands in 1555-56, then the Spanish Netherlands and Spanish Franche-Comté (to 1678), then the Austrian Netherlands from 1714.',
    [['Habsburg Netherlands', 'https://en.wikipedia.org/wiki/Habsburg_Netherlands']])

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
print('corrections', [(f['id'], f['n']) for f in FIX])
