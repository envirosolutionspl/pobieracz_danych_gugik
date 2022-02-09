import re
try:
    from . import service_api
    from .models import Las
except:
    import service_api
    from models import Las


c = re.compile("\{{1}.*\}{1}")


def getLasListbyPoint1992(point, isEvrf2007, isLaz=False):
    x = point.x()
    y = point.y()
    if isEvrf2007:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladEVRF2007?"
        LAYERS = [
            # 'Układ wysokościowy PL-EVRF2007-NH',
            'SkorowidzeLIDAR2019iStarsze', 'SkorowidzeLIDAR2020', 'SkorowidzeLIDAR2021'
        ]
    else:
        URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladKRON86?"
        LAYERS = [
            # 'Układ wysokościowy PL-KRON86-NH',
            'SkorowidzeLIDAR2017iStarsze', 'SkorowidzeLIDAR2018', 'SkorowidzeLIDAR2019'
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
            params['isLaz'] = isLaz
            las = Las(**params)
            lasList.append(las)
        return lasList
    else:
        return None


if __name__ == '__main__':
    from qgis.core import QgsPoint
    print(getLasListbyPoint1992(QgsPoint(504189, 380335), isLaz=True))
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiarowe/5020/5020_452318_M-34-52-C-d-1-3-2.las
# https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiaroweLAZ/5020/5020_452318_M-34-52-C-d-1-3-2.laz