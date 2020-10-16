import re
from . import service_api
from .models import Reflectance


c = re.compile("\{{1}.*\}{1}")


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

    if resp[0]:
        return createList(resp)
    else:
        return None


def createList(resp):
    reflectanceElements = c.findall(resp[1])
    reflectanceList = []
    for reflectanceElement in reflectanceElements:
        element = reflectanceElement.strip("{").strip("}").split(',')
        # print(element)
        params = {}
        for el in element:
            item = el.strip().split(':')
            val = item[1].strip('"')
            if len(item) > 2:
                val = ":".join(item[1:]).strip('"')
            params[item[0]] = val
        reflectance = Reflectance(**params)
        reflectanceList.append(reflectance)
    return reflectanceList