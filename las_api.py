import datetime
from .models.wms import get_wms_objects
try:
    from . import service_api
    from .models import WFS
except:
    import service_api
    from models import WFS


def getLasListbyPoint1992(point, isEvrf2007): #, isLaz=False
    x = point.x()
    y = point.y()
    if isEvrf2007:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladEVRF2007?"
    else:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladKRON86?"
    layers = service_api.getAllLayers(url=URL, service='WMS')
    if not layers:
        return
    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.3.0',
        'layers': ','.join(layers),
        'styles': '',
        'crs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y - 50, x - 50, y + 50, x + 50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(layers),
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
        if hasattr(elem, 'charakterystykaPrzestrzenna'):
            elem.charakterystykaPrzestrzenna = float(elem.charakterystykaPrzestrzenna.split()[0])
        if hasattr(elem, 'bladSredniWysokosci'):
            elem.bladSredniWysokosci = float(elem.bladSredniWysokosci)
        if hasattr(elem, 'bladSredniPolozenia'):
            elem.bladSredniPolozenia = float(elem.bladSredniPolozenia)
        if hasattr(elem, 'aktualnoscRok'):
            elem.aktualnoscRok = int(elem.aktualnoscRok)
    return elems_list


if __name__ == '__main__':
    from qgis.core import QgsPoint
    print(getLasListbyPoint1992(QgsPoint(504189, 380335))) #, isLaz=True
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiarowe/5020/5020_452318_M-34-52-C-d-1-3-2.las
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiaroweLAZ/5020/5020_452318_M-34-52-C-d-1-3-2.laz