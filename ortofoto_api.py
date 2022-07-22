import re
from . import service_api
from .models import Ortofotomapa


URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/SkorowidzeWgAktualnosci?"
c = re.compile("\{{1}.*\}{1}")


def getOrtoListbyPoint1992(point):
    """Zwraca listę dostępnych do pobrania ortofotomap na podstawie
    zapytania GetFeatureInfo z usługi WMS"""
    x = point.x()
    y = point.y()
    LAYERS = [
        'SkorowidzeOrtofotomapyZasiegiStarsze',
        'SkorowidzeOrtofotomapyStarsze',
        'SkorowidzeOrtofotomapyZasiegi2021',
        'SkorowidzeOrtofotomapy2021',
        'SkorowidzeOrtofotomapyZasiegi2022',
        'SkorowidzeOrtofotomapy2022',
        'SkorowidzeOrtofotomapyZasiegi2020',
        'SkorowidzeOrtofotomapy2020'
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
        ortos = c.findall(resp[1])
        ortofotomapaList = []
        for orto in ortos:
            element = orto.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            ortofotomapa = Ortofotomapa(**params)
            ortofotomapaList.append(ortofotomapa)
        return ortofotomapaList
    else:
        return None
