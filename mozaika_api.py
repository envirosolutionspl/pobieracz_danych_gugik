from .constants import MOZAIKA_WMS_URL, MOZAIKA_SKOROWIDZE_LAYERS
from .wms.utils import getWmsObject
from . import service_api

def getMozaikaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania linii mozaikowania na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(MOZAIKA_SKOROWIDZE_LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(MOZAIKA_SKOROWIDZE_LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }

    resp = service_api.getRequest(params=PARAMS, url=MOZAIKA_WMS_URL)
    return getWmsObject(resp)
