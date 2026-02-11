import requests, re
import xml.etree.ElementTree as ET
from .httpsAdapter import get_legacy_session
from ..constants import WFS_FILTER_KEYS, WFS_ATTRIBUTES, VALUE_ALL
from qgis.core import QgsMessageLog

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
        with get_legacy_session().get(url=wfsUrl, params=PARAMS, verify=False) as resp:
            r_txt = resp.text
            if resp.status_code == 200:
                typenamesDict = {}
                root = ET.fromstring(r_txt)
                for featureType in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
                    name = featureType.find('.xmlns:Name', ns).text
                    title = featureType.find('.xmlns:Title', ns).text
                    typenamesDict[title] = name
                return True, typenamesDict
            else:
                return False, f'Błąd {resp.status_code}'
    except requests.exceptions.ConnectionError:
        return False, "Błąd połączenia"

def roundCoordinatesOfWkt(wkt):
    c = re.compile(r'(\d+).(\d+)')
    return c.sub(r'\1', wkt)

def filterWfsFeaturesByUsersInput(features, filters):
    """Filtrowanie warstw zgodnie z parametrami wpisanymi przez użytkownika"""
    filtered_features = []
    
    # Skróty dla czytelności
    fk = WFS_FILTER_KEYS
    attr = WFS_ATTRIBUTES

    # Pre-cache constant filter values
    filter_kolor = filters[fk['COLOR']]
    is_color_active = filter_kolor != VALUE_ALL
    
    filter_zrodlo = filters[fk['SOURCE']]
    is_zrodlo_active = filter_zrodlo != VALUE_ALL
    
    filter_crs = filters[fk['CRS']]
    is_crs_active = filter_crs != VALUE_ALL
    
    min_val_pixels = filters[fk['PIXEL_FROM']]
    max_val_pixels = filters[fk['PIXEL_TO']]
    is_pixel_filter_active = min_val_pixels > 0 or max_val_pixels > 0

    for f in features:
        # Kolor
        if is_color_active and str(f[attr['COLOR']]) != filter_kolor:
            continue
        # Źródło
        if is_zrodlo_active and str(f[attr['SOURCE']]) != filter_zrodlo:
            continue
        # CRS
        if is_crs_active and filter_crs not in str(f[attr['CRS']]):
            continue
        # Piksel
        if is_pixel_filter_active:
            try:
                pix_val = float(f[attr['PIXEL']])
                if min_val_pixels > 0 and pix_val < min_val_pixels:
                    continue
                if max_val_pixels > 0 and pix_val > max_val_pixels:
                    continue
            except TypeError:
                QgsMessageLog.logMessage('Pusta wartość pola pikseli. Zignorowano filtr pikseli.')
                pass
            except KeyError:
                QgsMessageLog.logMessage('Brak pola pikseli. Zignorowano filtr pikseli.')
                pass 
            except Exception as e:
                QgsMessageLog.logMessage(f'Wystąpił błąd podczas filtrowania pikseli: {str(e)}')
                pass # jeśli brak pola piksel, nie odrzucaj

        filtered_features.append(f)

    return filtered_features
