import processing

from ..constants import WFS_URL_MAPPING, POZIOMY_UPROSZCZENIA

try:
    from .utils import getTypenamesFromWFS
    from .utils import roundCoordinatesOfWkt
except ImportError:
    from wfs.utils import getTypenamesFromWFS
    from wfs.utils import roundCoordinatesOfWkt
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject, QgsGeometry, QgsRectangle, QgsWkbTypes


class WfsFetch:
    def __init__(self):
        self.cachedTypenamesDict = {}
        self.errors = []
        # self.refreshCachedTypenamesDict()

    def refreshCachedTypenamesDict(self):
        self.errors = []
        for name in WFS_URL_MAPPING:
            self.__cacheTypenamesForService(name)

    def __cacheTypenamesForService(self, serviceName):
        resp = getTypenamesFromWFS(WFS_URL_MAPPING[serviceName])
        if resp[0]:
            self.cachedTypenamesDict[serviceName] = resp[1]
        else:
            self.errors.append(resp[1])
            print('błąd pobierania warstw usługi WFS %s: %s' % (serviceName, resp[1]))

    def getTypenamesByServiceName(self, serviceName):
        if serviceName not in WFS_URL_MAPPING:
            #podano nieistniejącą nazwę usługi
            raise Exception('podano nieistniejącą nazwę usługi')
        if serviceName not in self.cachedTypenamesDict:
            #nie ma listy w cache, spróbuj pobrać
            self.__cacheTypenamesForService(serviceName)
            if serviceName not in self.cachedTypenamesDict:
                # jeżeli nie udało się pobrać
                return {}
        return self.cachedTypenamesDict[serviceName]

    def getWfsListbyLayer1992(self, layer, wfsService, typename):
        """
        Funkcja pobierająca dane z WFS, dzieląc geometrię na mniejsze części.
        
        :param layer: Warstwa, dla której wykonujemy zapytanie.
        :param wfsService: Nazwa usługi WFS.
        :param typename: Typ danych.
        :return: Lista warstw z wynikami WFS.
        """
        wfsUrl = WFS_URL_MAPPING[wfsService]
        wfsTypename = self.cachedTypenamesDict[wfsService][typename]
        
        # Dynamiczne zarządzanie tolerancją
        area = layer.extent().area()

        # Agregacja i uproszczenie geometrii
        aggregation = processing.run("native:aggregate",
                    {'INPUT': layer,
                    'GROUP_BY': 'NULL', 'AGGREGATES': [], 'OUTPUT': 'TEMPORARY_OUTPUT'})

        simplification = processing.run("native:simplifygeometries",
                    {'INPUT': aggregation['OUTPUT'],
                    'METHOD': 1, 'TOLERANCE': 100, 'OUTPUT': 'TEMPORARY_OUTPUT'})

        simpleLayer = simplification['OUTPUT']
        feat = next(simpleLayer.getFeatures())
        geom = feat.geometry()
        geometry_type = feat.geometry().type()

        # Jeżeli geometria nie jest punktowa, podziel ją na mniejsze fragmenty
        geometries = [geom] 
        

        # Inicjalizacja danych WFS (jeden raz)
        dsu = QgsDataSourceUri()
        dsu.setParam('url', wfsUrl)
        dsu.setParam('version', '2.0.0')
        dsu.setParam('typename', wfsTypename)
        dsu.setParam('srsname', 'EPSG:2180')

        layers = []
        wkt = roundCoordinatesOfWkt(geom.asWkt())  # Zaokrąglamy współrzędne raz na początku

        # Wykonanie zapytania dla każdej części geometrii
        for sub_geom in geometries:
            if dsu.hasParam('filter'):
                dsu.removeParam('filter')
            wkt = roundCoordinatesOfWkt(sub_geom.asWkt())
            dsu.setParam('filter', "intersects($geometry, geomFromWKT('%s'))" % wkt)

            # Pobieranie danych z WFS dla każdej części
            l = QgsVectorLayer(dsu.uri(), typename, "WFS")
            l.updateFields()
            layers.append(l)

        # Łączenie warstw tylko jeśli jest ich więcej niż jedna
        if len(layers) > 1:
            merged_layer = processing.run("native:mergevectorlayers",
                                        {'LAYERS': layers, 'CRS': 'EPSG:2180', 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        else:
            merged_layer = layers[0]  # Jeżeli tylko jedna warstwa, nie ma potrzeby łączenia

        # Usunięcie zduplikowanych geometrii z połączonej warstwy
        processedLayer = processing.run(
            "native:deleteduplicategeometries", {
                'INPUT': merged_layer,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
        )['OUTPUT']
        return processedLayer



if __name__ == "__main__":

    wfsFetch = WfsFetch()
    print(wfsFetch.cachedTypenamesDict)
    resp = wfsFetch.getTypenamesByServiceName('nmtKron')
    print(resp)