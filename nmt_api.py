import re
from . import service_api
from .models import Nmt


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeWUkladzieKRON86?"
c = re.compile("\{{1}.*\}{1}")


def getRequest(params):
    return service_api.getRequest(params=params, url=URL)


def retreiveFile(url, destFolder):
    return service_api.retreiveFile(url=url, destFolder=destFolder)


def getNmtListbyPoint1992(point):
    x = point.x()
    y = point.y()

    LAYERS = [
        'Uk%C5%82ad%20wysoko%C5%9Bciowy%20PL-KRON86-NH',
        'KRON86_XYZ_GRID',
        'KRON86_XYZ_GRID_Zasiegi',
        'KRON86_ARC_INFO_GRID',
        'KRON86_ARC_INFO_GRID_Zasiegi'
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
    resp = getRequest(PARAMS)

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
        return nmtList
    else:
        return None