import requests
import xml.etree.ElementTree as ET

class WfsFetch:
    def __init__(self):
        self.wojewodztwoDict = self.__fetchWojewodztwoDict()
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
        self.filteredPowiatDict = {}


    def __fetchWojewodztwoDict(self):
        resp = requests.get('https://uldk.gugik.gov.pl/service.php?obiekt=wojewodztwo&wynik=wojewodztwo,teryt')
        wojList = resp.text.strip().split('\n')
        wojDict = {}
        if len(wojList) and wojList[0] == '0':
            wojList = wojList[1:]
            for el in wojList:
                split = el.split('|')
                wojDict[split[0]] = split[1]
            return wojDict
        else:
            return {}

    def getPowiatDictByWojewodztwoName(self, name):
        self.filteredPowiatDict = {v[0]: k for k, v in self.powiatDict.items() if v[1] == name}
        return self.filteredPowiatDict

    def getTerytByWojewodztwoName(self,name):
        return self.wojewodztwoDict[name]

    def getTerytByPowiatName(self,name):
        return self.filteredPowiatDict[name]


def getTypenames(wfsUrl):
    """Lista dostępnych warstw"""
    ns = {'ows': "http://www.opengis.net/ows/1.1",
          'fes': "http://www.opengis.net/fes/2.0",
          'gugik': "http://www.gugik.gov.pl",
          'gml': "http://www.opengis.net/gml/3.2",
          'wfs': "http://www.opengis.net/wfs/2.0",
          'xlink': "http://www.w3.org/1999/xlink",
          'xsi': "http://www.w3.org/2001/XMLSchema-instance",
          'xmlns': "http://www.opengis.net/wfs/2.0"
          }
    PARAMS = {
        'SERVICE': 'WFS',
        'request': 'GetCapabilities',
    }
    try:
        r = requests.get(url=wfsUrl, params=PARAMS)
    except requests.exceptions.ConnectionError:
        return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        typenamesList = {}
        root = ET.fromstring(r_txt)
        for featureType in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
            name = featureType.find('.xmlns:Name', ns).text
            title = featureType.find('.xmlns:Title', ns).text
            typenamesList[name] = title

        return True, typenamesList
    else:

        return False, "Błąd %d" % r.status_code

if __name__ == "__main__":
    orto = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze'
    trueOrto = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/SkorowidzPrawdziwejOrtofotomapy'
    lidarKron = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarKRON86/WFS/Skorowidze'
    lidarEvrf = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarEVRF2007/WFS/Skorowidze'
    nmtKron = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuKRON86/WFS/Skorowidze'
    nmtEvrf = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuEVRF2007/WFS/Skorowidze'
    nmptKron = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuKRON86/WFS/Skorowidze'
    nmptEvrf = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuEVRF2007/WFS/Skorowidze'
    resp = getTypenames(nmptEvrf)
    print(resp)