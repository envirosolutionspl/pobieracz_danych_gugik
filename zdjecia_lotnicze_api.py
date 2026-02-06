# -*- coding: utf-8 -*-
from .constants import ZDJECIA_LOTNICZE_WMS_URL
from . import service_api
from .wms.utils import getWmsObject


def getZdjeciaLotniczeListbyPoint1992(point):

    """Zwraca listę dostępnych do pobrania zdjęć lotniczych na podstawie
    zapytania GetFeatureInfo z usługi WMS"""

    x = point.x()
    y = point.y()

    layers = service_api.getAllLayers(url=ZDJECIA_LOTNICZE_WMS_URL, service='WMS')

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(layers),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(layers),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }

    resp = service_api.getRequest(params=PARAMS, url=ZDJECIA_LOTNICZE_WMS_URL)
    return _convert_attributes(getWmsObject(resp))


def _convert_attributes(elems_list):
    for elem in elems_list:
        if 'nrZdjÄcia' in elem:
            elem['nrZdjecia'] = elem.get('nrZdjÄcia')
        if 'nrZdjÄ\x99cia' in elem:
            elem['nrZdjecia'] = elem.get('nrZdjÄ\x99cia')
        elem['url'] = elem.get('adresUrlMiniatur') or 'brak zdjęcia'
    return elems_list
