"""Build the Balkan sample-town list: Natural Earth towns plus a curated set of historically important places."""
import json, math

CURATED = """Niš,43.321,21.896;Kragujevac,44.012,20.911;Pirot,43.153,22.586;Vranje,42.551,21.900;Leskovac,42.998,21.946;Šabac,44.756,19.690;Užice,43.858,19.843;Čačak,43.891,20.349;Smederevo,44.665,20.928;Negotin,44.226,22.531;Zaječar,43.904,22.285;Kruševac,43.580,21.334;Novi Pazar,43.137,20.512;Novi Sad,45.267,19.833;Subotica,46.100,19.667;Zemun,44.843,20.401;Prokuplje,43.234,21.588;Kuršumlija,43.140,21.270;
Cetinje,42.390,18.914;Podgorica,42.441,19.263;Nikšić,42.773,18.945;Bar,42.093,19.100;Ulcinj,41.929,19.224;Pljevlja,43.357,19.358;Kotor,42.425,18.771;Herceg Novi,42.453,18.537;Sutomore,42.142,19.047;Bijelo Polje,43.038,19.748;Plav,42.597,19.945;Kolašin,42.823,19.522;Danilovgrad,42.553,19.106;Andrijevica,42.734,19.791;
Mostar,43.343,17.808;Banja Luka,44.772,17.191;Tuzla,44.538,18.676;Bihać,44.817,15.870;Trebinje,42.712,18.344;Foča,43.506,18.775;Zenica,44.203,17.908;Travnik,44.226,17.665;
Nafplio,37.568,22.806;Arta,39.160,20.985;Larissa,39.639,22.419;Volos,39.362,22.942;Trikala,39.555,21.767;Karditsa,39.365,21.922;Lamia,38.900,22.434;Missolonghi,38.371,21.431;Patras,38.246,21.735;Corfu,39.624,19.922;Zakynthos,37.781,20.896;Argostoli,38.176,20.489;Lefkada,38.831,20.705;Heraklion,35.339,25.144;Chania,35.514,24.018;Ioannina,39.665,20.853;Preveza,38.959,20.751;Kavala,40.937,24.413;Serres,41.086,23.548;Kozani,40.300,21.789;Chios,38.368,26.136;Vathy,37.757,26.977;Rhodes,36.434,28.217;Mytilene,39.107,26.555;Ermoupoli,37.444,24.943;Chalkida,38.463,23.599;Tripoli,37.510,22.372;Kalamata,37.039,22.114;Elassona,39.895,22.188;Kalabaka,39.706,21.626;Tyrnavos,39.738,22.287;
Plovdiv,42.150,24.750;Varna,43.214,27.915;Ruse,43.848,25.954;Vidin,43.990,22.873;Pleven,43.417,24.607;Burgas,42.504,27.463;Stara Zagora,42.426,25.634;Veliko Tarnovo,43.081,25.629;Shumen,43.271,26.936;Silistra,44.117,27.260;Dobrich,43.567,27.829;Kardzhali,41.650,25.378;Kyustendil,42.284,22.691;Sliven,42.682,26.323;Haskovo,41.934,25.556;Smolyan,41.577,24.701;Blagoevgrad,42.021,23.094;
Constanța,44.160,28.635;Tulcea,45.179,28.805;Iași,47.159,27.587;Galați,45.435,28.008;Brăila,45.271,27.957;Craiova,44.330,23.795;Cluj,46.770,23.590;Timișoara,45.749,21.227;Brașov,45.658,25.601;Sibiu,45.793,24.152;Suceava,47.651,26.255;Turnu Severin,44.631,22.656;Giurgiu,43.904,25.970;Mangalia,43.817,28.583;Medgidia,44.250,28.270;Focșani,45.697,27.184;
Chernivtsi,48.292,25.935;Izmail,45.351,28.837;Bolhrad,45.681,28.613;Bilhorod-Dnistrovskyi,46.186,30.345;Reni,45.456,28.283;Kiliya,45.451,29.264;Vylkove,45.402,29.588;
Cahul,45.904,28.194;Bender,46.831,29.477;Bălți,47.762,27.929;Comrat,46.297,28.656;
Pristina,42.663,21.165;Prizren,42.215,20.740;Peja,42.659,20.288;
Skopje,41.998,21.425;Bitola,41.031,21.335;Ohrid,41.117,20.802;Štip,41.736,22.192;
Shkodër,42.068,19.513;Durrës,41.323,19.441;Vlorë,40.466,19.490;Korçë,40.618,20.781;Gjirokastër,40.076,20.139;
Dubrovnik,42.650,18.094;Split,43.508,16.440;Zadar,44.119,15.232;Rijeka,45.327,14.442;Osijek,45.554,18.694;Karlovac,45.487,15.548;
Edirne,41.677,26.556;Kırklareli,41.735,27.225;Tekirdağ,40.978,27.511;Gelibolu,40.408,26.670"""

def km(a, b):
    dy = (a[0] - b[0]) * 111
    dx = (a[1] - b[1]) * 111 * math.cos(math.radians(a[0]))
    return math.hypot(dx, dy)

ne = json.load(open('towns_ne.json'))
towns = [(n, round(lat, 3), round(lon, 3)) for n, _, lat, lon, _ in ne]
for item in CURATED.replace('\n', '').split(';'):
    n, lat, lon = item.split(',')
    p = (float(lat), float(lon))
    if not any(km(p, (t[1], t[2])) < 4 for t in towns):
        towns.append((n, p[0], p[1]))
# make names unique
seen = {}
out = []
for n, lat, lon in towns:
    k = n
    if k in seen:
        seen[k] += 1; k = f'{n} ({seen[n]})'
    else:
        seen[k] = 1
    out.append([k, lat, lon])
json.dump(out, open('towns.json', 'w'), ensure_ascii=False)
print(len(out))
print(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
