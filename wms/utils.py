import re
import urllib.error
import xml.etree.ElementTree as ET

from ..constants import TIMEOUT_MS, WMS_NAMESPACES
from ..utils import remove_duplicates_from_list_of_dicts
from ..network_utils import NetworkUtils

expr = re.compile(r"\{{1}.*\}{1}")

def getQueryableLayersFromWMS(wmsUrl):
    """Lista dostępnych warstw z usługi WMS"""

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetCapabilities',
    }
    network_utils = NetworkUtils()
    success, result = network_utils.fetchContent(wmsUrl, params=PARAMS, timeout_ms=TIMEOUT_MS * 2)

    if not success:
        return False, result

    content = result
    queryableLayers = []

    try:
        root = ET.fromstring(content)
        for layerET in root.findall('.//xmlns:Layer[@queryable="1"]', WMS_NAMESPACES):
            nameET = layerET.find('./xmlns:Name', WMS_NAMESPACES)
            if nameET is not None:
                queryableLayers.append(nameET.text)
                
        queryableLayers = remove_duplicates_from_list_of_dicts(queryableLayers)
        
        return True, queryableLayers
        
    except ET.ParseError:
        return False, "Serwer zwrócił dane w niepoprawnym formacie (oczekiwano XML)."
    except Exception as e:
        return False, f"Błąd pobierania warstw WMS: {str(e)}"


def get_wms_objects(request_response):
    if not request_response[0]:
        return None
    req_elements = expr.findall(request_response[1])
    req_list = []
    for req_element in req_elements:
        element = req_element.strip("{").strip("}").split(',')
        attributes = {}
        for el in element:
            item = el.strip().split(':')
            key = item[0].strip('"')
            val = item[1].strip('"')
            if len(item) > 2:
                val = ":".join(item[1:]).strip('"')
            attributes[key] = val
        req_list.append(attributes)
    return remove_duplicates_from_list_of_dicts(req_list)




if __name__ == "__main__":
    # print(getQueryableLayersFromWMS('https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladKRON86'))
    print(getQueryableLayersFromWMS('https://mapy.geoportal.gov.pl/wss/service/PZGIK/mapy/WMS/SkorowidzVMap'))