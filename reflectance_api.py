import datetime

from .constants import ODBICIOWOSC_WMS_URL, ODBICIOWOWSC_SKOROWIDZE_LAYERS
from . import service_api
from .wms.utils import get_wms_objects


def getReflectanceListbyPoint1992(point):
    x = point.x()
    y = point.y()

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.3.0',
        'layers': ','.join(ODBICIOWOWSC_SKOROWIDZE_LAYERS),
        'styles': '',
        'crs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(ODBICIOWOWSC_SKOROWIDZE_LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }

    resp = service_api.getRequest(params=PARAMS, url=ODBICIOWOSC_WMS_URL)
    return _convert_attributes(get_wms_objects(resp))


def _convert_attributes(elems_list):
    for elem in elems_list:
        if 'aktualnosc' in elem:
            elem['aktualnosc'] = datetime.datetime.strptime(elem.get('aktualnosc'), '%Y-%m-%d').date()
        if 'wielkoscPiksela' in elem:
            elem['wielkoscPiksela'] = float(elem.get('wielkoscPiksela'))
        if 'zakresIntensywnosci' in elem:
            elem['elemzakresIntensywnosci'] = int(elem.get('zakresIntensywnosci'))
        if 'aktualnoscRok' in elem:
            elem['aktualnoscRok'] = int(elem.get('aktualnoscRok'))
        if 'dt_pzgik' in elem:
            elem['dt_pzgik'] = str(elem.get('dt_pzgik'))
    return elems_list
