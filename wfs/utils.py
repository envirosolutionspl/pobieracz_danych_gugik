import re
import urllib.error
import xml.etree.ElementTree as ET
from ..constants import TIMEOUT_MS, WFS_NAMESPACES
from ..network_utils import NetworkUtils

def getTypenamesFromWFS(wfsUrl):
    """Lista dostępnych warstw z usługi WFS"""

    PARAMS = {
        'SERVICE': 'WFS',
        'request': 'GetCapabilities',
    }
    network_utils = NetworkUtils()
    success, result = network_utils.fetchContent(wfsUrl, params=PARAMS, timeout_ms=TIMEOUT_MS * 2)

    if not success:
        return False, result

    content = result 
    typenamesDict = {}

    try:
        root = ET.fromstring(content)   

        for featureType in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', WFS_NAMESPACES):
            name = featureType.find('.xmlns:Name', WFS_NAMESPACES).text
            title = featureType.find('.xmlns:Title', WFS_NAMESPACES).text
            typenamesDict[title] = name
            
        return True, typenamesDict
        
    except ET.ParseError:
        return False, "Serwer zwrócił dane w niepoprawnym formacie (oczekiwano XML)."
    except Exception as e:
        return False, f"Nieoczekiwany błąd przy przetwarzaniu warstw WFS: {str(e)}"

    
def roundCoordinatesOfWkt(wkt):
    c = re.compile(r'(\d+).(\d+)')
    return c.sub(r'\1', wkt)

