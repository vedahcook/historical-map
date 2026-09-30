"""City-proper populations from the UN Statistics Division (Demographic Yearbook city table, via
github.com/datasets/population-city, file unsd-citypopulation-year-both.csv) for the cities in ../cities.txt.
Writes un_cities.txt: name|year:pop;... Census figures win over estimates for the same year."""
import csv, re, sys, unicodedata
CT = sys.argv[1] if len(sys.argv) > 1 else '../cities.txt'
FOLD = str.maketrans({'ł': 'l', 'Ł': 'L', 'ı': 'i', 'İ': 'I', 'ø': 'o', 'Ø': 'O', 'æ': 'ae', 'ß': 'ss', 'đ': 'd', 'ş': 's', 'ğ': 'g'})
norm = lambda s: re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', s.translate(FOLD)).encode('ascii', 'ignore').decode().lower())
# the UN's names where they differ from the map's (map name -> UN name)
ALIAS = {'Warsaw': 'Warszawa', 'Athens': 'Athinai', 'Piraeus': 'Pireas', 'Antwerp': 'Antwerpen (Anvers)', 'Ghent': 'Gent (Gand)',
         'Brussels': 'Bruxelles (Brussel)', 'Liège': 'Liège (Luik)', 'Heraklion': 'Iraclion', 'Patras': 'Patrai', 'Donetsk': "Donets'k",
         'Horlivka': 'Gorlivka', 'Lutsk': "Luts'k", 'Mykolaiv': 'Nikolaev', 'Kryvyi Rih': 'Krivoy Rog', 'Luhansk': 'Lugansk',
         'Makiivka': 'Makijivka', 'Khmelnytskyi': 'Khmelnitsky (Hmilnyk)', 'Kremenchuk': 'Krementchug', 'Moscow': 'Moskva',
         'Rome': 'Roma', 'Milan': 'Milano', 'Naples': 'Napoli', 'Turin': 'Torino', 'Florence': 'Firenze',
         'Venice': 'Venezia', 'Genoa': 'Genova', 'Munich': 'München', 'Cologne': 'Köln', 'Nuremberg': 'Nürnberg', 'Vienna': 'Wien',
         'Prague': 'Praha', 'Lisbon': 'Lisboa', 'Copenhagen': 'København', 'Gothenburg': 'Göteborg', 'Belgrade': 'Beograd',
         'Bucharest': 'Bucuresti', 'Seville': 'Sevilla', 'The Hague': "'s-Gravenhage", 'Kyiv': 'Kyiv', 'Odessa': 'Odessa',
         'Chișinău': 'Chisinau', 'Tbilisi': 'Tbilisi', 'Hanover': 'Hannover', 'Brunswick': 'Braunschweig', 'Nizhny Novgorod': 'Nizhniy Novgorod', 'Frankfurt': 'Frankfurt am Main', 'Geneva': 'Genève', 'Tsaritsyn': 'Volgograd',
         'Rostov-on-Don': 'Rostov-na-Donu', 'Padua': 'Padova', 'Brest-Litovsk': 'Brest', 'Freiburg': 'Freiburg im Breisgau', 'Babruysk': 'Bobruisk',
         'Zaporizhzhia': 'Zaporizhzhya', 'Vinnytsia': 'Vinnytsya', 'Oryol': 'Orel', 'Luxembourg': 'Luxembourg-Ville', 'Aarhus': 'Århus'}
rows = [r for r in csv.reader(open('unsd-citypopulation-year-both.csv', encoding='utf-8')) if len(r) == 11 and r[1].isdigit() and r[5] == 'City proper']
un = {}
for c, y, _, _, city, _, rec, _, _, v, _ in rows:
    for key in {norm(city), norm(re.sub(r'\s*\(.*\)$', '', city))}:
        d = un.setdefault(key, {}).setdefault(c, {})
        y = int(y); v = float(v); cen = rec.startswith('Census')
        if y not in d or (cen and not d[y][1]): d[y] = (int(round(v)), cen)
out, miss = [], []
for l in open(CT, encoding='utf-8'):
    if l.startswith('#') or '|' not in l: continue
    name, lon, lat, ser = l.rstrip('\n').split('|')
    base = re.sub(r'\s*\(.*\)$', '', name)
    cands = un.get(norm(ALIAS.get(base, base)), {})
    if not cands: miss.append(name); continue
    # a name in several countries (Brest): the one whose latest figure is closest to the map's
    last = int(ser.split(';')[-1].split(':')[1][:-1])
    c = min(cands, key=lambda c: abs(__import__('math').log(max(1, cands[c][max(cands[c])][0]) / last)))
    pts = sorted((y, v) for y, (v, _) in cands[c].items())
    out.append(f"{name}|{c}|" + ';'.join(f'{y}:{v}' for y, v in pts))
open('un_cities.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('matched', len(out), 'not in the UN table', len(miss)); print(miss)
