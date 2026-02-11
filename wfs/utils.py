import re
import xml.etree.ElementTree as ET
from ..constants import TIMEOUT_MS, WFS_NAMESPACES, WFS_FILTER_KEYS, WFS_ATTRIBUTES, VALUE_ALL
from ..utils import NetworkUtils, MessageUtils

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
                MessageUtils.pushLogWarning('Pusta wartość pola pikseli. Zignorowano filtr pikseli.')
                pass
            except KeyError:
                MessageUtils.pushLogWarning('Brak pola pikseli. Zignorowano filtr pikseli.')
                pass 
            except Exception as e:
                MessageUtils.pushLogWarning(f'Wystąpił błąd podczas filtrowania pikseli: {str(e)}')
                pass # jeśli brak pola piksel, nie odrzucaj

        filtered_features.append(f)

    return filtered_features
