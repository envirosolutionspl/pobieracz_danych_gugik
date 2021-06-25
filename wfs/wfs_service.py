
from .utils import getTypenames

class WfsFetch:
    def __init__(self):
        self.wfsServiceDict = {
            'orto' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze',
            'trueOrto' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/SkorowidzPrawdziwejOrtofotomapy',
            'lidarKron' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarKRON86/WFS/Skorowidze',
            'lidarEvrf' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarEVRF2007/WFS/Skorowidze',
            'nmtKron' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuKRON86/WFS/Skorowidze',
            'nmtEvrf' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuEVRF2007/WFS/Skorowidze',
            'nmptKron' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuKRON86/WFS/Skorowidze',
            'nmptEvrf' : 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuEVRF2007/WFS/Skorowidze'
        }
        self.cachedTypenamesDict = {}
        self.errors = []
        # self.refreshCachedTypenamesDict()

    def refreshCachedTypenamesDict(self):
        self.errors = []
        for name in self.wfsServiceDict:
            self.cacheTypenamesForService(name)

    def cacheTypenamesForService(self, serviceName):

        resp = getTypenames(self.wfsServiceDict[serviceName])
        if resp[0]:
            self.cachedTypenamesDict[serviceName] = resp[1]
        else:
            self.errors.append(resp[1])
            print('błąd pobierania warstw usługi WFS %s: %s' % (serviceName, resp[1]))



if __name__ == "__main__":

    wfsFetch = WfsFetch()
    print(wfsFetch.errors)
    print(wfsFetch.cachedTypenamesDict)
    wfsFetch.cacheTypenamesForService('trueOrto')
    print(wfsFetch.cachedTypenamesDict)