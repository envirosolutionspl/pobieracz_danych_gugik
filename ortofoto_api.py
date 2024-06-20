from .wms.utils import get_wms_objects
from . import service_api


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/SkorowidzeWgAktualnosci?"

def getOrtoListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania ortofotomap na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    layers = service_api.getAllLayers(url=URL, service='WMS')

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.3.0',
        'layers': ','.join(layers),
        'styles': '',
        'crs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
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
    return get_wms_objects(resp)
