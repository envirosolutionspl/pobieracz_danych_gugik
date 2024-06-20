import datetime

from . import service_api
from .wms.utils import get_wms_objects


def getReflectanceListbyPoint1992(point):
    x = point.x()
    y = point.y()

    URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/OI/WMS/SkorowidzeObrazowIntensywnosci?"
    LAYERS = [
            'SkorowidzeOI',
            'SkorowidzeOIZasieg'
        ]

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.3.0',
        'layers': ','.join(LAYERS),
        'styles': '',
        'crs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }

    resp = service_api.getRequest(params=PARAMS, url=URL)
    return _convert_attributes(get_wms_objects(resp))


def _convert_attributes(elems_list):
    for elem in elems_list:
        if hasattr(elem, 'aktualnosc'):
            elem.aktualnosc = datetime.datetime.strptime(elem.aktualnosc, '%Y-%m-%d').date()
        if hasattr(elem, 'wielkoscPiksela'):
            elem.wielkoscPiksela = float(elem.wielkoscPiksela)
        if hasattr(elem, 'zakresIntensywnosci'):
            elem.elemzakresIntensywnosci = int(elem.zakresIntensywnosci)
        if hasattr(elem, 'aktualnoscRok'):
            elem.aktualnoscRok = int(elem.aktualnoscRok)
        if hasattr(elem, 'dt_pzgik'):
            elem.dt_pzgik = str(elem.dt_pzgik)
    return elems_list
