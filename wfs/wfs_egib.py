import os
import xml.etree.ElementTree as ET
from time import sleep
from lxml import etree
from lxml.etree import XMLSyntaxError
from datetime import datetime
from ..service_api import check_internet_connection
from ..network_utils import NetworkUtils
from ..constants import MIN_FILE_SIZE


class WfsEgib:

    def save_xml(self, folder, url, teryt):
        """Zapisuje plik XML dla zapytania getCapabilities"""
        if not check_internet_connection():
            return 'Połączenie zostało przerwane'
        
        path = os.path.join(folder, 'egib_wfs.xml')
        error_reason = None

        try:
            NetworkUtils.download_file(url, path)
        except (IOError, OSError) as e:
            error_reason = f"Błąd zapisu pliku (IOError): {e}"
        except ConnectionError as e:
            error_reason = "Błędy weryfikacji SSL (certyfikat)" if "SSL" in str(e) else f"Błąd połączenia: {e}"
        except TimeoutError:
            error_reason = "Przekroczono czas oczekiwania (Timeout)"
        except Exception as e:
            error_reason = f"Nieoczekiwany błąd: {e}"
            
        if error_reason:
            return f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {error_reason}. URL: \n{url}"
            
        return "brak"

    def work_on_xml(self, folder, url, teryt):
        """Pracuje na pliku XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane"""
        name_error = self.save_xml(folder, url, teryt)
        name_layers = None
        prefix = None

        if name_error == "brak":
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
                    if 'ewns:' in name_layers[0]:
                        prefix = 'ewns'
                    elif 'ms:' in name_layers[0]:
                        prefix = 'ms'
            except ET.ParseError:
                error_reason = "Błąd parsowania pliku XML. Serwer zwrócił niepoprawne dane"
            except Exception as e:
                error_reason = f"Błąd przy przetwarzaniu XML: {str(e)}"

            if error_reason:
                name_error = f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {error_reason}. URL: \n{url}"

        return name_error, name_layers, prefix

    def save_gml(self, folder, url, teryt):
        """Pobiera dane EGiB dla wszystkich warstw udostępnionych przez powiaty"""
        name_error, name_layers, prefix = self.work_on_xml(folder, url, teryt)
        if name_error != "brak":
            return name_error

        url_main = url.split('?')[0]
        name_error_lista_brak = [] # Sukcesy
        name_error_lista = []      # Błędy

        for layer in name_layers:
            if prefix == 'ewns':
                url_gml = f"{url_main}?service=WFS&request=GetFeature&version=2.0.0&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)"
            elif prefix == 'ms':
                url_gml = f"{url_main}?service=WFS&request=GetFeature&version=1.0.0&typeNames={layer}&namespaces=xmlns(ms,http://mapserver.gis.umn.edu/mapserver)"
            else:
                url_gml = f'{url_main}?request=getFeature&version=2.0.0&service=WFS&typeNames={layer}'

            print(url_gml)
            sleep(1)
            layer_name = layer.split(':')[-1]
            if not check_internet_connection():
                return 'Połączenie zostało przerwane'
            
            layer_path = os.path.join(folder, f"{teryt}_{layer_name}_egib_wfs_gml.gml")
            error_reason = None

            try:
                NetworkUtils.download_file(url_gml, layer_path)
                # Sprawdzenie rozmiaru
                if os.path.exists(layer_path) and os.path.getsize(layer_path) <= MIN_FILE_SIZE:
                    error_reason = "Za mały rozmiar pliku; błąd pobierania danych (prawdopodobnie brak danych dla tego obszaru)"
                else:
                    name_error_lista_brak.append(layer_name)
            except (IOError, OSError) as e:
                error_reason = f"Błąd zapisu pliku (IOError): {e}"
            except ConnectionError as e:
                error_reason = "Błędy weryfikacji SSL (certyfikat)" if "SSL" in str(e) else f"Błąd połączenia: {e}"
            except TimeoutError:
                error_reason = "Przekroczono czas oczekiwania (Timeout)"
            except InterruptedError:
                return "Pobieranie przerwane przez użytkownika"
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
            
        return "brak"

    def egib_wfs(self, teryt, wfs, folder):
        """Tworzy nowy folder dla plików XML"""
        wfs = f"{wfs}?service=WFS&request=GetCapabilities"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f'{teryt}_wfs_egib_{timestamp}/')
        os.mkdir(path)
        return self.save_gml(path, wfs, teryt)


if __name__ == '__main__':
    wfsEgib = WfsEgib()

