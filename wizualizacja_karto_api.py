import re
from . import service_api

def getWizualizacjaKartoListbyPoint1992(point, skala_10000):
    """Zwraca listę dostępnych do pobrania areotriangulacji na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    c = re.compile("\{{1}.*\}{1}")

    URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/BDOT/WMS/PobieranieArkuszeMapBDOT10k?"

    if skala_10000:
        LAYERS = [
            'Mapy10k'
        ]

    else:
        LAYERS = [
            'Mapy25'
        ]

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
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

    if resp[0]:
        print(resp[1])
        wzorzec = re.compile(r'http.+.pdf')
        resp = wzorzec.findall(resp[1])[0]
        # print(resp)
        return resp
    else:
        return None

