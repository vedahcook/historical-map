# The French Revolution deep dive (mockup, October 2026): events, routes, Paris in 1791 and podcast links.
#
#   cd europe-map && python3 deepdive/build_frrev.py            writes deep-frrev.json (needs pyproj)
#   cd europe-map && python3 deepdive/build_frrev.py moments    lists each event's candidate podcast moments
#
# Inputs, all in deepdive/:
#   paris1791-alpage.json      Paris city blocks, the Seine and streets in 1791 (alpage_to_json.py; ODbL, © ALPAGE)
#   frrev-season1-index.json   the segment index of The Rest Is History's French Revolution, season 1 (8 episodes),
#                              built October 12, 2026 (see the Historical Map project doc podcast-links.md)
# Positions are projected to the map's own units (ETRS89-LAEA, EPSG:3035, in km, y pointing down), as export.py does.
# Descriptions are our own words. Pictures come from each item's Wikidata picture (P18) on Wikimedia Commons.
import json, sys, hashlib
from pyproj import Transformer

tr = Transformer.from_crs(4326, 3035, always_xy=True)
def P(lat, lon):
    x, y = tr.transform(lon, lat); return [round(x / 1000, 3), round(-y / 1000, 3)]

# Pictures: file, width, height, author, license (as event-images.json; the md5 folder is added below)
PIC = {
    'tiles': ['Journée des Tuiles (Alexandre Debelle), Musée de la Révolution française - Vizille.jpg', 1094, 836, 'Alexandre Debelle', 'CC BY-SA 4.0'],
    'reveillon': ['Pillage de la Maison Réveillon.png', 1100, 1485, 'Unknown author', 'Public domain'],
    'estates': ['Opening of the Estates General at Versailles on 5th May 1789.jpg', 600, 331, 'Louis Charles Auguste Couder', 'Public domain'],
    'tennis': ['Serment du Jeu de Paume - Jacques-Louis David.jpg', 5004, 3303, 'Jacques-Louis David', 'Public domain'],
    'necker': ['Necker, Jacques, par Boillet, BNF Gallica.jpg', 2757, 3992, 'Boillet', 'Public domain'],
    'desmoulins': ['Camille Desmoulins, Musée Carnavalet.jpg', 2751, 3378, 'Unidentified painter', 'Public domain'],
    'bastille': ['Prise de la Bastille.jpg', 8133, 6181, 'Jean-Pierre Houël', 'Public domain'],
    'march': ["Women's March on Versailles01.jpg", 425, 256, 'Unknown author', 'Public domain'],
    'federation': ['Fête de la Fédération 1790, Musée de la Révolution française - Vizille.jpg', 979, 696, 'Unknown author', 'CC BY-SA 4.0'],
    'varennes': ['Le roi reconnu à chalons par Dumont.jpg', 2480, 2672, 'Unknown author', 'Public domain'],
}
for v in PIC.values(): v.append(hashlib.md5(v[0].replace(' ', '_').encode()).hexdigest()[:2])

# A person: name shown, English Wikipedia title
LOUIS = ['Louis XVI', 'Louis XVI']; MA = ['Marie Antoinette', 'Marie Antoinette']; NECKER = ['Jacques Necker', 'Jacques Necker']
LAF = ['Lafayette', 'Marquis de Lafayette']; BAILLY = ['Jean Sylvain Bailly', 'Jean Sylvain Bailly']

# Views: a box to fit on screen, [lat0, lon0, lat1, lon1]
PARIS = lambda lat, lon, r=1.7: [lat - r / 111, lon - r / 73, lat + r / 111, lon + r / 73]
VERSAILLES_PARIS = [48.79, 2.095, 48.885, 2.40]
EV = [
    dict(id='tiles', d='1788-06-07', t='Day of the Tiles', at='Grenoble', ll=[45.1885, 5.7245], box=[44.9, 1.9, 49.2, 6.2],
         x='When soldiers came to enforce the exile of Grenoble’s parlement, townspeople climbed onto the roofs and pelted them with tiles. The riot led to the Assembly of Vizille, where the province’s three estates met without the king’s leave.',
         w='Day of the Tiles', keys=['e:Q200749', 'e:Q1108912']),
    dict(id='reveillon', d='1789-04-28', t='Réveillon riots', at='Faubourg Saint-Antoine, Paris', ll=[48.8509, 2.3874], box=PARIS(48.8525, 2.375),
         x='A rumor that the wallpaper maker Jean-Baptiste Réveillon wanted wages cut set off a riot in the Faubourg Saint-Antoine. Crowds sacked his house and works; troops fired on them, and dozens or more were killed.',
         ppl=[['Jean-Baptiste Réveillon', 'Jean-Baptiste Réveillon']], w='Réveillon riots', keys=['e:Q1073320']),
    dict(id='estates', d='1789-05-05', t='The Estates General opens', at='Hôtel des Menus-Plaisirs, Versailles', ll=[48.8016, 2.131], box=VERSAILLES_PARIS,
         x='About 1,200 deputies of the clergy, the nobility and the commoners met at Versailles, the first Estates General since 1614. The Third Estate wanted all three orders to sit and vote together.',
         ppl=[LOUIS, NECKER], w='Estates General of 1789', keys=['e:n:opening session of the estates general', 'e:n:opening procession of the estates general']),
    dict(id='tennis', d='1789-06-20', t='Tennis Court Oath', at='Jeu de Paume, Versailles', ll=[48.8013, 2.1239], box=VERSAILLES_PARIS,
         x='Locked out of their hall, the deputies of the new National Assembly met in a nearby indoor tennis court and swore not to part until France had a constitution.',
         ppl=[BAILLY, ['Mirabeau', 'Honoré Gabriel Riqueti, comte de Mirabeau']], w='Tennis Court Oath', keys=['e:Q60022', 'e:n:closure of the salle des menus-plaisirs']),
    dict(id='necker', d='1789-07-11', t='Necker dismissed', at='Palace of Versailles', ll=[48.8047, 2.1203], box=VERSAILLES_PARIS,
         x='Louis XVI sacked his popular finance minister and ordered him to leave France at once. With some 20,000 troops gathering around Paris, many Parisians took it as the start of a crackdown.',
         ppl=[NECKER, LOUIS], w='Jacques Necker', keys=['e:n:dismissal of jacques necker']),
    dict(id='desmoulins', d='1789-07-12', t='Call to arms at the Palais-Royal', at='Palais-Royal, Paris', ll=[48.865, 2.3378], box=PARIS(48.862, 2.337),
         x='As news of Necker’s fall reached the crowds in the Palais-Royal gardens, the young journalist Camille Desmoulins jumped onto a café table and called Parisians to arms. Marchers then paraded wax busts of Necker and the Duke of Orléans.',
         ppl=[['Camille Desmoulins', 'Camille Desmoulins'], ['Duke of Orléans', 'Louis Philippe II, Duke of Orléans']], w='Camille Desmoulins', keys=['e:n:desmoulins\' call to arms at the palais-royal']),
    dict(id='tuileries', d='1789-07-12', t='Cavalry charge at the Tuileries', at='Place Louis XV and the Tuileries Garden', ll=[48.865, 2.3235], box=PARIS(48.862, 2.33),
         x='German-speaking cavalry tried to clear the crowd from Place Louis XV and rode into the Tuileries Garden. French Guards took the crowd’s side, and the royal commander, Besenval, pulled his troops out of Paris.',
         ppl=[['Baron de Besenval', 'Pierre Victor, baron de Besenval de Brünstatt']], w=None, keys=['e:n:royal-allemand charge in the tuileries garden', 'e:n:defection of the french guards']),
    dict(id='invalides', d='1789-07-14', t='Muskets seized at the Invalides', at='Hôtel des Invalides, Paris', ll=[48.8556, 2.3126], box=PARIS(48.856, 2.316),
         x='On the morning of the 14th, a huge crowd broke into the Invalides and carried off muskets and cannon. They had no gunpowder, and the nearest store of it was in the Bastille.',
         w='Les Invalides', keys=['e:n:seizure of arms at the invalides']),
    dict(id='bastille', d='1789-07-14', t='Storming of the Bastille', at='Bastille, Paris', ll=[48.8533, 2.3692], box=PARIS(48.8545, 2.362),
         x='After hours of fighting, the fortress’s small garrison gave up to the crowd and to French Guards who had brought cannon. Only seven prisoners were inside. The governor, de Launay, was killed on the way to the Hôtel de Ville.',
         ppl=[['Bernard-René de Launay', 'Bernard-René Jourdan de Launay'], ['Pierre-Augustin Hulin', 'Pierre-Augustin Hulin']], w='Storming of the Bastille', keys=['e:Q6539']),
    dict(id='kingparis', d='1789-07-17', t='The king comes to Paris', at='Hôtel de Ville, Paris', ll=[48.8564, 2.3522], box=PARIS(48.857, 2.345),
         x='Three days after the Bastille fell, Louis XVI rode into Paris. At the Hôtel de Ville the new mayor, Bailly, gave him the new cockade, and he put it in his hat.',
         ppl=[LOUIS, BAILLY, LAF], w='Cockade of France', keys=['e:n:louis xvi\'s visit to paris', 'e:n:louis xvi receives the tricolour cockade at the hôtel de ville']),
    dict(id='foulon', d='1789-07-22', t='Foullon and Bertier killed', at='Place de Grève, Paris', ll=[48.8559, 2.3514], box=PARIS(48.857, 2.345),
         x='A crowd seized Joseph Foullon, a royal official said to have told the hungry to eat hay, and his son-in-law Bertier de Sauvigny, the intendant of Paris. Both were killed outside the Hôtel de Ville.',
         ppl=[['Joseph Foullon de Doué', 'Joseph Foullon de Doué'], ['Bertier de Sauvigny', 'Louis Bénigne François Bertier de Sauvigny']], w=None, keys=['e:n:lynching of foullon and bertier de sauvigny']),
    dict(id='august4', d='1789-08-04', t='The Night of 4 August', at='Hôtel des Menus-Plaisirs, Versailles', ll=[48.8016, 2.131], box=VERSAILLES_PARIS,
         x='Alarmed by peasant risings across the countryside, the National Assembly voted away feudal dues, the nobles’ privileges and the tithe in a single night.',
         ppl=[['Vicomte de Noailles', 'Louis Marie de Noailles']], w='Abolition of feudalism in France', keys=['e:Q2622002']),
    dict(id='march', d='1789-10-05', t='Women’s March on Versailles', at='From the Hôtel de Ville to Versailles', ll=[48.8047, 2.1203], box=VERSAILLES_PARIS,
         route=[[48.8564, 2.3522], [48.8656, 2.3212], [48.864, 2.301], [48.856, 2.28], [48.8395, 2.258], [48.825, 2.229], [48.823, 2.21], [48.809, 2.187], [48.8, 2.17], [48.803, 2.135], [48.8047, 2.1203]],
         x='Thousands of Paris market women, angry at the price of bread, walked twelve miles in the rain to Versailles, with Lafayette and the National Guard behind them. Before dawn the next day, part of the crowd broke into the palace.',
         ppl=[LAF, MA, LOUIS], w='Women\'s March on Versailles', keys=['e:Q1151917']),
    dict(id='return', d='1789-10-06', t='The royal family taken to Paris', at='Versailles to the Tuileries Palace', ll=[48.8622, 2.3325], box=VERSAILLES_PARIS,
         route=[[48.8047, 2.1203], [48.803, 2.135], [48.8, 2.17], [48.809, 2.187], [48.823, 2.21], [48.825, 2.229], [48.8395, 2.258], [48.856, 2.28], [48.864, 2.301], [48.8656, 2.3212], [48.8622, 2.3325]],
         x='The crowd made the king, the queen and their children leave Versailles for Paris, escorted by National Guards and marchers. They moved into the Tuileries Palace, and the Assembly soon followed them to Paris.',
         ppl=[LOUIS, MA, LAF], w='Tuileries Palace', keys=['e:Q1151917', 'e:n:transfer of the national constituent assembly to paris']),
    dict(id='federation', d='1790-07-14', t='Festival of the Federation', at='Champ de Mars, Paris', ll=[48.8556, 2.2983], box=PARIS(48.857, 2.305, 2.0),
         x='On the first anniversary of the Bastille, delegates from all over France met on the Champ de Mars, which Parisians had dug into a vast arena by hand. Lafayette led an oath to the nation, the law and the king.',
         ppl=[LAF, ['Talleyrand', 'Charles Maurice de Talleyrand-Périgord']], w='Fête de la Fédération', keys=['e:Q143866']),
    dict(id='varennes', d='1791-06-20/1791-06-22', t='Flight to Varennes', at='The Tuileries to Varennes-en-Argonne', ll=[49.2269, 5.035], box=[48.35, 2.2, 49.5, 5.3],
         route=[[48.8622, 2.3325], [48.8838, 2.3697], [48.9022, 2.4828], [48.95, 2.7], [48.96, 2.878], [48.949, 3.127], [48.872, 3.541], [48.89, 3.86], [48.9575, 4.365], [49.0833, 4.9], [49.106, 5.07], [49.2269, 5.035]],
         x='The royal family slipped out of the Tuileries at night in disguise, heading for loyal troops at Montmédy. The postmaster Drouet recognized the king at Sainte-Menehould, and the family was stopped at Varennes and taken back to Paris.',
         ppl=[LOUIS, MA, ['Axel von Fersen', 'Axel von Fersen the Younger'], ['Jean-Baptiste Drouet', 'Jean-Baptiste Drouet (revolutionary)']], w='Flight to Varennes', keys=['e:Q1192894']),
]

# the short name beside an event's marker on the map
LB = {'tiles': 'Grenoble', 'reveillon': 'Réveillon’s works', 'estates': 'Hôtel des Menus-Plaisirs', 'tennis': 'Jeu de Paume', 'necker': 'Palace of Versailles',
      'desmoulins': 'Palais-Royal', 'tuileries': 'Tuileries Garden', 'invalides': 'Invalides', 'bastille': 'Bastille', 'kingparis': 'Hôtel de Ville',
      'foulon': 'Place de Grève', 'august4': 'Hôtel des Menus-Plaisirs', 'march': 'Versailles', 'return': 'Tuileries Palace', 'federation': 'Champ de Mars', 'varennes': 'Varennes'}
IX = json.load(open('deepdive/frrev-season1-index.json'))
EPS = IX['episodes']
def moments(e):
    seen, out = set(), []
    for k in e['keys']:
        r = IX['entities'].get(k)
        if not r: print('  no index entry for', k, file=sys.stderr); continue
        for a, b in r['m']:
            if (a, b) not in seen: seen.add((a, b)); out.append((a, b))
    return sorted(out)

if len(sys.argv) > 1 and sys.argv[1] == 'moments':
    for e in EV:
        print(e['id'], e['t'])
        for a, b in moments(e):
            s = EPS[a]['g'][b]; print(f"   ep{a + 1} {s['s'] // 60}:{s['s'] % 60:02d}  {s.get('w')}  {s['u']}")
    sys.exit()

PICK = json.load(open('deepdive/frrev-moments.json')) if __import__('os').path.exists('deepdive/frrev-moments.json') else {}
events = []
for i, e in enumerate(EV):
    ms = moments(e)
    if e['id'] in PICK: ms = [m for m in ms if [m[0], EPS[m[0]]['g'][m[1]]['s']] in PICK[e['id']]]
    ms = ms[:4]
    lat0, lon0, lat1, lon1 = e['box']; x0, y1 = P(lat0, lon0); x1, y0 = P(lat1, lon1)
    events.append({
        'id': e['id'], 'd': e['d'], 't': e['t'], 'at': e['at'], 'lb': LB[e['id']], 'p': P(*e['ll']), 'box': [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)],
        'x': e['x'], 'ppl': e.get('ppl', []), 'w': e.get('w'), 'pic': PIC.get(e['id']),
        'route': [P(*q) for q in e['route']] if e.get('route') else None,
        'm': [[a + 1, EPS[a]['id'], EPS[a]['g'][b]['s'], EPS[a]['g'][b]['u']] for a, b in ms],
    })
A = json.load(open('deepdive/paris1791-alpage.json'))
proj_ring = lambda r: [c for x, y in r for c in P(y, x)]       # flat [x0, y0, x1, y1, ...] in map km
paris = {'blocks': [[proj_ring(r) for r in poly] for poly in A['blocks']], 'water': [[proj_ring(r) for r in poly] for poly in A['water']]}
eps = [{'n': e['n'], 'id': e['id'], 'pt': e['pt'], 'yt': e['yt']} for e in EPS]
out = {'title': 'The French Revolution', 'span': '1788–1791', 'events': events, 'episodes': eps, 'paris': paris}
json.dump(out, open('deep-frrev.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(events), 'events,', sum(len(e['m']) for e in events), 'podcast moments,', len(paris['blocks']), 'blocks; deep-frrev.json',
      round(len(json.dumps(out, ensure_ascii=False, separators=(',', ':'))) / 1024), 'KB')
