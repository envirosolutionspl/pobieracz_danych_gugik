# Pobieracz danych GUGiK - Wtyczka QGIS 3
Wtyczka QGIS do pobierania danych przestrzennych z zasobów GUGiK. 
Możliwe jest pobieranie:
- poprzez wskazanie punktu na mapie
- poprzez warstwę poligonową
- poprzez warstwę liniową

od wersji 0.2 wtyczka generuje dodatkowo raport CSV z informacjami dodatowymi na temat pobranych plików

#### Dostępne warstwy
Wtyczka pozwala na pobieranie nastepujących warstw dla obszaru Polski:
- Ortofotomapy RGB/CIR

#### Pobieranie na podstawie warstwy poligonowej
1. Wtyczka generuje siatkę punktów wewnątrz zadanego poligonu oraz na podstawie werteksów
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy

#### Pobieranie na podstawie warstwy liniowej
1. Wtyczka generuje punkty w odstępie 1000m wzdłuż linii
2. Dla każdego z wygenerowanych punktów pobierana jest lista dostepnych warstw
3. Po przefiltrowaniu pobierane są wybrane przez użytkownika warstwy