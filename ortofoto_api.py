import requests, re
from .models import Ortofotomapa
import os, asyncio, time

URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/SkorowidzeWgAktualnosci?"
c = re.compile("\{{1}.*\}{1}")



def getRequest(params):
    try:
        r = requests.get(url=URL, params=params)
    except requests.exceptions.ConnectionError:
        time.sleep(0.4)
        try:
            r = requests.get(url=URL, params=params)
        except requests.exceptions.ConnectionError:
            return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        return True, r_txt
    else:
        return False, "Błąd %d" % r.status_code

def retreiveFile(url, destFolder):
    r = requests.get(url)
    path = os.path.join(destFolder, url.split('/')[-1])
    try:
        with open(path, 'wb') as f:
            f.write(r.content)
        # print('pobrano plik ', url.split('/')[-1])
        return [True]
    except IOError:
        return False, "Błąd zapisu pliku"

def getOrtoListbyPoint1992(point):
    x = point.x()
    y = point.y()
    LAYERS = [
        'SkorowidzeOrtofotomapyZasiegiStarsze',
        'SkorowidzeOrtofotomapyStarsze',
        'SkorowidzeOrtofotomapyZasiegi2018',
        'SkorowidzeOrtofotomapy2018',
        'SkorowidzeOrtofotomapyZasiegi2019',
        'SkorowidzeOrtofotomapy2019',
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
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
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
        ortos = c.findall(resp[1])
        ortofotomapaList = []
        for orto in ortos:
            element = orto.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                # print(el)
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    # print('---',item)
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            ortofotomapa = Ortofotomapa(**params)
            ortofotomapaList.append(ortofotomapa)
        # for el in ortofotomapaList:
        #     print(el.url, el.godlo, el.wielkoscPiksela, el.kolor, el.aktualnoscRok, el.aktualnosc)
        return ortofotomapaList
    else:
        # print(resp[1])
        return None