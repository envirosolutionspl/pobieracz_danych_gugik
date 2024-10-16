from qgis.utils import iface

from . import utils
from .wfs.httpsAdapter import get_legacy_session
import lxml.etree as ET
from requests.exceptions import (ConnectionError, ChunkedEncodingError, Timeout)
import os, time, socket


def getRequest(params, url):
    max_attempts = 3
    attempt = 0
    while attempt <= max_attempts:
        if not isInternetConnected():
            return False, 'Połączenie zostało przerwane'
        try:
            with get_legacy_session().get(url=url, params=params, verify=False) as resp:
                if resp.status_code == 200:
                    return True, resp.text
                else:
                    return False, f'Błąd {resp.status_code}'
        except ConnectionError:
            attempt += 1
            time.sleep(2)


def retreiveFile(url, destFolder, obj):
    file_name = url.split('/')[-1]
    if '?' in file_name:
        file_name = (file_name.split('?')[-1].replace('=', '_')) + '.zip'

    if 'Budynki3D' in url:
        if 'LOD1' in url:
            file_name = f"Budynki_3D_LOD1_{file_name}"
        elif 'LOD2' in url:
            file_name = f"Budynki_3D_LOD2_{file_name}"

        if len(url.split('/')) == 9:
            file_name = url.split('/')[6] + '_' + file_name

    elif 'PRG' in url:
        file_name = f"PRG_{file_name}"
    elif 'bdot10k' in url and 'Archiwum' not in url:
        file_name = f"bdot10k_{file_name}"
    elif 'Archiwum' in url and 'bdot10k' in url:
        file_name = "archiwalne_bdot10k_" + url.split('/')[5] + '_' + file_name
    elif 'bdoo' in url:
        file_name = "bdoo_" + 'rok' + url.split('/')[4] + '_' + file_name
    elif 'ZestawieniaZbiorczeEGiB' in url:
        file_name = "ZestawieniaZbiorczeEGiB_" + 'rok' + url.split('/')[4] + '_' + file_name
    elif 'osnowa' in url:
        file_name = f"podstawowa_osnowa_{file_name}"

    path = os.path.join(destFolder, file_name)
    
    try:
        resp = get_legacy_session().get(url=url, verify=False, stream=True)
        chunks_made = 0

        if str(resp.status_code) == '404':
            resp.close()
            return False, "Plik nie istnieje"
        saved = True
        try:
            cleanup_file(path)
            
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    """Pobieramy plik w kawałkach dzięki czemu możliwe jest przerwanie w trakcie pobierania"""

                    if chunks_made % 10000000 == 0:                      
                        if not isInternetConnected():
                            return False, 'Połączenie zostało przerwane'
                        
                    if obj.isCanceled():
                        resp.close()
                        saved = False
                        break
                    f.write(chunk)
                    chunks_made += len(chunk)
                    
        except IOError:
            return False, "Błąd zapisu pliku"
        resp.close()
        if saved:
            utils.openFile(destFolder)
            return True, True
        else:
            cleanup_file(path)
            return False, "Połączenie zostało przerwane"
        
    except (ConnectionError, ChunkedEncodingError):
        cleanup_file(path)
        return False, 'Połączenie zostało przerwane'


def getAllLayers(url, service):
    params = {
        'SERVICE': service,
        'request': 'GetCapabilities',
        'INFO_FORMAT': 'text/html'
    }

    layers = getRequest(params, url)
    
    if layers == None:
        layers = getRequest(params, url)
    
    if not layers[0]:
        return
    
    parser = ET.XMLParser(recover=True)
    tree = ET.ElementTree(ET.fromstring(layers[1][56:].lstrip(), parser=parser))

    # To find elements with tag 'element'
    layers = [el.text for el in tree.iter() if 'Name' in str(el.tag) and str(el.text) != 'WMS']
    return layers


def check_internet_connection():
    try:
        resp = get_legacy_session().get(url='https://uldk.gugik.gov.pl/', verify=False)
        return resp.status_code == 200
    except Timeout:
        return False
    except ConnectionError:
        return False
    

def isInternetConnected():
    try:
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        shutDownConnection(s)
        return True
    except Timeout:
        return False
    except ConnectionError:
        return False


def shutDownConnection(socket):
    socket.close()


def cleanup_file(path):
    if os.path.exists(path):
        os.remove(path)


if __name__ == '__main__':
    url = "https://opendata.geoportal.gov.pl/ortofotomapa/73214/73214_897306_N-34-91-C-d-1-4.tif"
    destFolder = "D:/test/orto"
    print(retreiveFile(url=url, destFolder=destFolder))
