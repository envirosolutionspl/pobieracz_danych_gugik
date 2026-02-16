import os
import xml.etree.ElementTree as ET
from time import sleep
from lxml import etree
from lxml.etree import XMLSyntaxError
from datetime import datetime
from ..utils import NetworkUtils, ServiceAPI
from ..constants import (
    MIN_FILE_SIZE, 
    CAPABILITIES_FILE_NAME, 
    GML_URL_TEMPLATES, 
    STATUS_SUCCESS, 
    STATUS_CANCELED, 
    MSG_CONNECTION_INTERRUPTED,
    MSG_DOWNLOAD_CANCELED
)


class WfsEgib:

    def __init__(self):
        self.service_api = ServiceAPI()
        self.network_utils = NetworkUtils()

    def saveXml(self, folder, url, teryt, obj=None):
        """Zapisuje plik XML dla zapytania getCapabilities"""
        if not self.service_api.checkInternetConnection():
            return MSG_CONNECTION_INTERRUPTED
        
        path = os.path.join(folder, CAPABILITIES_FILE_NAME)

        success, result = self.network_utils.downloadFile(url, path, obj=obj)
        if not success:
            return f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {result}. URL: \n{url}"
            
        return STATUS_SUCCESS

    def workOnXml(self, folder, url, teryt, obj=None):
        """Pracuje na pliku XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane"""
        name_error = self.saveXml(folder, url, teryt, obj=obj)
        name_layers = None
        prefix = None

        if name_error == STATUS_SUCCESS:
            error_reason = None
            try:
                tree = ET.parse(os.path.join(folder, 'egib_wfs.xml'))
                root = tree.getroot()
                name_layers = []
                wfs_ns = {"wfs": "http://www.opengis.net/wfs/2.0"}

                for child in root.findall('./wfs:FeatureTypeList/wfs:FeatureType', wfs_ns):
                    name = child.find('wfs:Name', wfs_ns)
                    if name is not None:
                        name_layers.append(name.text)

                if name_layers:
                    if name_layers[0].startswith('ewns:'):
                        prefix = 'ewns'
                    elif name_layers[0].startswith('ms:'):
                        prefix = 'ms'
            except ET.ParseError:
                error_reason = "Błąd parsowania pliku XML. Serwer zwrócił niepoprawne dane"
            except Exception as e:
                error_reason = f"Błąd przy przetwarzaniu XML: {str(e)}"

            if error_reason:
                name_error = f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {error_reason}. URL: \n{url}"

        return name_error, name_layers, prefix

    def saveGML(self, folder, url, teryt, obj=None):
        """Pobiera dane EGiB dla wszystkich warstw udostępnionych przez powiaty"""
        name_error, name_layers, prefix = self.workOnXml(folder, url, teryt, obj=obj)
        if name_error != STATUS_SUCCESS:
            return name_error

        url_main = url.split('?')[0]
        name_error_lista_brak = []
        name_error_lista = []

        for layer in name_layers:
            if obj and obj.isCanceled():
                return STATUS_CANCELED

            if prefix in GML_URL_TEMPLATES:
                url_gml = GML_URL_TEMPLATES[prefix].format(url_main=url_main, layer=layer)
            else:
                url_gml = GML_URL_TEMPLATES['default'].format(url_main=url_main, layer=layer)

            # skracamy sleep lub dodajemy sprawdzenie po nim
            sleep(0.1) 
            if obj and obj.isCanceled():
                return STATUS_CANCELED

            layer_name = layer.split(':')[-1]
            if not self.service_api.checkInternetConnection():
                return MSG_CONNECTION_INTERRUPTED
            
            layer_path = os.path.join(folder, f"{teryt}_{layer_name}_egib_wfs_gml.gml")
            error_reason = None

            try:
                success, result = self.network_utils.downloadFile(url_gml, layer_path, obj=obj)
                if success: 
                    # Sprawdzenie rozmiaru
                    if os.path.exists(layer_path) and os.path.getsize(layer_path) <= MIN_FILE_SIZE:
                        error_reason = "Za mały rozmiar pliku; błąd pobierania danych (prawdopodobnie brak danych dla tego obszaru)"
                    else:
                        name_error_lista_brak.append(layer_name)
                else:
                    if result == MSG_DOWNLOAD_CANCELED:
                        return STATUS_CANCELED
                    error_reason = result
            
            except IOError:
                error_reason = "Błąd zapisu pliku (IOError)"
            except OSError:
                error_reason = "Błąd zapisu pliku (OSError)"
            except Exception as e:
                error_reason = f"Nieoczekiwany błąd: {e}"

            if error_reason:
                full_msg = f"- (teryt: {teryt}, warstwa {layer_name}) {error_reason}. URL: \n{url_gml}"
                name_error_lista.append(full_msg)

        # --- Generowanie raportu końcowego ---
        if name_error_lista:
            report_parts = ["Nieprawidłowe warstwy: \n\n " + '\n\n '.join(name_error_lista)]
            if name_error_lista_brak:
                report_parts.append("Prawidłowe warstwy:  " + ', '.join(name_error_lista_brak))
            return "\n\n".join(report_parts)
            
        return STATUS_SUCCESS

    def egibWFS(self, teryt, wfs, folder, obj=None):
        """Tworzy nowy folder dla plików XML"""
        wfs = f"{wfs}?service=WFS&request=GetCapabilities"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f'{teryt}_wfs_egib_{timestamp}/')
        os.makedirs(path, exist_ok=True)
        return self.saveGML(path, wfs, teryt, obj=obj)


if __name__ == '__main__':
    wfsEgib = WfsEgib()

