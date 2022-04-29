import re
from . import service_api
from .models import Nmt
from .wms import utils


c = re.compile("\{{1}.*\}{1}")


def getNmptListbyPoint1992(point, isEvrf2007):
    """Pobiera listę dostępnych danych NMPT dla punktu o współrzędnych w układzie PUWG1992"""
    x = point.x()
    y = point.y()

    if isEvrf2007:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladEVRF2007?"
        # LAYERS = [
        #     'Układ wysokościowy PL-EVRF2007-NH',
        #     'EVRF2007_ARC_INFO_GRID_Zasiegi',
        #     'EVRF2007_ARC_INFO_GRID'
        # ]
    else:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladKRON86?"
        # LAYERS = [
        #     # 'Układ wysokościowy PL-KRON86-NH',
        #     'SkorowidzeNMPT2017iStarsze',
        #     'SkorowidzeNMPT2018',
        #     'SkorowidzeNMPT2019'
        # ]

    """dynamiczne pobieranie dostępnych warstw"""
    layersResp = utils.getQueryableLayersFromWMS(URL)
    if layersResp[0]:
        LAYERS = layersResp[1]
    else:
        return layersResp

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

    if resp[0]:
        nmtElements = c.findall(resp[1])
        nmtList = []
        for nmtElement in nmtElements:
            element = nmtElement.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            nmt = Nmt(**params)
            nmtList.append(nmt)
        return True, nmtList
    else:
        return resp