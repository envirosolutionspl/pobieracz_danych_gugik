from qgis.utils import iface

import requests
from lxml import etree
from .wfs.httpsAdapter import get_legacy_session


def get_wfs_egib_dict():
    egib_url = ("https://integracja.gugik.gov.pl/eziudp/index.php?teryt=&rodzaj=powiaty&nazwa=&zbior=&temat=1.6&usluga"
                "=pobierania&adres=")
    egib_dict = {}
    try:
        with get_legacy_session().get(url=egib_url, verify=False, timeout=30) as resp:
            if resp.status_code != 200:
                return
    except requests.exceptions.ConnectionError:
        iface.messageBar().pushWarning("Ostrzeżenie:", 'Brak połączenia z internetem - nie można pobrać adresu WFS.')
        return
    except requests.exceptions.Timeout:
        iface.messageBar().pushWarning('Ostrzeżenie:', 'Przekroczono czas oczekiwania na odpowiedź serwera.')
        return
    root = etree.HTML(resp.content)
    table = root.xpath('.//table[contains(@class, "table")]')[0]
    if table is None:
        return
    for row in table.iterfind('.//tr'):
        cells = [cell for cell in row.iterfind('td')]
        if len(cells) < 7:
            continue
        teryt = next(cells[3].itertext())
        link = cells[6].find('a').get('href')
        egib_dict[teryt] = link.split("?")[0] if link else ''
    egib_dict.update({"2062": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2062"})
    egib_dict.update({"2007": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2007"})
    return egib_dict