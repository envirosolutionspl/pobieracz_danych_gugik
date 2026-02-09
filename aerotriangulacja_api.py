from .constants import AEROTRAINGULACJA_WMS_URL, AEROTRAINGULACJA_SKOROWIDZE_LAYERS
from .wms.utils import get_wms_objects
from .service_api import ServiceAPI



def getAerotriangulacjaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania areotriangulacji na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(AEROTRAINGULACJA_SKOROWIDZE_LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(AEROTRAINGULACJA_SKOROWIDZE_LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=PARAMS, url=AEROTRAINGULACJA_WMS_URL)
    return get_wms_objects(resp)
