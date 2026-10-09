import os
from time import sleep
from lxml.etree import XMLParser, XMLSyntaxError, fromstring
from datetime import datetime
from ..utils import NetworkUtils, ServiceAPI
from ..constants import (
    MIN_FILE_SIZE,
    CAPABILITIES_FILE_NAME,
    OGC_VERSIONS,
    GML_URL_TEMPLATES,
    STATUS_SUCCESS,
    STATUS_CANCELED,
    MSG_NO_CONNECTION,
    MSG_DOWNLOAD_CANCELED
)


class WfsEgib:

    def __init__(self):
        self.service_api = ServiceAPI()
        self.network_utils = NetworkUtils()

    def saveXml(self, folder, url, teryt, obj=None):
        """Zapisuje plik XML dla zapytania getCapabilities"""
        is_success = self.service_api.checkInternetConnection()
        if not is_success:
            return MSG_NO_CONNECTION

        path = os.path.join(folder, CAPABILITIES_FILE_NAME)

        is_success, result = self.network_utils.downloadFile(url, path, obj=obj)
        if not is_success:
            return f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {result}. URL: \n{url}"

        return STATUS_SUCCESS

    @staticmethod
    def workOnXml(folder, url, teryt):
        """Pracuje na pliku XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane.

        Wywoływać WYŁĄCZNIE w głównym wątku (np. w QgsTask.finished()). lxml używany
        w wątku QgsTask powoduje crash QGIS przy zamykaniu wątku (xmlDictFree).
        Plik musi być wcześniej pobrany przez saveXml().
        """
        name_error = STATUS_SUCCESS
        name_layers = None
        prefix = None

        if name_error == STATUS_SUCCESS:
            error_reason = None
            try:
                parser = XMLParser(
                    resolve_entities=False,  # Prevent XXE
                    no_network=True,         # Disable network access
                    recover=False            # Avoid silent error recovery
                )

                lxml_string = None

                with open(os.path.join(folder, 'egib_wfs.xml'), 'rb') as f:
                    lxml_string = f.read()
                if lxml_string is None or lxml_string == b"":
                    raise Exception(f"The file '{os.path.join(folder, 'egib_wfs.xml')}' is empty.")

                root = fromstring(lxml_string, parser=parser)

                name_layers = []
                wfs_ns = [
                    {"wfs": "http://www.opengis.net/wfs/2.0"},
                    {"wfs": "http://www.opengis.net/wfs"}
                ]

                for wfs_standard in wfs_ns:
                    for child in root.findall('./wfs:FeatureTypeList/wfs:FeatureType', wfs_standard):
                        name = child.find('wfs:Name', wfs_standard)
                        if name is not None:
                            name_layers.append(name.text)

                    if name_layers:
                        if name_layers[0].startswith('ewns:'):
                            prefix = 'ewns'
                        elif name_layers[0].startswith('ms:'):
                            prefix = 'ms'
                        break
            except XMLSyntaxError:
                error_reason = "Błąd parsowania pliku XML. Serwer zwrócił niepoprawne dane"
            except Exception as e:
                error_reason = f"Błąd przy przetwarzaniu XML: {str(e)}"

            if error_reason:
                name_error = f"Nieprawidłowe warstwy: \n\n - (teryt: {teryt}) {error_reason}. URL: \n{url}"

        return name_error, name_layers, prefix

    def saveGML(self, folder, url, teryt, name_layers, prefix, obj=None):
        """Pobiera dane EGiB dla wszystkich warstw udostępnionych przez powiaty.

        Wykonywane w wątku QgsTask. Lista warstw (name_layers, prefix) pochodzi
        z workOnXml(), wywołanego wcześniej w głównym wątku.
        """
        url_main = url.split('?')[0]
        name_error_lista_brak = []
        name_error_lista = []

        for layer in name_layers:
            if obj and obj.isCanceled():
                return STATUS_CANCELED

            for version in OGC_VERSIONS:

                if prefix in GML_URL_TEMPLATES:
                    url_gml = GML_URL_TEMPLATES[prefix].format(
                        url_main=url_main,
                        layer=layer,
                        version=version
                    )
                else:
                    url_gml = GML_URL_TEMPLATES['default'].format(
                        url_main=url_main,
                        layer=layer,
                        version=version
                    )

                # skracamy sleep lub dodajemy sprawdzenie po nim
                sleep(0.1)
                if obj and obj.isCanceled():
                    return STATUS_CANCELED

                layer_name = layer.split(':')[-1]
                is_success = self.service_api.checkInternetConnection()
                if not is_success:
                    return MSG_NO_CONNECTION

                layer_path = os.path.join(folder, f"{teryt}_{layer_name}_egib_wfs_gml.gml")
                error_reason = None

                try:
                    is_success, result = self.network_utils.downloadFile(url_gml, layer_path, obj=obj)
                    if is_success:
                        # Sprawdzenie rozmiaru
                        if os.path.exists(layer_path) and os.path.getsize(layer_path) <= MIN_FILE_SIZE:
                            error_reason = "Za mały rozmiar pliku; błąd pobierania danych (prawdopodobnie brak danych dla tego obszaru)"
                        else:
                            name_error_lista_brak.append(layer_name)
                            break
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

    @staticmethod
    def capabilitiesUrl(wfs):
        """Adres zapytania GetCapabilities dla usługi WFS"""
        return f"{wfs}?service=WFS&request=GetCapabilities"

    @staticmethod
    def createFolder(teryt, folder):
        """Tworzy nowy folder dla plików XML i GML"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f'{teryt}_wfs_egib_{timestamp}/')
        os.makedirs(path, exist_ok=True)
        return path


if __name__ == '__main__':
    wfsEgib = WfsEgib()
