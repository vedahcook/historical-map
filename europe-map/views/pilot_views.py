# The pilot's period views: four cities, each view with the year it was made (y: the year used to pick the
# closest view; label: how the date is shown), what it is, who made it, its license, and its Wikimedia Commons file.
# f: the Commons file name (thumbnail URLs are built from it; see make_fetch_script.py).
V = [
 # Cologne
 ('cologne', 1493, '1493', 'Woodcut in Hartmann Schedel’s Nuremberg Chronicle', 'Michael Wolgemut and Wilhelm Pleydenwurff', 'PD', 'Hartmann Schedel, Colonia (FL54266073 4108338).jpg'),
 ('cologne', 1572, '1572', 'Engraving in Braun and Hogenberg, Civitates Orbis Terrarum, vol. 1', 'Georg Braun and Frans Hogenberg', 'PD', 'Braun Köln UBHD.jpg'),
 ('cologne', 1635, '1635', 'Bird’s-eye view, etching', 'Wenceslaus Hollar', 'PD', 'Eigentliche Abbildung des H. Römischen Reichs freyer Statt Cöllen (1633).jpg'),
 ('cologne', 1845, '1845', 'Panorama with the bridge of boats, painting (Kölnisches Stadtmuseum)', 'Johann Jakob Diezler', 'PD', 'Köln-Panorama mit Schiffsbrücke - Jakob Diezler - Kölnisches Stadtmuseum-7272.jpg'),
 ('cologne', 1895, '1890s', 'Photochrom print (Library of Congress)', 'Detroit Publishing Co.', 'PD', 'General view, Cologne, the Rhine, Germany-LCCN2002714082.jpg'),
 ('cologne', 1945, '1945', 'Aerial photograph, March 9, 1945 (Imperial War Museums)', 'Royal Air Force', 'PD', 'Cologne Cathedral stands intact amidst the destruction caused by Allied air raids, 9 March 1945. CL2169.jpg'),
 ('cologne', 2014, '2014', 'Photograph', 'Dietmar Rabich', 'CC BY-SA 4.0', 'Köln, Stadtpanorama -- 2014 -- 1857.jpg'),
 # Vienna
 ('vienna', 1493, '1493', 'Woodcut in Hartmann Schedel’s Nuremberg Chronicle', 'Michael Wolgemut and Wilhelm Pleydenwurff', 'PD', 'Hartmann Schedel, Vienna Pannonie (FL54266072 4108343).jpg'),
 ('vienna', 1572, '1572', 'Engraving in Braun and Hogenberg, Civitates Orbis Terrarum, vol. 1', 'Georg Braun and Frans Hogenberg', 'PD', 'Braun Wien UBHD.jpg'),
 ('vienna', 1649, '1649', 'Engraving in Topographia Provinciarum Austriacarum', 'Matthäus Merian', 'PD', 'Statt Wien (Merian).jpg'),
 ('vienna', 1760, '1758–61', 'Vienna seen from the Belvedere, painting (Kunsthistorisches Museum)', 'Bernardo Bellotto', 'PD', 'Bernardo Bellotto, called Canaletto - Vienna Viewed from the Belvedere Palace - Google Art Project.jpg'),
 ('vienna', 1895, '1890s', 'The Opernring, photochrom print (Library of Congress)', 'Detroit Publishing Co.', 'PD', 'Opernring, Vienna, Austro-Hungary-LCCN2002708403.jpg'),
 ('vienna', 2018, '2018', 'The city from the south tower of St. Stephen’s Cathedral, photograph', 'Dietmar Rabich', 'CC BY-SA 4.0', 'Wien, Stephansdom, Blick vom Südturm -- 2018 -- 3274-6.jpg'),
 # Paris
 ('paris', 1572, '1572', 'Engraving in Braun and Hogenberg, Civitates Orbis Terrarum, vol. 1 (Bibliothèque nationale de France)', 'Georg Braun and Frans Hogenberg', 'PD', 'Lutetia vulgari nomine Paris, urbs Galliae maxima, 1572 - Gallica.jpg'),
 ('paris', 1615, '1615', 'Bird’s-eye plan, engraving (Bibliothèque nationale de France)', 'Matthäus Merian', 'PD', 'Merian map of Paris 1615 - Gallica.jpg'),
 ('paris', 1752, '1752', 'The Île Saint-Louis and Notre-Dame, painting', 'Nicolas-Jean-Baptiste Raguenet', 'PD', "Raguenet Vue de l'île Saint Louis avec Notre-Dame de Paris.jpg"),
 ('paris', 1860, 'about 1860', 'Panorama of the Île de la Cité, photograph (Metropolitan Museum of Art)', 'Édouard Baldus', 'PD', 'Édouard Baldus, Panorama de la Cité, circa 1860.jpg'),
 ('paris', 1895, '1890s', 'Notre-Dame and the Pont Saint-Michel, photochrom print (Library of Congress)', 'Detroit Publishing Co.', 'PD', 'Notre Dame, and St. Michael bridge, Paris, France-LCCN2001698531.jpg'),
 ('paris', 1948, '1948', 'Aerial photograph of the islands and the Boulevard Saint-Germain (Musée Carnavalet)', 'Roger Henrard', 'CC0', 'Vue aérienne de Paris vue générale avec le boulevard Saint-Germain et les îles de la Cité et Saint-Louis, 1er, 5ème, 6, PH344-456.jpg'),
 ('paris', 2014, '2014', 'The Île de la Cité from the Pont des Arts, photograph', 'DXR', 'CC BY-SA 3.0', 'Île de la Cité shortly before sunrise, West View 140320 1.jpg'),
 # Constantinople / Istanbul
 ('istanbul', 1493, '1493', 'Woodcut in Hartmann Schedel’s Nuremberg Chronicle', 'Michael Wolgemut and Wilhelm Pleydenwurff', 'PD', '1493 view of Istanbul from Hartmann Schedels Chronik.jpg'),
 ('istanbul', 1572, '1572', 'Engraving in Braun and Hogenberg, Civitates Orbis Terrarum, vol. 1', 'Georg Braun and Frans Hogenberg', 'PD', 'Georg Braun & Frans Hogenberg - Byzantium Nunc Constantinopolis.jpg'),
 ('istanbul', 1638, '1638', 'View of Constantinople, engraving', 'Matthäus Merian', 'PD', '1638 Merian View of Istanbul, Turkey.jpg'),
 ('istanbul', 1775, '1770s', 'Constantinople and the Topkapı Palace from the Swedish embassy, painting (Rijksmuseum)', 'Jan van der Steen', 'PD', 'Gezicht op Constantinopel en het Serail vanuit de Zweedse ambassade te Pera Rijksmuseum SK-A-2056.jpeg'),
 ('istanbul', 1852, '1852', 'Panorama from a minaret of Hagia Sophia, lithograph (Library of Congress)', 'Gaspare Fossati and Louis Haghe', 'PD', "Panorama de Constantinople, pris d'un des minarets de Ste. Sophie LCCN2004666277.jpg"),
 ('istanbul', 1895, '1890s', 'The Golden Horn, photochrom print (Library of Congress)', 'Detroit Publishing Co.', 'PD', 'The Golden Horn, Constantinople, Turkey-LCCN2001699446.jpg'),
 ('istanbul', 1955, '1955', 'The Golden Horn, photograph', 'U.S. Navy', 'PD', 'View of the Golden Horn in Istanbul, Turkey, in 1955.jpg'),
 ('istanbul', 2011, '2011', 'The Golden Horn from Pierre Loti hill, photograph', 'Ggia', 'CC BY-SA 3.0', '20110711 Pierre Loti hill view Istanbul Turkey Panorama.jpg'),
]
