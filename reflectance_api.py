import datetime

from .constants import ODBICIOWOSC_WMS_URL, ODBICIOWOWSC_SKOROWIDZE_LAYERS, WMS_GET_FEATURE_INFO_PARAMS
from .utils import ServiceAPI
from .wms.utils import getWmsObjects


def getReflectanceListbyPoint1992(point):
    x = point.x()
    y = point.y()
    service_api = ServiceAPI()

    params = WMS_GET_FEATURE_INFO_PARAMS.copy()
    params.update({
        'layers': ','.join(ODBICIOWOWSC_SKOROWIDZE_LAYERS),
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
        'query_layers': ','.join(ODBICIOWOWSC_SKOROWIDZE_LAYERS)
    })

    resp = service_api.getRequest(params=params, url=ODBICIOWOSC_WMS_URL)
    return _convertAttributes(getWmsObjects(resp))


def _convertAttributes(elems_list):
    """
    Konwertuje atrybuty elementów WMS na odpowiednie typy.
    Zapewnia bezpieczeństwo typów danych, przy np. porównywaniu wartości liczbowych.
    
    :param elems_list: Lista elementów WMS.
    :return: Lista elementów WMS z poprawnymi typami atrybutów.
    """
    for elem in elems_list:
        if 'aktualnosc' in elem:
            elem['aktualnosc'] = datetime.datetime.strptime(elem.get('aktualnosc'), '%Y-%m-%d').date()
        if 'wielkoscPiksela' in elem:
            elem['wielkoscPiksela'] = float(elem.get('wielkoscPiksela'))
        if 'zakresIntensywnosci' in elem:
            elem['zakresIntensywnosci'] = int(elem.get('zakresIntensywnosci'))
        if 'aktualnoscRok' in elem:
            elem['aktualnoscRok'] = int(elem.get('aktualnoscRok'))
        if 'dt_pzgik' in elem:
            elem['dt_pzgik'] = str(elem.get('dt_pzgik'))
    return elems_list
