import re
import urllib.error
import xml.etree.ElementTree as ET
from ..constants import TIMEOUT_MS
from ..network_utils import NetworkUtils

def getTypenamesFromWFS(wfsUrl):
    """Lista dostępnych warstw z usługi WFS"""
    ns = {'ows': "http://www.opengis.net/ows/1.1",
          'fes': "http://www.opengis.net/fes/2.0",
          'gugik': "http://www.gugik.gov.pl",
          'gml': "http://www.opengis.net/gml/3.2",
          'wfs': "http://www.opengis.net/wfs/2.0",
          'xlink': "http://www.w3.org/1999/xlink",
          'xsi': "http://www.w3.org/2001/XMLSchema-instance",
          'xmlns': "http://www.opengis.net/wfs/2.0"
          }
    PARAMS = {
        'SERVICE': 'WFS',
        'request': 'GetCapabilities',
    }
    try:
        content = NetworkUtils.fetch_content(wfsUrl, params=PARAMS, timeout_ms=TIMEOUT_MS * 2)
        typenamesDict = {}
        root = ET.fromstring(content)
        for featureType in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
            name = featureType.find('.xmlns:Name', ns).text
            title = featureType.find('.xmlns:Title', ns).text
            typenamesDict[title] = name
        return True, typenamesDict
    except TimeoutError:
        return False, "Przekroczono czas oczekiwania na odpowiedź serwera WFS."
    except ConnectionError:
        return False, "Błąd połączenia z serwerem WFS. Sprawdź połączenie internetowe."
    except urllib.error.HTTPError as e:
        return False, f"Serwer WFS zwrócił błąd HTTP {e.code}: {e.reason}"
    except ET.ParseError:
        return False, "Serwer zwrócił dane w niepoprawnym formacie (oczekiwano XML)."
    except Exception as e:
        return False, f"Nieoczekiwany błąd przy pobieraniu warstw WFS: {str(e)}"

def roundCoordinatesOfWkt(wkt):
    c = re.compile(r'(\d+).(\d+)')
    return c.sub(r'\1', wkt)

