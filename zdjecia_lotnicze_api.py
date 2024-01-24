# -*- coding: utf-8 -*-
import re
from . import service_api
from .models import ZdjeciaLotnicze


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Zasiegi_zdj_lot?"
c = re.compile("\{{1}.*\}{1}")


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
    if resp[0]:
        zdj_lot = c.findall(resp[1])
        zdjeciaLotniczeList = []
        for zdj in zdj_lot:
            element = zdj.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                if item[0] == 'nrZdjÄcia':
                    item[0] = 'nrZdjecia'
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            zdjecia_lotnicze = ZdjeciaLotnicze(**params)
            # print("lista: ", params)
            zdjeciaLotniczeList.append(zdjecia_lotnicze)
        return zdjeciaLotniczeList
    else:
        return None
