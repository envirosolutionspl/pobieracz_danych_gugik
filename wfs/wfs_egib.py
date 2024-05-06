import requests
import os
import xml.etree.ElementTree as ET
from time import sleep
from lxml import etree
from lxml.etree import XMLSyntaxError
from ..wfs.httpsAdapter import get_legacy_session


class WfsEgib:

    def save_xml(self, folder, url, teryt):
        """Zapisuje plik XML dla zapytania getCapabilities oraz obsługuje błędy z tym związane"""
        """W przypadku błędów przekazuje ich opis"""
        try:
            with get_legacy_session().get(url, verify=False) as resp:
                if str(resp.status_code) == '404':
                    name_error = f"- (teryt: {teryt}) Serwer nie może znaleźć żądanego pliku. URL do pliku \n{url}"
                else:
                    with open(folder + 'egib_wfs.xml', 'wb') as f:
                        f.write(resp.content)
                    name_error = "brak"
        except requests.exceptions.SSLError:
            name_error = f"- (teryt: {teryt}) Błędy weryfikacji SSL. Może to wskazywać na problem z serwerem i/lub jego certyfikatem. URL do pliku \n{url}"
        except IOError:
            name_error = f"- (teryt: {teryt}) Błąd IOError. Błąd zapisu pliku. URL do pliku \n{url}"
        except requests.exceptions.ConnectionError:
            name_error = f"- (teryt: {teryt}) Błąd ConnectionError. Problem związany z połączeniem. URL do pliku \n{url}"
        except Exception:
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
                ns = etree.parse(folder + 'egib_wfs.xml')
                ns = ns.getroot().nsmap
                if None in ns:
                    ns['xmlns'] = ns.pop(None)
                tree = ET.parse(folder + 'egib_wfs.xml')
                root = tree.getroot()

                name_layers = []

                for child in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
                    name = child.find('xmlns:Name', ns)
                    name_layers.append(name.text)

                # print("name_layers: ", name_layers)

                if 'ewns:' in name_layers[0]:
                    prefix = 'ewns'
                elif 'ms:' in name_layers[0]:
                    prefix = 'ms'
                else:
                    prefix = None

            except XMLSyntaxError:
                name_error = f"- (teryt: {teryt}) Błąd XMLSyntaxError. Problem związany parsowaniem pliku XML. URL do pliku \n{url}"
            except Exception:
                name_error = f"- (teryt: {teryt}) Nieznany błąd. URL do pliku \n{url}"

            # print("prefix: ", prefix)
            # print('ns: ', ns)

            if name_error != "brak":
                name_error = "Nieprawidłowe warstwy: " + '\n\n ' + name_error

        return name_error, name_layers, prefix

    def save_gml(self, folder, url, teryt):
        """Pobiera dane EGiB dla wszystkich warstw udostępnionych przez powiaty"""
        """W przypadku błędów przekazuje ich opis"""

        name_error, name_layers, prefix = self.work_on_xml(folder, url, teryt)

        if name_error == "brak":
            url_main = url.split('?')[0]

            name_error_lista = []
            name_error_lista_brak = []

            for layer in name_layers:

                if prefix == 'ewns':
                    url_gml = url_main + f"?service=WFS&request=GetFeature&version=2.0.0&srsName=urn:ogc:def:crs:EPSG::2180&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)"
                elif prefix == 'ms':
                    url_gml = url_main + f"?service=WFS&request=GetFeature&version=1.0.0&srsName=urn:ogc:def:crs:EPSG::2180&typeNames={layer}&namespaces=xmlns(ms,http://mapserver.gis.umn.edu/mapserver)"
                else:
                    url_gml = url_main + '?request=getFeature&version=2.0.0&service=WFS&srsName=urn:ogc:def:crs:EPSG::2180&typename=' + layer

                print(url_gml)
                sleep(1)
                try:
                    with get_legacy_session().get(url_gml, verify=False) as resp:
                        if str(resp.status_code) == '404':
                            name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Serwer nie może znaleźć żądanego pliku. URL do pliku \n{url_gml}"
                            name_error_lista.append(name_error)
                        else:
                            with open(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml', 'wb') as f:
                                f.write(resp.content)
                                name_error = "brak"
                            size = os.path.getsize(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
                            if size <= 9000:
                                name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Za mały rozmiar pliku; błąd pobierania. URL do pliku \n{url_gml}."
                                name_error_lista.append(name_error)
                            else:
                                name_error_lista_brak.append(f"{layer.split(':')[-1]}")

                except requests.exceptions.SSLError:
                    name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błędy weryfikacji SSL. Może to wskazywać na problem z serwerem i/lub jego certyfikatem. URL do pliku \n{url_gml}"
                    name_error_lista.append(name_error)
                except IOError:
                    name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błąd IOError. Błąd zapisu pliku. URL do pliku \n{url_gml}"
                    name_error_lista.append(name_error)
                except requests.exceptions.ConnectionError:
                    name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Błąd ConnectionError. Problem związany z połączeniem. URL do pliku \n{url_gml}"
                    name_error_lista.append(name_error)
                except Exception:
                    name_error = f"- (teryt: {teryt}, warstwa {layer.split(':')[-1]}) Nieznany błąd. URL do pliku \n{url_gml}"

            if len(name_error_lista) != 0:
                name_error_brak = ', '.join(name_error_lista_brak)
                name_error = '\n\n '.join(name_error_lista)
                name_error = "Nieprawidłowe warstwy: " + '\n\n ' + name_error
                if len(name_error_brak) != 0:
                    name_error = name_error + "\n\nPrawidłowe warstwy:  " + name_error_brak

        return name_error

    def egib_wfs(self, teryt, wfs, folder):
        """Tworzy nowy folder dla plików XML"""

        wfs = wfs + "?service=WFS&request=GetCapabilities"
        num_error_exists_file = 0
        try:
            path = os.path.join(folder, teryt + "_wfs_egib/")
            os.mkdir(path)
        except FileExistsError:
            while FileExistsError is True:
                num_error_exists_file = num_error_exists_file + 1
                path = os.path.join(folder, teryt + "_wfs_egib_" + str(num_error_exists_file) + "/")
                os.mkdir(path)
        # print("Stworzenie folderu '% s'" % path)

        name_error = self.save_gml(path, wfs, teryt)

        return name_error


if __name__ == '__main__':
    wfsEgib = WfsEgib()
    dictionary = {'1206': 'https://wms.powiat.krakow.pl:1518/iip/ows',
                  '2471': 'https://wms.sip.piekary.pl/piekary-egib',
                  '2061': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2061',
                  '0213': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0213',
                  '2402': 'https://bielski-wms.webewid.pl/us/wfs/sip',
                  '0220': 'https://trzebnicki-wms.webewid.pl/iip/ows',
                  '1811': 'https://mielec.geoportal2.pl/map/geoportal/wfs.php',
                  '3003': 'https://wms.geodezjagniezno.pl/gniezno-egib',
                  '3030': 'https://wms.wrzesnia.powiat.pl/wrzesnia-egib',
                  '1465': 'https://wms2.um.warszawa.pl/geoserver/wfs/wms',
                  '0809': 'https://giportal.powiat-zielonogorski.pl/zielonagora-egib',
                  '1437': 'http://zuromin-powiat.geoportal2.pl/map/geoportal/wfs.php',
                  '1606': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1606',
                  '2403': 'https://cieszyn.geoportal2.pl/map/geoportal/wfs.php',
                  '2002': 'https://bialystok.geoportal2.pl/map/geoportal/wfs.php',
                  '2601': 'https://geodezja.powiat.busko.pl/map/geoportal/wfs.php',
                  '0464': 'https://geoportal.wloclawek.eu/map/geoportal/wfs.php',
                  '0808': 'https://giportal2.powiat.swiebodzin.pl/swiebodzin-egib',
                  '0216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0216',
                  '2472': 'https://rudaslaska.geoportal2.pl/map/geoportal/wfs.php',
                  '3019': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3019',
                  '1661': 'https://wms.um.opole.pl/opole-egib',
                  '1809': 'https://lubaczow.geoportal2.pl/map/geoportal/wfs.php',
                  '1817': 'https://sanocki.webewid.pl:4443/us/wfs/sip',
                  '1814': 'https://sip.powiatprzeworsk.pl:4443/iip/ows',
                  '1802': 'https://brzozowski.webewid.pl:4443/us/wfs/sip/',
                  '1601': 'https://imapa.brzeg-powiat.pl/brzeg-egib',
                  '1605': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1605',
                  '3002': 'https://wms.czarnkowsko-trzcianecki.pl/czarnkowskotrzcianecki-egib',
                  '0811': 'https://zary.geoportal2.pl/map/geoportal/wfs.php',
                  '1861': 'https://krosno-wms.webewid.pl/us/wfs/sip',
                  '1609': 'https://geodezja.powiatopolski.pl/ggp',
                  '1604': 'http://185.108.68.134/kluczbork-egib',
                  '1813': 'https://powiat-przemysl.geoportal2.pl/map/geoportal/wfs.php',
                  '0462': 'http://geoportal.grudziadz.pl/ggp',
                  '2408': 'https://mapa.mikolowski.pl/map/geoportal/wfs.php',
                  '2479': 'http://wfs.geoportal.zory.pl/gugik',
                  '2469': 'https://services.gugik.gov.pl/cgi-bin/2469',
                  '1815': 'https://spropczyce.geoportal2.pl/map/geoportal/wfs.php',
                  '1819': 'https://strzyzowski.geoportal2.pl/map/geoportal/wfs.php',
                  '1608': 'https://ikerg.powiatoleski.pl/olesno-egib',
                  '1818': 'https://stalowawola.geoportal2.pl/map/geoportal/wfs.php',
                  '2661': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2661',
                  '1801': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1801',
                  '0410': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0410',
                  '1812': 'https://powiat-nisko.geoportal2.pl/map/geoportal/wfs.php',
                  '0403': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0403',
                  '0461': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0461',
                  '0414': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0414',
                  '2213': 'https://wms.powiatstarogard.pl/iip/ows',
                  '1602': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1602',
                  '0419': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0419',
                  '0405': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0405',
                  '1820': 'https://tarnobrzeski.geoportal2.pl/map/geoportal/wfs.php',
                  '0261': 'http://geoportal.jeleniagora.pl/ggp',
                  '0416': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0416',
                  '3006': 'https://ikerg.powiat-jarocinski.pl/jarocin-egib',
                  '0411': 'https://radziejow.geoportal2.pl/map/geoportal/wfs.php',
                  '3025': 'https://wms.powiatsredzki.pl/srodawlkp-egib',
                  '1863': 'https://osrodek.erzeszow.pl/map/geoportal/wfs.php',
                  '0408': 'https://lipno.geoportal2.pl/map/geoportal/wfs.php',
                  '2812': 'https://powiat-nowomiejski.geoportal2.pl/map/geoportal/wfs.php',
                  '0463': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0463',
                  '1804': 'https://jaroslawski-wms.webewid.pl/iip/ows',
                  '2607': 'https://ostrowiec.geoportal2.pl/map/geoportal/wfs.php',
                  '1810': 'https://lancut.geoportal2.pl/map/geoportal/wfs.php',
                  '2611': 'https://starachowice.geoportal2.pl/map/geoportal/wfs.php',
                  '2803': 'https://powiatdzialdowski.geoportal2.pl/map/geoportal/wfs.php',
                  '0412': 'https://rypin.geoportal2.pl/map/geoportal/wfs.php',
                  '0404': 'https://chelminski.webewid.pl:44316/iip/ows',
                  '0417': 'https://wabrzezno.geoportal2.pl/map/geoportal/wfs.php',
                  '0407': 'https://inowroclawski-wms.webewid.pl/iip/ows',
                  '1607': 'https://wms-egib.powiat.nysa.pl/nysa-egib',
                  '3020': 'https://wms.geo.net.pl/pleszew-egib',
                  '1808': 'https://lezajsk.geoportal2.pl/map/geoportal/wfs.php',
                  '0206': 'https://wms.podgik.jgora.pl/jeleniagora-egib',
                  '2463': 'https://e-odgik.chorzow.eu/arcgis/services/chorzow_egib/serwer',
                  '1610': 'https://ikerg2.powiatprudnicki.pl/prudnik-egib',
                  '1412': 'https://wms.epodgik.pl/cgi-bin/minsk',
                  '3021': 'https://ikerg.podgik.poznan.pl/wms-poznanski',
                  '3215': 'https://szczecinecki-wms.webewid.pl/iip/ows',
                  '0409': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0409',
                  '2811': 'https://powiatnidzicki.geoportal2.pl/map/geoportal/wfs.php',
                  '0862': 'https://gis.um.zielona-gora.pl/arcgis/services/zielona_gora_egib/serwer',
                  '1805': 'https://jasielski-wms.webewid.pl/iip/ows',
                  '2605': 'https://konskie.geoportal2.pl/map/geoportal/wfs.php',
                  '2461': 'https://ikerg.bielsko-biala.pl/bielsko-egib',
                  '1806': 'https://kolbuszowa.geoportal2.pl/map/geoportal/wfs.php',
                  '1816': 'https://powiatrzeszowski.geoportal2.pl/map/geoportal/wfs.php',
                  '0210': 'https://iegib.powiatluban.pl/luban-egib',
                  '1611': 'https://mapy.powiatstrzelecki.pl/ggp',
                  '1204': 'https://dabrowski-wms.webewid.pl/iip/ows',
                  '0406': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0406',
                  '0402': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0402',
                  '3061': 'https://ikerg.um.kalisz.pl/kalisz-egib',
                  '1421': 'https://wms.epodgik.pl/cgi-bin/pruszkow',
                  '0663': 'https://gis.lublin.eu/opendata/wfs',
                  '1807': 'https://krosnienski-wms.webewid.pl/iip/ows',
                  '2205': 'https://kartuski-wms.webewid.pl/iip/ows',
                  '2808': 'https://powiatketrzynski.geoportal2.pl/map/geoportal/wfs.php',
                  '0604': 'https://hrubieszow.geoportal2.pl/map/geoportal/wfs.php',
                  '1202': 'https://brzesko.geoportal2.pl/map/geoportal/wfs.php',
                  '0661': 'https://bialapodlaska.geoportal2.pl/map/geoportal/wfs.php',
                  '2411': 'https://raciborz.geoportal2.pl/map/geoportal/wfs.php',
                  '2263': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2263',
                  '2477': 'http://sit.umtychy.pl/isdp/gs/ows/default/wfs4',
                  '0223': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0223',
                  '0219': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0219',
                  '1862': 'https://przemysl.geoportal2.pl/map/geoportal/wfs.php',
                  '0264': 'https://iwms.zgkikm.wroc.pl/wroclaw-egib',
                  '1212': 'https://olkuski.webewid.pl:4434/iip/ows',
                  '3064': 'https://portal.geopoz.poznan.pl/wmsegib',
                  '0262': 'https://mapy.legnica.eu/mapserv/262011/geoportal/',
                  '1219': 'https://wielicki-wms.webewid.pl/iip/ows',
                  '1006': 'https://lodzkiwschodni.geoportal2.pl/map/geoportal/wfs.php',
                  '0215': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0215',
                  '1419': 'https://powiat-plock.geoportal2.pl/map/geoportal/wfs.php',
                  '1015': 'https://powiat-skierniewice.geoportal2.pl/map/geoportal/wfs.php',
                  '2814': 'https://powiatolsztynski.geoportal2.pl/map/geoportal/wfs.php',
                  '1001': 'http://belchatow.geoportal2.pl/map/geoportal/wfs.php',
                  '1218': 'https://wadowicki.webewid.pl:20443/iip/ows',
                  '2815': 'https://ostroda.geoportal2.pl/map/geoportal/wfs.php',
                  '2806': 'https://wms.epodgik.pl/cgi-bin/gizycko',
                  '0418': 'https://wloclawek.geoportal2.pl/map/geoportal/wfs.php',
                  '0614': 'https://pulawy.geoportal2.pl/map/geoportal/wfs.php',
                  '2817': 'http://szczytno.geoportal2.pl/map/geoportal/wfs.php',
                  '3213': 'https://slawienski.webewid.pl:4443/iip/ows',
                  '3001': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3001',
                  '0804': 'http://212.109.136.187/nowasol-egib',
                  '2818': 'https://powiatgoldap.geoportal2.pl/map/geoportal/wfs.php',
                  '1203': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1203',
                  '2810': 'https://wms.epodgik.pl/cgi-bin/mragowo',
                  '2014': 'https://powiatzambrowski.geoportal2.pl/map/geoportal/wfs.php',
                  '2807': 'https://ilawa.geoportal2.pl/map/geoportal/wfs.php',
                  '2805': 'https://powiatelk.geoportal2.pl/map/geoportal/wfs.php',
                  '2861': 'http://wms.umelblag.pl/elblag-wms',
                  '2819': 'https://wms.epodgik.pl/cgi-bin/wegorzewo',
                  '0225': 'https://iegib.powiat.zgorzelec.pl/zgorzelec-egib',
                  '0608': 'https://powiatlubartowski.geoportal2.pl/map/geoportal/wfs.php',
                  '2606': 'https://opatow.geoportal2.pl/map/geoportal/wfs.php',
                  '2802': 'https://powiat-braniewo.geoportal2.pl/map/geoportal/wfs.php',
                  '2414': 'https://sbl.webewid.pl:8443/us/wfs/sip',
                  '3218': 'https://wms.powiatlobeski.pl/lobez-egib',
                  '3204': 'https://goleniowski.webewid.pl:6443/iip/ows',
                  '0413': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0413',
                  '2801': 'https://powiatbartoszyce.geoportal2.pl/map/geoportal/wfs.php',
                  '2476': 'https://swietochlowice.geoportal2.pl/map/geoportal/wfs.php',
                  '0610': 'https://leczna.geoportal2.pl/map/geoportal/wfs.php',
                  '2813': 'https://olecko.geoportal2.pl/map/geoportal/wfs.php',
                  '2462': 'https://sitplan.um.bytom.pl/isdp/gs/ows/wfs',
                  '3217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3217',
                  '2262': 'https://pc73.miasto.gdynia.pl/iip/ows',
                  '2212': 'https://wms.powiat.slupsk.pl/iip/ows',
                  '2465': 'https://geoportal-wms.dg.pl/iip/ows',
                  '0662': 'https://wms.epodgik.pl/cgi-bin/mchelm',
                  '3203': 'https://drawski-wms.webewid.pl/iip/ows',
                  '2610': 'http://skarzysko.geoportal2.pl/map/geoportal/wfs.php',
                  '1004': 'https://leczycki.geoportal2.pl/map/geoportal/wfs.php',
                  '0609': 'https://powiatlubelski.geoportal2.pl/map/geoportal/wfs.php',
                  '2809': 'https://powiatlidzbarski.geoportal2.pl/map/geoportal/wfs.php',
                  '0612': 'https://opolelubelskie.geoportal2.pl/map/geoportal/wfs.php',
                  '0401': 'https://mapa.aleksandrow.pl/map/geoportal/wfs.php',
                  '1217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1217',
                  '1603': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1603',
                  '0212': 'https://ikerg.powiatlwowecki.pl/lwowekslaski-egib',
                  '3214': 'https://ikerg2.powiatstargardzki.eu/stargard-egib',
                  '3201': 'https://bialogardzki-wms.webewid.pl/iip/ows',
                  '2609': 'https://sandomierz.geoportal2.pl/map/geoportal/wfs.php',
                  '3209': 'https://koszalinski-wms.webewid.pl/iip/ows',
                  '3009': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3009',
                  '3263': 'http://77.88.191.50/swinoujscie',
                  '0207': 'https://wms.kamienna-gora.pl/kamiennagora-egib',
                  '1408': 'https://powiat-legionowski.geoportal2.pl/map/geoportal/wfs.php',
                  '3212': 'https://ikerg.pyrzyce.pl/pyrzyce-egib',
                  '1213': 'https://oswiecimski.webewid.pl:4422/iip/ows',
                  '1432': 'https://wms.pwz.pl/iip/ows',
                  '3262': 'https://wms.e-osrodek.szczecin.pl/szczecin-egib',
                  '0201': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0201',
                  '2409': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2409',
                  '0222': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0222',
                  '0806': 'https://fsd.geoportal2.pl/map/geoportal/wfs.php',
                  '0810': 'https://zaganski-wms.webewid.pl/iip/ows',
                  '2467': 'https://jastrzebie.geoportal2.pl/map/geoportal/wfs.php',
                  '3013': 'https://leszczynski.webewid.pl:543/iip/ows',
                  '0801': 'https://powiatgorzowski.geoportal2.pl/map/geoportal/wfs.php',
                  '3202': 'https://ikerg.geopowiatchoszczno.pl/choszczno-egib',
                  '1463': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1463',
                  '3018': 'https://wms.spostrzeszow.pl/ostrzeszow-egib',
                  '3017': 'https://ikerg.powiat-ostrowski.pl/ostrow-egib',
                  '3208': 'https://kolobrzeski-wms.webewid.pl/iip/ows',
                  '0606': 'https://powiatkrasnostawski.geoportal2.pl/map/geoportal/wfs.php',
                  '3014': 'https://wms.epodgik.pl/cgi-bin/miedzychod',
                  '1061': 'https://mapa.lodz.pl/OGC/LODZ',
                  '0226': 'https://wms.powiat-zlotoryja.pl/zlotoryja-egib',
                  '1404': 'https://gostynin.geoportal2.pl/map/geoportal/wfs.php',
                  '3022': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3022',
                  '2413': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2413',
                  '3062': 'https://ikerg.kosit.konin.eu/konin-egib',
                  '1864': 'https://tarnobrzeg.geoportal2.pl/map/geoportal/wfs.php',
                  '3010': 'https://konin.geoportal2.pl/map/geoportal/wfs.php',
                  '3012': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3012',
                  '0620': 'https://powiatzamojski.geoportal2.pl/map/geoportal/wfs.php',
                  '3007': 'https://kalisz.geoportal2.pl/map/geoportal/wfs.php',
                  '3029': 'https://ikerg.powiatwolsztyn.pl/wolsztyn-egib',
                  '1427': 'https://sierpc.geoportal2.pl/map/geoportal/wfs.php',
                  '1428': 'https://sochaczew.geoportal2.pl/map/geoportal/wfs.php',
                  '2214': 'https://wms.powiat.tczew.pl/iip/ows',
                  '3023': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3023',
                  '2478': 'https://wms.miastozabrze.pl/iip/ows',
                  '2466': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2466',
                  '3024': 'https://wms.szamotuly.com.pl/szamotuly-egib',
                  '0605': 'https://janow.geoportal2.pl/map/geoportal/wfs.php',
                  '1803': 'https://debica.geoportal2.pl/map/geoportal/wfs.php',
                  '2604': 'https://geoportal.powiat.kielce.pl/map/geoportal/wfs.php',
                  '3026': 'http://77.65.26.91/srem-egib',
                  '3027': 'https://iegib.powiat.turek.pl/cgi-bin/turek_egib',
                  '3005': 'http://185.209.71.51/grodziskwlkp-egib',
                  '3015': 'https://wms.powiatnowotomyski.pl/nowytomysl-egib',
                  '0209': 'https://legnicki-wms.webewid.pl/iip/ows',
                  '2473': 'https://services.gugik.gov.pl/cgi-bin/2473',
                  '2612': 'https://staszow.geoportal2.pl/map/geoportal/wfs.php',
                  '1438': 'https://wms.epodgik.pl/cgi-bin/zyrardow',
                  '3261': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3261',
                  '2862': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2862',
                  '2202': 'https://chojnicki-wms.webewid.pl/iip/ows',
                  '3063': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3063',
                  '2474': 'https://siemianowice.geoportal2.pl/map/geoportal/wfs.php',
                  '1414': 'https://nowodworski.geoportal2.pl/map/geoportal/wfs.php',
                  '1420': 'https://plonski.geoportal2.pl/map/geoportal/wfs.php',
                  '1422': 'https://przasnysz.geoportal2.pl/map/geoportal/wfs.php',
                  '1005': 'https://lowicz.geoportal2.pl/map/geoportal/wfs.php',
                  '0218': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0218',
                  '1435': 'https://powiat-wyszkowski.geoportal2.pl/map/geoportal/wfs.php',
                  '1405': 'https://grodzisk.geoportal2.pl/map/geoportal/wfs.php',
                  '1821': 'https://lesko.geoportal2.pl/map/geoportal/wfs.php',
                  '0203': 'https://glogow.geoportal2.pl/map/geoportal/wfs.php',
                  '1063': 'https://skierniewice.geoportal2.pl/map/geoportal/wfs.php',
                  '1007': 'https://opoczno.geoportal2.pl/map/geoportal/wfs.php',
                  '0202': 'https://geoportal.pow.dzierzoniow.pl/ggp',
                  '3031': 'https://ikerg.zlotow-powiat.pl/cgi-bin/zlotow-darmowe',
                  '2210': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2210',
                  '2415': 'https://sip.powiatwodzislawski.pl:8080/wodzislaw-egib',
                  '2009': 'https://sejny.geoportal2.pl/map/geoportal/wfs.php',
                  '1464': 'https://siedlce.geoportal2.pl/map/geoportal/wfs.php',
                  '1424': 'https://powiatpultuski.geoportal2.pl/map/geoportal/wfs.php',
                  '1425': 'https://radom.geoportal2.pl/map/geoportal/wfs.php',
                  '3008': 'https://ikerg.powiatkepno.pl/kepno-egib',
                  '3028': 'http://ikerg.wagrowiec.pl/cgi-bin/wagrowiec-egib',
                  '2816': 'https://powiatpiski.geoportal2.pl/map/geoportal/wfs.php',
                  '0208': 'https://geoportal.powiat.klodzko.pl/ggp',
                  '3210': 'http://213.76.166.254/mysliborz-egib',
                  '0211': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0211',
                  '0205': 'https://jawor.geoportal2.pl/map/geoportal/wfs.php',
                  '1416': 'https://ostrowmaz.geoportal2.pl/map/geoportal/wfs.php',
                  '2264': 'https://wms.um.sopot.pl/iip/ows',
                  '3016': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3016',
                  '3004': 'http://77.65.50.130/gostyn-egib',
                  '1205': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1205',
                  '0214': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0214',
                  '2215': 'https://wms.epodgik.pl/cgi-bin/wejherowo',
                  '3211': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3211',
                  '0607': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0607',
                  '3216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3216',
                  '1409': 'https://powiatlipsko.geoportal2.pl/map/geoportal/wfs.php',
                  '0224': 'https://zabkowicki.webewid.pl:444/iip/ows',
                  '2470': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2470',
                  '3206': 'https://gryfinski.webewid.pl:4439/iip/ows',
                  '2464': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2464',
                  '1411': 'https://makow.geoportal2.pl/map/geoportal/wfs.php',
                  '2602': 'https://jedrzejow.geoportal2.pl/map/geoportal/wfs.php',
                  '2006': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2006',
                  '0221': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0221',
                  '2013': 'https://wysokomazowiecki.geoportal2.pl/map/geoportal/wfs.php',
                  '1436': 'https://zwolenpowiat.geoportal2.pl/map/geoportal/wfs.php',
                  '0603': 'https://chelmski-wms.webewid.pl/iip/ows',
                  '1207': 'https://limanowski-wms.webewid.pl/iip/ows',
                  '2406': 'https://mapy.powiatklobucki.pl/ggp',
                  '2261': 'https://ewid-wms.gdansk.gda.pl/iip/ows',
                  '1417': 'https://powiat-otwocki.geoportal2.pl/map/geoportal/wfs.php',
                  '3207': 'https://ikerg.powiatkamienski.pl/kamien',
                  '0861': 'https://geoportal.wms.um.gorzow.pl/map/geoportal/wfs.php',
                  '1423': 'https://przysucha.geoportal2.pl/map/geoportal/wfs.php',
                  '1462': 'https://wms-ggk.plock.eu:4443/iip/ows',
                  '2003': 'https://powiatbielski.geoportal2.pl/map/geoportal/wfs.php',
                  '1418': 'https://wms.epodgik.pl/cgi-bin/piaseczno',
                  '1261': 'https://msip.um.krakow.pl/arcgis/services/ZSOZ/EGIB_udostepnianie/MapServer/WFSServer',
                  '0602': 'https://bilgorajski.geoportal2.pl/map/geoportal/wfs.php',
                  '1016': 'https://powiat-tomaszowski.geoportal2.pl/map/geoportal/wfs.php',
                  '0204': 'https://gora.geoportal2.pl/map/geoportal/wfs.php',
                  '0217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0217',
                  '2407': 'http://83.17.150.14/lubliniec-egib',
                  '2804': 'https://ikerg.powiat.elblag.pl/elblaski-egib',
                  '2010': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2010',
                  '1008': 'https://pabianice.geoportal2.pl/map/geoportal/wfs.php',
                  '2063': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2063',
                  '2004': 'https://starostwograjewo.geoportal2.pl/map/geoportal/wfs.php',
                  '1410': 'https://losice.geoportal2.pl/map/geoportal/wfs.php',
                  '3205': 'https://ikerg.podgikgryfice.pl/gryfice-egib',
                  '2011': 'https://powiatsokolski.geoportal2.pl/map/geoportal/wfs.php',
                  '2008': 'https://monki.geoportal2.pl/map/geoportal/wfs.php',
                  '0664': 'https://zamosc.geoportal2.pl/map/geoportal/wfs.php',
                  '2401': 'https://ikerg.powiat.bedzin.pl/bedzin-egib',
                  '1214': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1214',
                  '2005': 'https://hajnowka.geoportal2.pl/map/geoportal/wfs.php',
                  '1403': 'https://wms.epodgik.pl/cgi-bin/garwolin',
                  '0415': 'https://torunski-wms.webewid.pl/iip/ows',
                  '1401': 'https://bialobrzegi.geoportal2.pl/map/geoportal/wfs.php',
                  '0611': 'https://powiatlukowski.geoportal2.pl/map/geoportal/wfs.php',
                  '1426': 'https://powiatsiedlecki.geoportal2.pl/map/geoportal/wfs.php',
                  '1209': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1209',
                  '2012': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2012',
                  '0803': 'https://powiat-miedzyrzecki.geoportal2.pl/map/geoportal/wfs.php',
                  '0812': 'https://wschowa.geoportal2.pl/map/geoportal/wfs.php',
                  '2203': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2203',
                  '0616': 'https://ryki.geoportal2.pl/map/geoportal/wfs.php',
                  '2608': 'https://pinczow.geoportal2.pl/map/geoportal/wfs.php',
                  '0615': 'https://powiatradzynski.geoportal2.pl/map/geoportal/wfs.php',
                  '1430': 'https://szydlowiecpowiat.geoportal2.pl/map/geoportal/wfs.php',
                  '1413': 'https://powiatmlawski.geoportal2.pl/map/geoportal/wfs.php',
                  '1215': 'https://powiatsuski.geoportal2.pl/map/geoportal/wfs.php',
                  '1019': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1019',
                  '2209': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2209',
                  '0807': 'https://sulecin.geoportal2.pl/map/geoportal/wfs.php',
                  '1003': 'https://lask.geoportal2.pl/map/geoportal/wfs.php',
                  '1010': 'https://piotrkow.geoportal2.pl/map/geoportal/wfs.php',
                  '1013': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1013',
                  '0601': 'https://powiatbialski.geoportal2.pl/map/geoportal/wfs.php',
                  '0613': 'http://parczew.geoportal2.pl/map/geoportal/wfs.php',
                  '2206': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2206',
                  '2208': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2208',
                  '1415': 'https://powiatostrolecki.geoportal2.pl/map/geoportal/wfs.php',
                  '0619': 'https://wms.epodgik.pl/cgi-bin/wlodawa',
                  '1406': 'https://grojec.geoportal2.pl/map/geoportal/wfs.php',
                  '1211': 'https://nowotarski.geoportal2.pl/map/geoportal/wfs.php',
                  '0617': 'https://powiatswidnik.geoportal2.pl/map/geoportal/wfs.php',
                  '2211': 'https://pdp.puck.pl/iip/ows',
                  '1062': 'https://ikerg.piotrkow.pl/piotrkow-egib',
                  '1002': 'https://powiatkutno.geoportal2.pl/map/geoportal/wfs.php',
                  '2207': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2207',
                  '1433': 'https://wms.epodgik.pl/cgi-bin/wegrow',
                  '2001': 'https://wms.epodgik.pl/cgi-bin/augustow',
                  '2216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2216',
                  '2204': 'https://gdanski-wms.webewid.pl/iip/ows',
                  '1461': 'https://ostroleka.geoportal2.pl/map/geoportal/wfs.php',
                  '1429': 'https://powiat-sokolowski.geoportal2.pl/map/geoportal/wfs.php',
                  '2404': 'https://czestochowa.geoportal2.pl/map/geoportal/wfs.php',
                  '1012': 'https://radomszczanski.geoportal2.pl/map/geoportal/wfs.php',
                  '0265': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0265',
                  '2603': 'https://kazimierzaw.geoportal2.pl/map/geoportal/wfs.php',
                  '2405': 'https://gliwicki.webewid.pl:4443/iip/ows',
                  '2410': 'https://pszczynski-wms.webewid.pl/iip/ows',
                  '1020': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1020',
                  '1262': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1262',
                  '1210': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1210',
                  '1402': 'https://ciechanow.geoportal2.pl/map/geoportal/wfs.php',
                  '1201': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1201',
                  '1009': 'https://pajeczno.geoportal2.pl/map/geoportal/wfs.php',
                  '1011': 'https://poddebice.geoportal2.pl/map/geoportal/wfs.php',
                  '1407': 'https://kozienicepowiat.geoportal2.pl/map/geoportal/wfs.php',
                  '3011': 'https://iegib.powiatkoscian.pl/cgi-bin/koscian',
                  '1018': 'https://wieruszow.geoportal2.pl/map/geoportal/wfs.php',
                  '1263': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1263',
                  '2412': 'https://rybnik.geoportal2.pl/map/geoportal/wfs.php',
                  '0618': 'https://tomaszowlubelski.geoportal2.pl/map/geoportal/wfs.php',
                  '2417': 'https://zywiecki-wms.webewid.pl/iip/ows',
                  '1208': 'https://miechow.geoportal2.pl/map/geoportal/wfs.php',
                  '2201': 'https://bytowski.webewid.pl:4433/iip/ows',
                  '2475': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2475',
                  '1021': 'https://brzeziny.geoportal2.pl/map/geoportal/wfs.php',
                  '1014': 'https://sieradz.geoportal2.pl/map/geoportal/wfs.php',
                  '1434': 'https://wms.epodgik.pl/cgi-bin/wolomin',
                  '1216': 'https://webewid.powiat.tarnow.pl:20443/iip/ows',
                  '2468': 'https://jaworzno-wms.webewid.pl/iip/ows',
                  '1017': 'https://wielun.geoportal2.pl/map/geoportal/wfs.php',
                  '2613': 'https://wloszczowa.geoportal2.pl/map/geoportal/wfs.php',
                  '0805': 'https://slubice.geoportal2.pl/map/geoportal/wfs.php',
                  '0802': 'https://wms.powiatkrosnienski.pl/krosno-egib',
                  '2416': 'https://ikerg.zawiercie.powiat.pl/powiatzawiercianski-egib'}
    folder = f"C:\\wtyczka aktualizacja\\probne/"
# print(wfsEgib.egib_wfs("2613", 'https://mielec.geoportal2.pl/map/geoportal/wfs.php', folder))

# for k, v in dictionary.items():
#     print(wfsEgib.egib_wfs(k, v, folder))
