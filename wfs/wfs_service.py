try:
    from .utils import getTypenames
except ImportError:
    from wfs.utils import getTypenames

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




if __name__ == "__main__":

    wfsFetch = WfsFetch()
    print(wfsFetch.cachedTypenamesDict)
    resp = wfsFetch.getTypenamesByServiceName('nmtKron')
    print(resp)