import requests, re
import xml.etree.ElementTree as ET

def getQueryableLayersFromWMS(wmsUrl):
    """Lista dostępnych warstw z usługi WMS"""
    ns = {'sld': "http://www.opengis.net/sld",
          'ms': "http://mapserver.gis.umn.edu/mapserver",
          'xlink': "http://www.w3.org/1999/xlink",
          'xsi': "http://www.w3.org/2001/XMLSchema-instance",
          'xmlns': "http://www.opengis.net/wms"
          }
    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetCapabilities',
    }
    try:
        r = requests.get(url=wmsUrl, params=PARAMS, verify=False)
    except requests.exceptions.ConnectionError:
        return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        queryableLayers = []
        root = ET.fromstring(r_txt)
        for layerET in root.findall('.//xmlns:Layer[@queryable="1"]', ns):
            nameET = layerET.find('./xmlns:Name', ns)
            if nameET is not None:
                queryableLayers.append(nameET.text)
        return True, queryableLayers
    else:
        return False, "Błąd %d" % r.status_code


if __name__ == "__main__":
    # print(getQueryableLayersFromWMS('https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladKRON86'))
    print(getQueryableLayersFromWMS('https://mapy.geoportal.gov.pl/wss/service/PZGIK/mapy/WMS/SkorowidzVMap'))