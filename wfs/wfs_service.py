import processing
try:
    from .utils import getTypenames
except ImportError:
    from wfs.utils import getTypenames
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject
class WfsFetch:
    def __init__(self):
        self.wfsServiceDict = {
            'Ortofotomapa' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze',
            'Prawdziwa Ortofotomapa' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/SkorowidzPrawdziwejOrtofotomapy',
            'LIDAR (PL-KRON86-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarKRON86/WFS/Skorowidze',
            'LIDAR (PL-EVRF2007-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarEVRF2007/WFS/Skorowidze',
            'NMT (PL-KRON86-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuKRON86/WFS/Skorowidze',
            'NMT (PL-EVRF2007-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuEVRF2007/WFS/Skorowidze',
            'NMPT (PL-KRON86-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuKRON86/WFS/Skorowidze',
            'NMPT (PL-EVRF2007-NH)' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuEVRF2007/WFS/Skorowidze'
        }
        self.cachedTypenamesDict = {}
        self.errors = []
        # self.refreshCachedTypenamesDict()

    def refreshCachedTypenamesDict(self):
        self.errors = []
        for name in self.wfsServiceDict:
            self.__cacheTypenamesForService(name)

    def __cacheTypenamesForService(self, serviceName):

        resp = getTypenames(self.wfsServiceDict[serviceName])
        if resp[0]:
            self.cachedTypenamesDict[serviceName] = resp[1]
        else:
            self.errors.append(resp[1])
            print('błąd pobierania warstw usługi WFS %s: %s' % (serviceName, resp[1]))

    def getTypenamesByServiceName(self, serviceName):
        if serviceName not in self.wfsServiceDict:
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

        print('----------',layer.crs())
        wfsUrl = self.wfsServiceDict[wfsService]
        wfsTypename = self.cachedTypenamesDict[wfsService][typename]
        output = processing.run("native:aggregate",
                       {'INPUT': layer,
                        'GROUP_BY': 'NULL', 'AGGREGATES': [], 'OUTPUT': 'TEMPORARY_OUTPUT'})
        layerAggr = output['OUTPUT']
        feat = next(layerAggr.getFeatures())
        geom = feat.geometry()
        wkt = geom.asWkt()
        print('i-------', wkt)
        # wkt =
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