from .constants import NMPT_EVRF_WMS_URL, NMPT_KRON86_WMS_URL
from .service_api import ServiceAPI
from .wms.utils import get_wms_objects


def getNmptListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMPT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()
    _url = NMPT_EVRF_WMS_URL if isEvrf2007 else NMPT_KRON86_WMS_URL
    layers = service_api.getAllLayers(url=_url, service='WMS')

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
    
    resp = service_api.getRequest(params=PARAMS, url=_url)
    return get_wms_objects(resp)
