# -*- coding: utf-8 -*-
from . import service_api
from .models.wms import get_wms_objects

URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Zasiegi_zdj_lot?"


def getZdjeciaLotniczeListbyPoint1992(point):

    """Zwraca listę dostępnych do pobrania zdjęć lotniczych na podstawie
    zapytania GetFeatureInfo z usługi WMS"""

    x = point.x()
    y = point.y()

    layers = service_api.getAllLayers(url=URL,service='WMS')

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
    resp = service_api.getRequest(params=PARAMS, url=URL)
    return _convert_attributes(get_wms_objects(resp))


def _convert_attributes(elems_list):
    for elem in elems_list:
        if hasattr(elem, 'nrZdjÄcia'):
            elem.nrZdjecia = getattr(elem, 'nrZdjÄcia')
        if hasattr(elem, 'adresUrlMiniatur') and hasattr(elem, 'url'):
            elem.url = 'brak zdjęcia' if elem.adresUrlMiniatur == '' else elem.adresUrlMiniatur
    return elems_list
