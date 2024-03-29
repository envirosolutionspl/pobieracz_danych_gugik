import requests, re
import xml.etree.ElementTree as ET
from .httpsAdapter import get_legacy_session

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
        #r = requests.get(url=wfsUrl, params=PARAMS, verify=False)
        r = get_legacy_session().get(url=wfsUrl, params=PARAMS, verify=False)
    except requests.exceptions.ConnectionError:
        return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        typenamesDict = {}
        root = ET.fromstring(r_txt)
        for featureType in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
            name = featureType.find('.xmlns:Name', ns).text
            title = featureType.find('.xmlns:Title', ns).text
            typenamesDict[title] = name

        return True, typenamesDict
    else:

        return False, "Błąd %d" % r.status_code

def roundCoordinatesOfWkt(wkt):
    c = re.compile(r'(\d+).(\d+)')
    return c.sub(r'\1', wkt)

