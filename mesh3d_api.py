import re

from .wms.utils import get_wms_objects
from .service_api import ServiceAPI

URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/ModeleSiatkowe3D?"
c = re.compile(r"\{{1}.*\}{1}")


def getMesh3dListbyPoint1992(point):
    x = point.x()
    y = point.y()
    LAYERS = [
        'SkorowidzeModeleSiatkowe3D'
    ]

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }
    service_api = ServiceAPI()
    resp = service_api.getRequest(params=PARAMS, url=URL)
    return get_wms_objects(resp)
