from .constants import NMPT_EVRF_WMS_URL, NMPT_KRON86_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS
from .utils import ServiceAPI
from .wms.utils import getWmsObjects


def getNmptListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMPT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()
    _url = NMPT_EVRF_WMS_URL if isEvrf2007 else NMPT_KRON86_WMS_URL
    layers = service_api.getAllLayers(url=_url, service=WMS_GET_FEATURE_INFO_PARAMS['SERVICE'])
    if not layers:
        return []

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(layers),
        'query_layers': ','.join(layers),
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50)
    })
    
    resp = service_api.getRequest(params=params, url=_url)
    return getWmsObjects(resp)
