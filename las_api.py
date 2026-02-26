import datetime

from .constants import LAS_EVRF_WMS_URL, LAS_KRON86_WMS_URL, WMS_GET_FEATURE_INFO_PARAMS
from .wms.utils import getWmsObjects

from .utils import ServiceAPI


def getLasListbyPoint1992(point, isEvrf2007):
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()
    _url = LAS_EVRF_WMS_URL if isEvrf2007 else LAS_KRON86_WMS_URL
    layers = service_api.getAllLayers(url=_url, service='WMS')

    if not layers:
        return
    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(layers),
        'bbox': '%f,%f,%f,%f' % (y - 50, x - 50, y + 50, x + 50),
        'query_layers': ','.join(layers),
    })
    
    resp = service_api.getRequest(params=params, url=_url)

    return _convertAttributes(getWmsObjects(resp))


def _convertAttributes(elems_list):
    for elem in elems_list:
        if 'aktualnosc' in elem:
            elem['aktualnosc'] = datetime.datetime.strptime(elem.get('aktualnosc'), '%Y-%m-%d').date()
        if 'charakterystykaPrzestrzenna' in elem:
            elem['charakterystykaPrzestrzenna'] = float(elem.get('charakterystykaPrzestrzenna').split()[0])
        if 'bladSredniWysokosci' in elem:
            elem['bladSredniWysokosci'] = float(elem.get('bladSredniWysokosci'))
        if 'bladSredniPolozenia' in elem:
            elem['bladSredniPolozenia'] = float(elem.get('bladSredniPolozenia'))
        if 'aktualnoscRok' in elem:
            elem['aktualnoscRok'] = int(elem.get('aktualnoscRok'))
    return elems_list


if __name__ == '__main__':
    from qgis.core import QgsPoint
    print(getLasListbyPoint1992(QgsPoint(504189, 380335))) #, isLaz=True
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiarowe/5020/5020_452318_M-34-52-C-d-1-3-2.las
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiaroweLAZ/5020/5020_452318_M-34-52-C-d-1-3-2.laz