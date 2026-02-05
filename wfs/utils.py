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
    
    # Pre-cache constant filter values
    f_kolor = filters['kolor']
    f_kolor_active = f_kolor != "wszystkie"
    
    f_zrodlo = filters['zrodlo_danych']
    f_zrodlo_active = f_zrodlo != "wszystkie"
    
    f_crs = filters['uklad_xy']
    f_crs_active = f_crs != "wszystkie"
    
    val_from = filters['piksel_od']
    val_to = filters['piksel_do']
    pixel_filter_active = val_from > 0 or val_to > 0

    for f in features:
        # Kolor
        if f_kolor_active and str(f['kolor']) != f_kolor:
            continue
        # Źródło
        if f_zrodlo_active and str(f['zrodlo_danych']) != f_zrodlo:
            continue
        # CRS
        if f_crs_active:
             if f_crs not in str(f['uklad_xy']):
                continue
        # Piksel
        if pixel_filter_active:
            try:
                pix_val = float(f['piksel'])
                if val_from > 0 and pix_val < val_from:
                    continue
                if val_to > 0 and pix_val > val_to:
                    continue
            except: 
                pass # jeśli brak pola piksel, nie odrzucaj

        filtered_features.append(f)

    return filtered_features
