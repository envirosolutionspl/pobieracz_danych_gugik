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
- Ortofotomapy RGB/CIR -  ortofotomapa cyfrowa i zobrazowanie w bliskiej podczerwieni
- NMT/NMPT (od wersji 0.3)
- LAZ LIDAR (od wersji 0.4)
- Obrazy intensywności (od wersji 0.5)
- Paczki danych BDOT10k - powiatowe, wojewódzkie lub krajowa (od wersji 0.6)
- Paczki danych BDOO - wojewódzkie lub krajowe (od wersji 1.0)
- Paczki danych PRNG (od wersji 1.0)
- Paczki danych PRG (od wersji 1.0)
- Paczki danych modeli 3D budynków - powiatowe (od wersji 1.0)
- Paczki danych EGiB - powiatowe (wersja beta od wersji 1.0)
- Paczki archiwalnych danych BDOT10k - wojewódzkie (od wersji 1.0)

#### Dodatowe dane
Wtyczka pozwala także na pobranie dodatkowych danych udostępnionych przed GUGiK:
- Zestawienia zbiorcze EGiB - arkusz kalkulacyjny excel, XLS (od wersji 1.0)
- Opracowania tyflologiczne - mapy dla niewidomych i słabowidzących, PDF/TIFF/JPG/CDR (od wersji 1.0)
- Osnowa geodezyjna (od wersji 1.0)
	- Podstawowa Osnowa Geodezyjna - XLS/PDF
	- Archiwalne Kartoteki Osnów  - TIFF/PDF
- Aerotriangulacja - format m.in: ASC/CSF/ISPM/PDF (od wersji 1.0)
- Linie mozaikowania - SHZ (od wersji 1.0)
- Wizualizacja kartograficzna BDOT10k - PDF (od wersji 1.0)
- Zdjęcia lotnicze - JPG (od wersji 1.0)

#### Pobieranie na podstawie warstwy poligonowej
1. Wtyczka generuje siatkę punktów wewnątrz zadanej warstwy poligonowej oraz na podstawie werteksów
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

#### Pobieranie na podstawie warstwy liniowej
1. Wtyczka generuje punkty w odstępie 1000m wzdłuż linii (1500m dla NMT/NMPT)
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

**UWAGA:** Na niestandardowych wersjach programu QGIS, możliwe są błędy importu bibliotek.
Jeżeli wystąpi taka sytuacja, należy zgodnie z instrukcją producenta oprogramowania doinstalować bibliotekę/i.

#### Pobieranie na podstawie warstwy punktowej
1. Dla każdego z punktów w warstwie pobierana jest lista dostepnych warstw
2. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

##### Kontakt:
Michał Włoga - EnviroSolutions Sp. z o.o. http://www.envirosolutions.pl
