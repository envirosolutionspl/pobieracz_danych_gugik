# Pobieracz danych GUGiK - Wtyczka QGIS 3
Wtyczka QGIS do pobierania danych przestrzennych z zasobów GUGiK. 
Możliwe jest pobieranie:
- poprzez wskazanie punktu na mapie
- poprzez warstwę poligonową
- poprzez warstwę liniową
- poprzez warstwę punktową (od wersji 0.3)

od wersji 0.2 wtyczka generuje dodatkowo raport CSV z informacjami dodatowymi na temat pobranych plików

#### Dostępne warstwy
Wtyczka pozwala na pobieranie nastepujących warstw dla obszaru Polski:
- Ortofotomapy RGB/CIR
- NMT/NMPT (od wersji 0.3)
- LAS/LAZ LIDAR (od wersji 0.4)
- Obrazy intensywności (od wersji 0.5)
- Paczki danych BDOT10k - powiatowe, wojewódzkie lub krajowa (od wersji 0.6)
- Paczki danych BDOO - wojewódzkie lub krajowe (od wersji 1.0)
- Paczki danych PRNG (od wersji 1.0)
- Paczki danych PRG (od wersji 1.0)
- Paczki danych modeli 3D budynków - powiatowe (od wersji 1.0)
- Paczki danych EGiB - powiatowe (od wersji 1.0)
- Paczki archiwalnych danych BDOT10k - wojewódzkie (od wersji 1.0)

#### Dodatowe dane
Wtyczka pozwala także na pobranie danych nieprzestrzennych udostępnionych przed GUGiK:
- Zestawienia zbiorcze EGiB - arkusz kalkulacyjny excel (od wersji 1.0)
- Opracowania tyflologiczne - mapy dla niewidomych i słabowidzących, format: pdf, tiff, jpg, cdr (od wersji 1.0)
- Osnowa geodezyjna (od wersji 1.0)
	- Podstawowa Osnowa Geodezyjna - format: pdf, xls
	- Archiwalne Kartoteki Osnów  - format: tiff, pdf
- Aerotriangulacja - format m.in: pdf, csf, asc, ispm (od wersji 1.0)
- Linie mozaikowania - format shz (od wersji 1.0)
- Wizualizacja kartograficzna BDOT10k - format pdf (od wersji 1.0)
- Zdjęcia lotnicze - format jpg (od wersji 1.0)

#### Pobieranie na podstawie warstwy poligonowej
1. Wtyczka generuje siatkę punktów wewnątrz zadanej warstwy poligonowej oraz na podstawie werteksów
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

#### Pobieranie na podstawie warstwy liniowej
1. Wtyczka generuje punkty w odstępie 1000m wzdłuż linii (1500m dla NMT/NMPT)
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

#### Pobieranie na podstawie warstwy punktowej
1. Dla każdego z punktów w warstwie pobierana jest lista dostepnych warstw
2. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

##### Kontakt:
Michał Włoga - EnviroSolutions Sp. z o.o. http://www.envirosolutions.pl