from .constants import AEROTRAINGULACJA_WMS_URL, AEROTRAINGULACJA_SKOROWIDZE_LAYERS, WMS_GET_FEATURE_INFO_PARAMS
from .wms.utils import getWmsObjects
from .utils import ServiceAPI



def getAerotriangulacjaListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania areotriangulacji na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'version': '1.1.1',
        'layers': ','.join(AEROTRAINGULACJA_SKOROWIDZE_LAYERS),
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'query_layers': ','.join(AEROTRAINGULACJA_SKOROWIDZE_LAYERS)
    })
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=params, url=AEROTRAINGULACJA_WMS_URL)
    return getWmsObjects(resp)
