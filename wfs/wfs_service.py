import processing

from ..constants import WFS_URL_MAPPING

try:
    from .utils import getTypenamesFromWFS
    from .utils import roundCoordinatesOfWkt
except ImportError:
    from wfs.utils import getTypenamesFromWFS
    from wfs.utils import roundCoordinatesOfWkt
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject


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

    def divideGeometry(self, geometry, parts):
        """
        Funkcja dzieląca geometrię na mniejsze części.
        
        :param geometry: Geometria, która ma zostać podzielona.
        :param parts: Liczba części, na które ma zostać podzielona geometria.
        :return: Lista mniejszych geometrii.
        """
        bounds = geometry.boundingBox()
        width = bounds.width() / parts
        height = bounds.height() / parts

        sub_geometries = []
        for i in range(parts):
            for j in range(parts):
                sub_bounds = QgsRectangle(
                    bounds.xMinimum() + i * width,
                    bounds.yMinimum() + j * height,
                    bounds.xMinimum() + (i + 1) * width,
                    bounds.yMinimum() + (j + 1) * height
                )
                sub_geometry = geometry.intersection(QgsGeometry.fromRect(sub_bounds))
                if not sub_geometry.isEmpty():
                    sub_geometries.append(sub_geometry)
        
        return sub_geometries

    def getWfsListbyLayer1992(self, layer, wfsService, typename):
        wfsUrl = WFS_URL_MAPPING[wfsService]
        wfsTypename = self.cachedTypenamesDict[wfsService][typename]
        aggregation = processing.run("native:aggregate",
                       {'INPUT': layer,
                        'GROUP_BY': 'NULL', 'AGGREGATES': [], 'OUTPUT': 'TEMPORARY_OUTPUT'})
        simplification = processing.run("native:simplifygeometries",
                       {'INPUT': aggregation['OUTPUT'],
                        'METHOD': 1, 'TOLERANCE': 100, 'OUTPUT': 'TEMPORARY_OUTPUT'})
        simpleLayer = simplification['OUTPUT']
        feat = next(simpleLayer.getFeatures())
        geom = feat.geometry()
        wkt = geom.asWkt()
        wkt = roundCoordinatesOfWkt(wkt)    # zaokrąglanie współrzędnych do liczb całkowitych


        dsu = QgsDataSourceUri()
        dsu.setParam('url', wfsUrl)
        dsu.setParam('version', '2.0.0')
        dsu.setParam('typename', wfsTypename)
        # dsu.setParam( 'maxNumFeatures', '10')
        # dsu.setParam('srsname', 'urn:ogc:def:crs:EPSG::3857')
        dsu.setParam('srsname', 'EPSG:2180')
        dsu.setParam('filter', "intersects($geometry, geomFromWKT('%s'))" % wkt)

        # dsu.setParam( 'filter', "intersects($geometry, geomFromWKT('Polygon ((17.84319299999999942 52.99999700000000047, 18.18789100000000047 52.93750200000000206, 18.31216900000000081 52.79166599999999931, 18.06204899999999824 52.77083199999999863, 17.84430300000000003 52.77083900000000227, 17.84319299999999942 52.99999700000000047))'))")
        l = QgsVectorLayer(dsu.uri(), typename, "WFS")
        l.updateFields()
        return l





if __name__ == "__main__":

    wfsFetch = WfsFetch()
    print(wfsFetch.cachedTypenamesDict)
    resp = wfsFetch.getTypenamesByServiceName('nmtKron')
    print(resp)