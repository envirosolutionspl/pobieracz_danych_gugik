# -*- coding: utf-8 -*-
from .constants import ZDJECIA_LOTNICZE_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS
from .utils import ServiceAPI
from .wms.utils import getWmsObjects


def getZdjeciaLotniczeListbyPoint1992(point):

    """Zwraca listę dostępnych do pobrania zdjęć lotniczych na podstawie
    zapytania GetFeatureInfo z usługi WMS"""

    x = point.x()
    y = point.y()
    service_api = ServiceAPI()

    layers = service_api.getAllLayers(url=ZDJECIA_LOTNICZE_WMS_URL, service='WMS')

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(layers),
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'query_layers': ','.join(layers)
    })

    resp = service_api.getRequest(params=params, url=ZDJECIA_LOTNICZE_WMS_URL)
    return _convertAttributes(getWmsObjects(resp))


def _convertAttributes(elems_list):
    for elem in elems_list:
        if 'nrZdjÄcia' in elem:
            elem['nrZdjecia'] = elem.get('nrZdjÄcia')
        if 'nrZdjÄ\x99cia' in elem:
            elem['nrZdjecia'] = elem.get('nrZdjÄ\x99cia')
        elem['url'] = elem.get('adresUrlMiniatur') or 'brak zdjęcia'
    return elems_list
