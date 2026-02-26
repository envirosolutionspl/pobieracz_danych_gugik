from .constants import ORTOFOTOMAPA_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS
from .wms.utils import getWmsObjects
from .utils import ServiceAPI

def getOrtoListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania ortofotomap na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()
    layers = service_api.getAllLayers(url=ORTOFOTOMAPA_WMS_URL, service='WMS')

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'version': '1.3.0',
        'layers': ','.join(layers),
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
        'query_layers': ','.join(layers)
    })

    resp = service_api.getRequest(params=params, url=ORTOFOTOMAPA_WMS_URL)
    return getWmsObjects(resp)
