from qgis.utils import iface

import requests
from lxml import etree

from .service_api import check_internet_connection
from .constants import EGIB_WFS_URL
from .wfs.httpsAdapter import get_legacy_session

def get_wfs_dict(filter_name):
    data_dict = {}
    try:
        with get_legacy_session().get(url=EGIB_WFS_URL, verify=False) as resp:
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
        nazwa_zbioru = next(cells[2].itertext()).strip()

        if nazwa_zbioru == filter_name:
            teryt = next(cells[3].itertext()).strip()
            link_element = cells[6].find('a')
            link = link_element.get('href') if link_element is not None else ''
            data_dict[teryt] = link.split("?")[0] if link else ''

    data_dict.update({"2062": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2062"})
    data_dict.update({"2007": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2007"})
    
    return data_dict

def get_wfs_egib_dict():
    return get_wfs_dict("Ewidencja Gruntów i Budynków (EGIB)")
