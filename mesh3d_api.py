import re

from .wms.utils import getWmsObjects
from .utils import ServiceAPI
from .constants import MESH3D_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS, MESH3D_SKOROWIDZE_LAYERS

c = re.compile(r"\{{1}.*\}{1}")


def getMesh3dListbyPoint1992(point):
    x = point.x()
    y = point.y()

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'version': '1.1.1',
        'layers': ','.join(MESH3D_SKOROWIDZE_LAYERS),
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'query_layers': ','.join(MESH3D_SKOROWIDZE_LAYERS)
    })
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=params, url=MESH3D_WMS_URL)
    return getWmsObjects(resp)
