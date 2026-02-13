import re

from .constants import (
    WIZUALIZACJA_KARTO_WMS_URL, 
    WIZUALIZACJA_KARTO_CONFIG
)
from .utils import ServiceAPI
from .models import Wizualizacja_karto

#TODO zmiana sposobu zapisu danych z requesta na słownik jak w innych przypadkach
def getWizualizacjaKartoListbyPoint1992(point, skala):
    """Zwraca listę dostępnych do pobrania wizualizacji kartograficznych BDOT10k na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()
    
    config = WIZUALIZACJA_KARTO_CONFIG.get(skala)

    layers = config['layers']
    skala_m = config['label']

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(layers),
        'bbox': '%f,%f,%f,%f' % (x - 50, y - 50, x + 50, y + 50),
        'query_layers': ','.join(layers)
    }
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=params, url=WIZUALIZACJA_KARTO_WMS_URL)
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
            id = id + 1
            params["url"] = wizKartoElement
            params["data"] = wizKartoElementsData
            params["godlo"] = godlo
            params["skala"] = skala_m
            wizualizacja_karto = Wizualizacja_karto(**params)
            wizKartoList.append(wizualizacja_karto)
        # print("wizKartoElement: ", wizKartoElement)
        # print("wizKartoElementsData: ", wizKartoElementsData)
        # print("godlo: ", godlo)
        # print("slownik: ", params)
        return wizKartoList
    else:
        return None
