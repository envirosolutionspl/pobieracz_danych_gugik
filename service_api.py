from .constants import TIMEOUT_MS, MAX_ATTEMPTS
from . import utils
import lxml.etree as ET
import os, time, urllib.error
from .network_utils import NetworkUtils

def getRequest(params, url):
    attempt = 0
    while attempt <= MAX_ATTEMPTS:
        try:
            content = NetworkUtils.fetch_content(url, params=params, timeout_ms=TIMEOUT_MS * 2)
            return True, content
        except (TimeoutError, ConnectionError) as e:
            attempt += 1
            if attempt > MAX_ATTEMPTS:
                return False, f'Błąd po {MAX_ATTEMPTS} próbach połączenia: {str(e)}'
            time.sleep(2)
        except urllib.error.HTTPError as e:
            return False, f'Serwer zwrócił błąd HTTP {e.code}: {e.reason}'
        except Exception as e:
            return False, f'Nieoczekiwany błąd sieci: {str(e)}'


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
        cleanup_file(path)
        NetworkUtils.download_file(url, path, obj=obj)
        utils.openFile(destFolder)
        return True, True
    except InterruptedError:
        cleanup_file(path)
        return False, "Pobieranie zostało anulowane."
    except (TimeoutError, ConnectionError, urllib.error.HTTPError) as e:
        cleanup_file(path)
        return False, f"Błąd pobierania pliku: {str(e)}"
    except Exception as e:
        cleanup_file(path)
        return False, f"Nieoczekiwany błąd przy zapisie: {str(e)}"


def getAllLayers(url, service="WMS"):
    # Poprawne parametry GetCapabilities
    params = {
        "SERVICE": service,
        "REQUEST": "GetCapabilities",
        "VERSION": "1.3.0",
    }

    ok, payload = getRequest(params, url)
    if not ok or not payload:
        return []

    # Parsowanie XML
    parser = ET.XMLParser(recover=True)
    try:
        root = ET.fromstring(payload.encode("utf-8"), parser=parser)
    except Exception:
        # gdyby serwer odesłał już bytes w UTF-8
        root = ET.fromstring(payload, parser=parser)

    # Obsługa przestrzeni nazw (lub jej braku)
    #    lxml: root.nsmap może mieć None dla domyślnego ns
    ns_uri = None
    try:
        ns_uri = root.nsmap.get(None)  # domyślna przestrzeń nazw, np. 'http://www.opengis.net/wms'
    except AttributeError:
        ns_uri = None  # brak nsmap -> brak przestrzeni nazw

    layers = []

    if ns_uri:
        # XPath: tylko 'Layer' mające 'Name' -> bierzemy 'Layer/Name'
        ns = {"wms": ns_uri}
        names = root.xpath(".//wms:Capability//wms:Layer[wms:Name]/wms:Name", namespaces=ns)
        layers = [el.text for el in names if el is not None and el.text]
    else:
        # Bez przestrzeni nazw – klasyczne ścieżki
        for layer in root.findall(".//Layer"):
            name_el = layer.find("Name")
            if name_el is not None and name_el.text:
                layers.append(name_el.text)

    # zwróć tylko unikalne nazwy w kolejności wystąpienia
    seen = set()
    unique_layers = []
    for n in layers:
        if n not in seen:
            seen.add(n)
            unique_layers.append(n)

    return unique_layers



def check_internet_connection():
    # próba połączenia z serwerem np. gugik
    try:
        NetworkUtils.fetch_content('https://uldk.gugik.gov.pl/', timeout_ms=TIMEOUT_MS)
        return True
    except Exception:
        return False
    

def isInternetConnected():
    return check_internet_connection()


def cleanup_file(path):
    if os.path.exists(path):
        os.remove(path)


if __name__ == '__main__':
    url = "https://opendata.geoportal.gov.pl/ortofotomapa/73214/73214_897306_N-34-91-C-d-1-4.tif"
    destFolder = "D:/test/orto"
    print(retreiveFile(url=url, destFolder=destFolder))
