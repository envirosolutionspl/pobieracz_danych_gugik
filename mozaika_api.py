from .wms.utils import get_wms_objects
from . import service_api


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/LinieMozaikowania?"

def getMozaikaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania linii mozaikowania na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

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
    return get_wms_objects(resp)
