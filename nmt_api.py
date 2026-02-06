from .constants import NMT_EVRF_WMS_URL, NMT_GRID5M_WMS_URL, NMT_KRON86_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS
from . import service_api
from .wms.utils import getWmsObject
from .utils import remove_duplicates_from_list_of_dicts

def getNmtListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    
    bbox = '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50)
    
    def getWmsData(url):
        layers = service_api.getAllLayers(url=url, service=WMS_GET_FEATURE_INFO_PARAMS['SERVICE'])
        if not layers:
            return False, None
            
        params = WMS_GET_FEATURE_INFO_PARAMS.copy()
        params.update({
            'layers': ','.join(layers),
            'query_layers': ','.join(layers),
            'bbox': bbox
        })
        return service_api.getRequest(params=params, url=url)

    wms_objects = []
    
    if isEvrf2007:
        resp_1m = getWmsData(NMT_EVRF_WMS_URL)
        if resp_1m[0]:
            wms_objects += getWmsObject(resp_1m)
            
        resp_5m = getWmsData(NMT_GRID5M_WMS_URL)
        if resp_5m[0]:
            wms_objects += getWmsObject(resp_5m)
    else:
        resp_kron = getWmsData(NMT_KRON86_WMS_URL)
        if resp_kron[0]:
            wms_objects += getWmsObject(resp_kron)

    if wms_objects:
        return True, remove_duplicates_from_list_of_dicts(wms_objects)
    else:
        return False, "Nie znaleziono danych NMT dla tego obszaru."


