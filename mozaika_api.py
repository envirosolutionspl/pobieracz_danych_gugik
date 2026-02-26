from .constants import MOZAIKA_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS, MOZAIKA_SKOROWIDZE_LAYERS
from .wms.utils import getWmsObjects
from .utils import ServiceAPI

def getMozaikaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania linii mozaikowania na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(MOZAIKA_SKOROWIDZE_LAYERS),
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'query_layers': ','.join(MOZAIKA_SKOROWIDZE_LAYERS)
    })
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=params, url=MOZAIKA_WMS_URL)
    return getWmsObjects(resp)
