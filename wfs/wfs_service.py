import processing
from functools import partial

from ..constants import WFS_URL_MAPPING, POZIOMY_UPROSZCZENIA, CRS

try:
    from .utils import getTypenamesFromWFS, parseTypenamesFromCapabilities
    from .utils import WFS_CAPABILITIES_PARAMS, WFS_CAPABILITIES_TIMEOUT_MS
    from .utils import roundCoordinatesOfWkt
except ImportError:
    from wfs.utils import getTypenamesFromWFS, parseTypenamesFromCapabilities
    from wfs.utils import WFS_CAPABILITIES_PARAMS, WFS_CAPABILITIES_TIMEOUT_MS
    from wfs.utils import roundCoordinatesOfWkt
from qgis.core import QgsDataSourceUri, QgsVectorLayer
from ..utils import MessageUtils, NetworkUtils


class WfsFetch:
    def __init__(self):
        self.cachedTypenamesDict = {}
        self.errors = []
        self.network_utils = NetworkUtils()
        # self.refreshCachedTypenamesDict()

    def getCachedTypenames(self, serviceName):
        """Lista warstw z pamięci albo None, jeśli jeszcze nie pobrana."""
        return self.cachedTypenamesDict.get(serviceName)

    def fetchTypenamesAsync(self, serviceName, on_done):
        """Pobiera listę warstw usługi bez blokowania QGIS.

        `on_done(typenames_dict)` w głównym wątku; pusty słownik oznacza błąd.
        Parsowanie (lxml) też w głównym wątku - lxml w QgsTask crashuje QGIS.
        """
        self.network_utils.fetchContentAsync(
            WFS_URL_MAPPING[serviceName],
            partial(self._onCapabilitiesFetched, serviceName, on_done),
            params=WFS_CAPABILITIES_PARAMS,
            timeout_ms=WFS_CAPABILITIES_TIMEOUT_MS
        )

    def _onCapabilitiesFetched(self, serviceName, on_done, fetch_result):
        """GetCapabilities -> lista warstw (zapisana w cache); pusty słownik przy błędzie."""
        is_success, result = fetch_result
        if is_success:
            is_success, result = parseTypenamesFromCapabilities(result)
        if not is_success:
            self.errors.append(result)
            MessageUtils.pushLogWarning('Błąd pobierania warstw usługi WFS %s: %s' % (serviceName, result))
            on_done({})
            return
        self.cachedTypenamesDict[serviceName] = result
        on_done(result)

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
            MessageUtils.pushLogWarning('Błąd pobierania warstw usługi WFS %s: %s' % (serviceName, resp[1]))

    def getTypenamesByServiceName(self, serviceName):
        if serviceName not in WFS_URL_MAPPING:
            # podano nieistniejącą nazwę usługi
            raise Exception('podano nieistniejącą nazwę usługi')
        if serviceName not in self.cachedTypenamesDict:
            # nie ma listy w cache, spróbuj pobrać
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

        # Agregacja i uproszczenie geometrii
        aggregation = processing.run(
            "native:aggregate", {
                'INPUT': layer,
                'GROUP_BY': 'NULL',
                'AGGREGATES': [],
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
        )['OUTPUT']

        feat = aggregation.getFeature(1)
        length = feat.geometry().length()

        for poziom in POZIOMY_UPROSZCZENIA.keys():
            if length <= poziom:
                simplification = processing.run(
                    "native:simplifygeometries", {
                        'INPUT': aggregation,
                        'METHOD': 1,
                        'TOLERANCE': POZIOMY_UPROSZCZENIA[poziom],
                        'OUTPUT': 'TEMPORARY_OUTPUT'
                    }
                )
                break
        else:
            simplification = processing.run(
                "native:simplifygeometries", {
                    'INPUT': aggregation,
                    'METHOD': 1,
                    'TOLERANCE': POZIOMY_UPROSZCZENIA[50000000],
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )

        simpleLayer = simplification['OUTPUT']
        feat = next(simpleLayer.getFeatures())
        geom = feat.geometry()
        feat.geometry().type()

        # Jeżeli geometria nie jest punktowa, podziel ją na mniejsze fragmenty
        geometries = [geom]

        # Inicjalizacja danych WFS (jeden raz)
        dsu = QgsDataSourceUri()
        dsu.setParam('url', wfsUrl)
        dsu.setParam('version', '2.0.0')
        dsu.setParam('typename', wfsTypename)
        dsu.setParam('srsname', 'EPSG:' + CRS)

        layers = []
        # Wykonanie zapytania dla każdej części geometrii
        for sub_geom in geometries:
            if dsu.hasParam('filter'):
                dsu.removeParam('filter')
            wkt = roundCoordinatesOfWkt(sub_geom.asWkt())
            dsu.setParam('filter', "intersects($geometry, geomFromWKT('%s'))" % wkt)

            # Pobieranie danych z WFS dla każdej części
            wfs_layer = QgsVectorLayer(dsu.uri(), typename, "WFS")
            wfs_layer.updateFields()
            layers.append(wfs_layer)

        # Łączenie warstw tylko jeśli jest ich więcej niż jedna
        if len(layers) > 1:
            merged_layer = processing.run(
                "native:mergevectorlayers",
                {
                    'LAYERS': layers,
                    'CRS': 'EPSG:' + CRS,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )['OUTPUT']
        else:
            merged_layer = layers[0]  # Jeżeli tylko jedna warstwa, nie ma potrzeby łączenia

        return merged_layer


if __name__ == "__main__":

    wfsFetch = WfsFetch()
    print(wfsFetch.cachedTypenamesDict)
    resp = wfsFetch.getTypenamesByServiceName('nmtKron')
    print(resp)
