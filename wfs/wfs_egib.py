import uuid

import requests
import os
import xml.etree.ElementTree as ET
from time import sleep
from lxml import etree
from lxml.etree import XMLSyntaxError

from ..service_api import check_internet_connection
from ..wfs.httpsAdapter import get_legacy_session


class WfsEgib:

    def save_xml(self, folder, url, teryt):
        """Zapisuje plik XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane"""
        """W przypadku błędów przekazuje ich opis"""
        if not check_internet_connection():
            return 'Połączenie zostało przerwane'
        try:
            with get_legacy_session().get(url, verify=False) as resp:
                if str(resp.status_code) == '404':
                    name_error = f"- (teryt: {teryt}) Serwer nie może znaleźć żądanego pliku. URL do pliku \n{url}"
                else:
                    with open(f'{folder}egib_wfs.xml', 'wb') as f:
                        f.write(resp.content)
                    name_error = "brak"
        except requests.exceptions.SSLError:
            name_error = f"- (teryt: {teryt}) Błędy weryfikacji SSL. Może to wskazywać na problem z serwerem i/lub jego certyfikatem. URL do pliku \n{url}"
        except IOError:
            name_error = f"- (teryt: {teryt}) Błąd IOError. Błąd zapisu pliku. URL do pliku \n{url}"
        except requests.exceptions.ConnectionError:
            name_error = f"- (teryt: {teryt}) Błąd ConnectionError. Problem związany z połączeniem. URL do pliku \n{url}"
        except Exception as e:
            print(type(e).__name__)  # debug
            name_error = f"- (teryt: {teryt}) Nieznany błąd. URL do pliku \n{url}"
        if name_error != "brak":
            name_error = "Nieprawidłowe warstwy: " + '\n\n ' + name_error
        return name_error

    def work_on_xml(self, folder, url, teryt):
        """Pracuje na pliku XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane"""
        """Zwraca listę warstw EGiB dostępnych dla wybranego powiatu"""
        name_error = self.save_xml(folder, url, teryt)
        name_layers = None
        prefix = None

        if name_error == "brak":
            try:
                tree = ET.parse(folder + 'egib_wfs.xml')
                root = tree.getroot()

                name_layers = []

                # Użyj bezpośrednio namespace URI
                wfs_ns = {"wfs": "http://www.opengis.net/wfs/2.0"}

                for child in root.findall('./wfs:FeatureTypeList/wfs:FeatureType', wfs_ns):
                    name = child.find('wfs:Name', wfs_ns)
                    if name is not None:
                        name_layers.append(name.text)

                # Określ prefiks
                if name_layers:
                    if 'ewns:' in name_layers[0]:
                        prefix = 'ewns'
                    elif 'ms:' in name_layers:
                        prefix = 'ms'
                    else:
                        prefix = None

            except XMLSyntaxError:
                name_error = f"- (teryt: {teryt}) Błąd XMLSyntaxError. Problem związany parsowaniem pliku XML. URL do pliku \n{url}"
            except IndexError:
                name_error = f"- (teryt: {teryt}) Błąd indeksu. URL do pliku \n{url}"
            except Exception as e:
                print(type(e).__name__)  # debug
                name_error = f"- (teryt: {teryt}) Nieznany błąd: {str(e)}. URL do pliku \n{url}"

            if name_error != "brak":
                name_error = "Nieprawidłowe warstwy: " + '\n\n ' + name_error

        return name_error, name_layers, prefix

    def save_gml(self, folder, url, teryt):
        """Pobiera dane EGiB dla wszystkich warstw udostępnionych przez powiaty"""
        """W przypadku błędów przekazuje ich opis"""

        name_error, name_layers, prefix = self.work_on_xml(folder, url, teryt)
        if name_error == "brak":
            url_main = url.split('?')[0]

            name_error_lista_brak = []

            name_error_lista = []
            for layer in name_layers:
                if prefix == 'ewns':
                    url_gml = f"{url_main}?service=WFS&request=GetFeature&version=2.0.0&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)"
                elif prefix == 'ms':
                    url_gml = f"{url_main}?service=WFS&request=GetFeature&version=1.0.0&typeNames={layer}&namespaces=xmlns(ms,http://mapserver.gis.umn.edu/mapserver)"
                elif prefix is None:
                    url_gml = f'{url_main}?request=getFeature&version=2.0.0&service=WFS&typenames={layer}'
                else:
                    url_gml = f'{url_main}?request=getFeature&version=2.0.0&service=WFS&typename={layer}'

                print(url_gml)
                sleep(1)
                if not check_internet_connection():
                    return 'Połączenie zostało przerwane'
                try:
                    with get_legacy_session().get(url_gml, verify=False) as resp:
                        if str(resp.status_code) == '404':
                            name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Serwer nie może znaleźć żądanego pliku. URL do pliku \n{url_gml}"
                            name_error_lista.append(name_error)
                        else:
                            with open(os.path.join(folder, teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml'), 'wb') as f:
                                f.write(resp.content)
                                name_error = "brak"
                            size = os.path.getsize(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
                            if size <= 9000:
                                name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Za mały rozmiar pliku; błąd pobierania. URL do pliku \n{url_gml}."
                                name_error_lista.append(name_error)
                            else:
                                name_error_lista_brak.append(f"{layer.split(':')[-1]}")
                except requests.exceptions.SSLError:
                    name_error = (f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błędy weryfikacji SSL. Może to "
                                  f"wskazywać na problem z serwerem i/lub jego certyfikatem. URL do pliku \n{url_gml}")
                    name_error_lista.append(name_error)
                except IOError:
                    name_error = (f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błąd IOError. Błąd zapisu pliku."
                                  f" URL do pliku \n{url_gml}")
                    name_error_lista.append(name_error)
                except requests.exceptions.ConnectionError:
                    name_error = (f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błąd ConnectionError. "
                                  f"Problem związany z połączeniem. URL do pliku \n{url_gml}")
                    name_error_lista.append(name_error)
                except Exception:
                    name_error = (f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Nieznany błąd. "
                                  f"URL do pliku \n{url_gml}")
            if name_error_lista:
                name_error_brak = ', '.join(name_error_lista_brak)
                name_error = '\n\n '.join(name_error_lista)
                name_error = "Nieprawidłowe warstwy: " + '\n\n ' + name_error
                if name_error_brak != "":
                    name_error = name_error + "\n\nPrawidłowe warstwy:  " + name_error_brak
        return name_error

    def egib_wfs(self, teryt, wfs, folder):
        """Tworzy nowy folder dla plików XML"""
        wfs = f"{wfs}?service=WFS&request=GetCapabilities"
        path = os.path.join(folder, f'{teryt}_wfs_egib_{uuid.uuid4()}/')
        os.mkdir(path)
        return self.save_gml(path, wfs, teryt)


if __name__ == '__main__':
    wfsEgib = WfsEgib()

