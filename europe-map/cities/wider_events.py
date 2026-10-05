# Wider events: wars, epidemics and disasters that struck a whole country or region, matched to the cities they
# touched (by today's country and position). The city card's Population tab names them alongside the city's own
# Wikidata events when a city's population fell in their years, since Wikidata rarely ties them to single cities
# (Cologne has no "Black Death" event, for example). Written October 5, 2026; years, areas and articles checked
# against Wikipedia by a separate reviewer (see the Project doc claude/city-views-pilot.md).
#   python3 cities/wider_events.py        (in europe-map/; writes wider-events.json)
import json

# name shown, English Wikipedia title, Wikidata id, first year, last year, where (a test on country, longitude, latitude)
DE, CZ, AT, PL, FR = 'Germany (Federal Republic)', 'Czech Republic (Czechia)', 'Republic of Austria', 'Republic of Poland', 'French Fifth Republic'
BE, NL, LU, IT, ES = 'Kingdom of Belgium', 'Kingdom of the Netherlands', 'Grand Duchy of Luxembourg', 'Italian Republic', 'Kingdom of Spain'
SOVIET = {'Russian Federation', 'Ukraine', 'Russian-occupied Ukraine', 'Republic of Belarus', 'Georgia', 'Republic of Armenia',
          'Republic of Azerbaijan', 'Abkhazia', 'South Ossetia', 'Transnistria'}

def silesia_pomerania(lon, lat):     # the parts of today's Poland that were in the Holy Roman Empire in 1618
    return (lat < 51.45 and lon < 19.05) or (51.45 <= lat < 52.5 and lon < 16.3) or (52.5 <= lat < 53.6 and lon < 16.3) or (lat >= 53.6 and lon < 17.4)

def liguria(lon, lat): return (lat < 44.45 and 7.9 <= lon < 10.0) or (lat < 44.0 and lon < 7.9)     # the Genoese coast
def marche(lon, lat): return lon >= 12.6 and lat < 44.0
def islands(lon, lat): return (lat < 38.4 and 12.3 < lon < 15.6) or (lon < 9.9 and lat < 41.3)     # Sicily, Sardinia: never invaded

EVENTS = [
    ('Black Death', 'Black Death', 'Q42005', 1346, 1353,       # not in Flanders until about 1400; little known for Iran and the Caucasus
        lambda c, x, y: c not in ('Iran', 'Georgia', 'Republic of Armenia', 'Republic of Azerbaijan', 'Abkhazia', 'South Ossetia', 'Republic of Finland',
                                  'Republic of Iceland') and not (c == BE and x < 4.1)),
    ('French Wars of Religion', 'French Wars of Religion', 'Q673175', 1562, 1598,      # France as it was then: not Flanders, Roussillon, Savoy, Bresse
        lambda c, x, y: c == FR and x < 6.0 and not (y >= 50.0 and x >= 2.0) and not (y < 42.95 and x >= 2.2) and not (x >= 5.8 and 45.4 <= y < 46.0)
                        and not (x >= 5.1 and 46.0 <= y < 46.4)),
    ("Eighty Years' War", "Eighty Years' War", 'Q164432', 1568, 1648, lambda c, x, y: (c in (BE, NL, LU) or (c == FR and y >= 50.0 and x >= 2.0)) and not (c == BE and 5.1 <= x < 5.95 and 50.4 <= y < 51.1)),   # (Liège stayed out)
    ('Expulsion of the Moriscos', 'Expulsion of the Moriscos', 'Q2345573', 1609, 1614,
        lambda c, x, y: c == ES and x >= -2.0 and y < 42.9 and not (x > 0.35 and y > 40.5) and not (x > 1.0 and y < 40.2)),
    ("Thirty Years' War", "Thirty Years' War", 'Q2487', 1618, 1648,
        lambda c, x, y: c in (DE, CZ, AT) or (c == FR and x >= 5.1 and 46.8 <= y <= 49.6) or (c == PL and silesia_pomerania(x, y))),
    ('Italian plague', '1629–1631 Italian plague', 'Q3307987', 1629, 1631,
        lambda c, x, y: c == IT and 43.5 <= y < 46.3 and not liguria(x, y) and not marche(x, y) and not (x >= 13.5 and y >= 45.6)),   # (not Habsburg Trieste, Gorizia, Tyrol)
    ('Sicily earthquake', '1693 Sicily earthquake', 'Q2706283', 1693, 1693, lambda c, x, y: c == IT and 36.6 <= y <= 37.7 and x >= 14.45),
    ('French Revolution', 'French Revolution', 'Q6534', 1789, 1799, lambda c, x, y: c == FR and x < 8.5),
    ('French Revolutionary Wars', 'French Revolutionary Wars', 'Q207318', 1792, 1802,
        lambda c, x, y: (c in (BE, NL, LU, IT, 'Switzerland', 'Malta') or (c == DE and (x < 9.0 or y < 49.0))) and not islands(x, y)),
    ('Napoleonic Wars', 'Napoleonic Wars', 'Q78994', 1803, 1815,
        lambda c, x, y: c in (FR, BE, NL, LU, IT, DE, AT, CZ, PL, 'Switzerland', 'Slovak Republic', 'Republic of Hungary', 'Republic of Croatia',
                              'Republic of Slovenia', 'Kingdom of Denmark') and not islands(x, y)),
    ('Peninsular War', 'Peninsular War', 'Q152499', 1808, 1814,      # (not the Balearics, Ceuta or Melilla)
        lambda c, x, y: c in (ES, 'Portuguese Republic') and not (x > 1.2 and y < 40.2) and y >= 35.95),
    ('French invasion of Russia', 'French invasion of Russia', 'Q179250', 1812, 1812,
        lambda c, x, y: c in ('Republic of Lithuania', 'Republic of Belarus') or (c == 'Republic of Latvia' and y < 57.2) or
                        (c == 'Russian Federation' and x < 38.0 and 53.5 <= y <= 56.5)),
    ('Great Famine in Ireland', 'Great Famine (Ireland)', 'Q188371', 1845, 1852, lambda c, x, y: c == 'Ireland' or (c == 'United Kingdom' and x < -5.4 and y > 54.0)),
    ('World War I', 'World War I', 'Q361', 1914, 1918,
        lambda c, x, y: c not in (ES, NL, 'Switzerland', 'Kingdom of Denmark', 'Kingdom of Norway', 'Kingdom of Sweden', 'Principality of Andorra',
                                  'Kingdom of Morocco', 'Algeria', 'Republic of Tunisia', 'Republic of Iceland', 'Malta', 'Republic of Cyprus')),
    ('Russian Civil War', 'Russian Civil War', 'Q79911', 1917, 1922, lambda c, x, y: c in SOVIET and (c != 'Russian Federation' or x > 23.0)),   # (Kaliningrad was German)
    ('Spanish Civil War', 'Spanish Civil War', 'Q10859', 1936, 1939, lambda c, x, y: c == ES),
    ('World War II', 'World War II', 'Q362', 1939, 1945,
        lambda c, x, y: c not in (ES, 'Portuguese Republic', 'Kingdom of Sweden', 'Switzerland', 'Ireland', 'Republic of Turkey', 'Principality of Andorra',
                                  'Iran', 'Iraq', 'Syria', 'Lebanon', 'Kingdom of Morocco', 'Algeria', 'Republic of Iceland', 'Georgia',
                                  'Republic of Armenia', 'Republic of Azerbaijan', 'South Ossetia', 'Abkhazia')),
    ('Armenian earthquake', '1988 Armenian earthquake', 'Q815567', 1988, 1988, lambda c, x, y: c == 'Republic of Armenia' and y >= 40.6 and x <= 44.6),
]

if __name__ == '__main__':
    rows = [l.rstrip('\n').split('|') for l in open('cities.txt') if l.strip() and not l.startswith('#')]
    cc = json.load(open('cities/city_country.json'))
    assert len(rows) == len(cc) and all(r[0] == c[0] for r, c in zip(rows, cc))
    out = []
    for n, t, q, a, b, where in EVENTS:
        ids = [i for i, (r, c) in enumerate(zip(rows, cc)) if where(c[1], float(r[1]), float(r[2]))]
        rest = [i for i in range(len(rows)) if i not in set(ids)]
        out.append([n, t if t != n else '', q, a, b, 'all' if not rest else {'not': rest} if len(rest) < len(ids) else ids])
        print(f'{n}: {a}–{b}, {len(ids)} cities')
    json.dump({'source': 'Hand-made list of wars, epidemics and disasters that struck whole regions, October 5, 2026 (cities/wider_events.py); '
                         'each row: name, Wikipedia title if not the name, Wikidata id, first and last year, and the cities: indexes into the city list, '
                         '"all", or {"not": the cities left out}',
               'ev': out}, open('wider-events.json', 'w'), ensure_ascii=False, separators=(',', ':'))
