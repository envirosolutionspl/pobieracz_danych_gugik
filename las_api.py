import re
from . import service_api
from .models import Las


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomNMT/WMS/SkorowidzeWUkladzieKRON86?"
c = re.compile("\{{1}.*\}{1}")


def getLasListbyPoint1992(point):
    x = point.x()
    y = point.y()

    LAYERS = [
        # 'Układ wysokościowy PL-KRON86-NH',
        'KRON86_LAS',
        'KRON86_LAS_Zasiegi'
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
        lasElements = c.findall(resp[1])
        lasList = []
        for lasElement in lasElements:
            element = lasElement.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            las = Las(**params)
            lasList.append(las)
        return lasList
    else:
        return None