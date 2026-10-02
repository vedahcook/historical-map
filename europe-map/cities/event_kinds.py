"""Kinds of city events for the map's icons, as Wikidata classes: an event belongs to a kind when one of its classes
(P31) is, or is a subclass (P279*) of, one of the kind's root classes. Kinds are tried in this order; DROP comes
after the others (an Olympic Games edition is a kind of sports event, but is kept as culture). Events of no kind are
left out (most are buildings, stations, concerts and the like)."""
KINDS = [
    ('war', 'Battle, siege, bombing', ['Q178561', 'Q188055', 'Q1261499', 'Q645883', 'Q2001676', 'Q4688003', 'Q678146', 'Q19841484', 'Q192623',
                                      'Q1361229', 'Q476807', 'Q24238946', 'Q350604', 'Q198', 'Q2380335', 'Q111034471']),
    ('violence', 'Massacre, assassination, attack', ['Q3199915', 'Q750215', 'Q2223653', 'Q891854', 'Q18493502', 'Q21480300', 'Q177716', 'Q135010',
                                                    'Q41397', 'Q3882219', 'Q1139665', 'Q2583015', 'Q1371150']),
    ('uprising', 'Uprising, revolution, protest', ['Q124734', 'Q6107280', 'Q1323212', 'Q10931', 'Q45382', 'Q25906438', 'Q124757', 'Q3588250',
                                                  'Q273120', 'Q175331', 'Q686984', 'Q49776', 'Q1464916']),
    ('treaty', 'Treaty, congress, conference', ['Q131569', 'Q625298', 'Q6934728', 'Q9557810', 'Q107706', 'Q1412901', 'Q1127126', 'Q7157512',
                                               'Q18564543', 'Q1072326', 'Q321839', 'Q2495862']),
    ('religion', 'Church council, papal election', ['Q51645', 'Q10551516', 'Q111161', 'Q29102902', 'Q186431', 'Q1123131']),
    ('crown', 'Coronation, royal event', ['Q209715']),
    ('fire', 'Great fire', ['Q838718', 'Q168983', 'Q7625093']),
    ('disaster', 'Earthquake, flood, epidemic', ['Q7944', 'Q8068', 'Q8065', 'Q1516910', 'Q3241045', 'Q2165983', 'Q68800046', 'Q12184', 'Q44512']),
    ('culture', 'World fair, Olympic Games', ['Q172754', 'Q135976384', 'Q137592217']),
    ('other', 'Trial, crisis, scandal, declaration', ['Q8016240', 'Q1265353', 'Q5791104', 'Q3002772', 'Q934744', 'Q62662439', 'Q12772819',
                                                      'Q22702', 'Q2140711', 'Q7755', 'Q1464916']),
]
DROP = ['Q27020041', 'Q114609228', 'Q16510064', 'Q13406554', 'Q18536594', 'Q26132862', 'Q51031626', 'Q1079023', 'Q500834', 'Q1366722', 'Q878123',
        'Q2683596', 'Q4504495', 'Q618779', 'Q27787439', 'Q41582469', 'Q132241', 'Q27968043', 'Q110288240', 'Q62391930', 'Q5398426', 'Q15416',
        'Q3890208', 'Q13406463', 'Q17633526', 'Q79007', 'Q174782', 'Q16970', 'Q24354', 'Q1248784', 'Q46622', 'Q1426271', 'Q2015628', 'Q1154710',
        'Q43229', 'Q4830453', 'Q15238777', 'Q20127274', 'Q4', 'Q744913', 'Q1078765', 'Q3002150', 'Q171558', 'Q1309431', 'Q132821', 'Q81672',
        'Q149086', 'Q16738832', 'Q6813020', 'Q3305213', 'Q12561', 'Q22947792', 'Q2288051', 'Q464980', 'Q667276', 'Q57305', 'Q868557',
        'Q106594095', 'Q35718073', 'Q16523578', 'Q48004378', 'Q11483816', 'Q15275719', 'Q27968055', 'Q167170', 'Q3918', 'Q38723', 'Q1407393',
        'Q930164', 'Q473853', 'Q3307578', 'Q56061', 'Q131621892', 'Q45400320', 'Q12708896', 'Q200538']
ROOTS = sorted({q for _, _, qs in KINDS for q in qs} | set(DROP))
if __name__ == '__main__':
    print(' '.join(ROOTS)); print(len(ROOTS))
