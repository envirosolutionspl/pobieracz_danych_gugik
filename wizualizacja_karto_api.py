import re

from .constants import WIZUALIZACJA_KARTO_WMS_URL, WIZUALIZACJA_KARTO_10K_SKOROWIDZE_LAYERS, \
    WIZUALIZACJA_KARTO_25K_SKOROWIDZE_LAYERS
from . import service_api
from .models import Wizualizacja_karto

#TODO zmiana sposobu zapisu danych z requesta na słownik jak w innych przypadkach
def getWizualizacjaKartoListbyPoint1992(point, skala_10000):
    """Zwraca listę dostępnych do pobrania wizualizacji kartograficznych BDOT10k na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()
    layers = WIZUALIZACJA_KARTO_10K_SKOROWIDZE_LAYERS if skala_10000 else WIZUALIZACJA_KARTO_25K_SKOROWIDZE_LAYERS

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(layers),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x - 50, y - 50, x + 50, y + 50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(layers),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }
    resp = service_api.getRequest(params=PARAMS, url=WIZUALIZACJA_KARTO_WMS_URL)
    url_wzorzec = re.compile(r'http.+.pdf')
    data_wzorzec = re.compile(r"(\d{4}-\d{1,2}-\d{1,2})")
    if resp[0]:
        wizKartoElementsUrl = url_wzorzec.findall(resp[1])
        wizKartoList = []
        params = {}
        id = 0
        for wizKartoElement in wizKartoElementsUrl:
            godlo = wizKartoElement.split('/')[-1].split('.')[0]
            wizKartoElementsData = data_wzorzec.findall(resp[1])[id]
            if skala_10000:
                skala = '1:10000'
            else:
                skala = '1:25000'
            id = id + 1
            params["url"] = wizKartoElement
            params["data"] = wizKartoElementsData
            params["godlo"] = godlo
            params["skala"] = skala
            wizualizacja_karto = Wizualizacja_karto(**params)
            wizKartoList.append(wizualizacja_karto)
        # print("wizKartoElement: ", wizKartoElement)
        # print("wizKartoElementsData: ", wizKartoElementsData)
        # print("godlo: ", godlo)
        # print("slownik: ", params)
        return wizKartoList
    else:
        return None