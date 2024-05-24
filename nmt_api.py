import re
from . import service_api
from .models import Nmt
from .wms import utils


c = re.compile(r"\{{1}.*\}{1}")


def getNmtListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()
    URL2 = None
    if isEvrf2007:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladEVRF2007?"
        URL2 = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SheetsGrid5mEVRF2007?"

        layers2 = service_api.getAllLayers(url=URL2, service='WMS')
        layers = layers2


    else:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladKRON86?"

        layers = service_api.getAllLayers(url=URL, service='WMS')

    # """dynamiczne pobieranie dostępnych warstw"""
    # layersResp = utils.getQueryableLayersFromWMS(URL)
    # if layersResp[0]:
    #     LAYERS = layersResp[1]
    # else:
    #     return layersResp


    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.3.0',
        'layers': ','.join(layers),
        'styles': '',
        'crs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (y-50, x-50, y+50, x+50),
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
    # obsługa drugiego URLa do danych NMT
    resp2 = (False, None)
    if URL2 is not None:
        resp2 = service_api.getRequest(params=PARAMS, url=URL2)
    if resp[0] or resp2[0]:
        lista = []
        if resp[0]:
            lista += createList(resp)
        if resp2[0]:
            lista += createList(resp2)
        return True,  lista
    else:
        return resp


def createList(resp):
    nmtElements = c.findall(resp[1])
    nmtList = []
    for nmtElement in nmtElements:
        element = nmtElement.strip("{").strip("}").split(',')
        # print(element)
        params = {}
        for el in element:
            item = el.strip().split(':')
            val = item[1].strip('"')
            if len(item) > 2:
                val = ":".join(item[1:]).strip('"')
            params[item[0]] = val
        nmt = Nmt(**params)
        nmtList.append(nmt)
    return nmtList
