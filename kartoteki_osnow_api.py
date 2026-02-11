import re

from .constants import KARTOTEKI_OSNOW_WMS_URL, KARTOTEKI_OSNOW_SKOROWIDZE_LAYERS, KARTOTEKI_OSNOW_ARCHIWALNE_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS, KATALOGI_OSNOW
from .utils import ServiceAPI


def getKartotekiOsnowListbyPoint1992(point, is_kronsztad):
    """Zwraca listę dostępnych do pobrania archiwalnych kartotek osnów geodezyjnych na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(KARTOTEKI_OSNOW_SKOROWIDZE_LAYERS),
        'bbox': '%f,%f,%f,%f' % (x - 50, y - 50, x + 50, y + 50),
        'query_layers': ','.join(KARTOTEKI_OSNOW_SKOROWIDZE_LAYERS),
    })
    
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=params, url=KARTOTEKI_OSNOW_WMS_URL)
    url_wzorzec = re.compile(r'http.+.zip')
    kartoteki_osnowList = []
    if resp and all(resp):
        znalezione_linki = url_wzorzec.findall(resp[1])

        if znalezione_linki:
            elemnetUrl = znalezione_linki[0]
            godlo = elemnetUrl.split('/')[-1].split('.')[0]

            if is_kronsztad:
                rodzaj_katalogu = KATALOGI_OSNOW['Kronsztadt60']
            else:
                rodzaj_katalogu = KATALOGI_OSNOW['Kartoteki1942']

            url = f'{KARTOTEKI_OSNOW_ARCHIWALNE_WMS_URL}{rodzaj_katalogu}/{godlo}.zip'
                
            params = {"url": url, "rodzaj_katalogu": rodzaj_katalogu, "godlo": godlo}
            kartoteki_osnowList.append(params)
            return kartoteki_osnowList
        else:
            return []
    else:
        return None