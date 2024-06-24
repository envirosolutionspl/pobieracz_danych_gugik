import re

from . import service_api


def getKartotekiOsnowListbyPoint1992(point, katalog_niwelacyjne):
    """Zwraca listę dostępnych do pobrania archiwalnych kartotek osnów geodezyjnych na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/Osnowy/WMS/Archiwalne_kartoteki?"

    LAYERS = [
        'Katalogi_Kartoteki1942',
        'Katalogi_Kronsztadt60'
    ]

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x - 50, y - 50, x + 50, y + 50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }

    resp = service_api.getRequest(params=PARAMS, url=URL)
    url_wzorzec = re.compile(r'http.+.zip')
    kartoteki_osnowList = []
    if resp[0]:
        elemnetUrl = url_wzorzec.findall(resp[1])[0]
        godlo = elemnetUrl.split('/')[-1].split('.')[0]

        if katalog_niwelacyjne:
            rodzaj_katalogu = 'Katalogi_Kronsztadt60'
        else:
            rodzaj_katalogu = 'Katalogi_Kartoteki1942'
        url = f"https://opendata.geoportal.gov.pl/bdpog/MaterialyArchiwalne/{rodzaj_katalogu}/{godlo}.zip"
        params = {"url": url, "rodzaj_katalogu": rodzaj_katalogu, "godlo": godlo}
        kartoteki_osnowList.append(params)
        return kartoteki_osnowList
    else:
        return None