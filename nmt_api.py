from .constants import NMT_EVRF_WMS_URL, NMT_GRID5M_WMS_URL, NMT_KRON86_WMS_URL
from .utils import ServiceAPI
from .wms.utils import getWmsObjects

def getNmtListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()
    if isEvrf2007:
        layers = service_api.getAllLayers(url=NMT_GRID5M_WMS_URL, service='WMS')
    else:
        layers = service_api.getAllLayers(url=NMT_KRON86_WMS_URL, service='WMS')

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
    resp = service_api.getRequest(params=PARAMS, url=NMT_EVRF_WMS_URL if isEvrf2007 else NMT_KRON86_WMS_URL)
    evrf_resp = service_api.getRequest(params=PARAMS, url=NMT_GRID5M_WMS_URL) if isEvrf2007 else (False, None)


    if resp[0] or evrf_resp[0]:
        wms_objects = []
        if resp[0]:
            wms_objects += getWmsObjects(resp)
        if evrf_resp[0]:
            wms_objects += getWmsObjects(evrf_resp)
        return True, wms_objects

    else:
        return resp


