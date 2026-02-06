from .constants import NMT_EVRF_WMS_URL, NMT_GRID5M_WMS_URL, NMT_KRON86_WMS_URL
from . import service_api
from .wms.utils import get_wms_objects
from .utils import remove_duplicates_from_list_of_dicts

def getNmtListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    
    bbox = '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50)
    
    def get_wms_data(url):
        layers = service_api.getAllLayers(url=url, service='WMS')
        if not layers:
            return False, None
            
        params = {
            'SERVICE': 'WMS',
            'request': 'GetFeatureInfo',
            'version': '1.3.0',
            'layers': ','.join(layers),
            'styles': '',
            'crs': 'EPSG:2180',
            'bbox': bbox,
            'width': '101',
            'height': '101',
            'format': 'image/png',
            'transparent': 'true',
            'query_layers': ','.join(layers),
            'i': '50',
            'j': '50',
            'INFO_FORMAT': 'text/html'
        }
        return service_api.getRequest(params=params, url=url)

    wms_objects = []
    
    if isEvrf2007:
        resp_1m = get_wms_data(NMT_EVRF_WMS_URL)
        if resp_1m[0]:
            wms_objects += get_wms_objects(resp_1m)
            
        resp_5m = get_wms_data(NMT_GRID5M_WMS_URL)
        if resp_5m[0]:
            wms_objects += get_wms_objects(resp_5m)
    else:
        resp_kron = get_wms_data(NMT_KRON86_WMS_URL)
        if resp_kron[0]:
            wms_objects += get_wms_objects(resp_kron)

    if wms_objects:
        return True, remove_duplicates_from_list_of_dicts(wms_objects)
    else:
        return False, "Nie znaleziono danych NMT dla tego obszaru."


