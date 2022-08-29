import re
from . import service_api
from .models import Linie_mozaikowania


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/LinieMozaikowania?"
c = re.compile("\{{1}.*\}{1}")


def getMozaikaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania linii mozaikowania na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()
    print("x: ", x)
    print("y: ", y)
    LAYERS = [
        'SkorowidzLiniiMozaikowania'
    ]
    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
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
        mozaikowanie = c.findall(resp[1])
        mozaikaList = []
        for mozaika in mozaikowanie:
            element = mozaika.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            linie_mozaikowania = Linie_mozaikowania(**params)
            mozaikaList.append(linie_mozaikowania)
        # print("mozaikaList: ", mozaikaList)
        return mozaikaList
    else:
        return None
