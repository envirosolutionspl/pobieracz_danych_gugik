from qgis.utils import iface

import requests
from lxml import etree

from .service_api import check_internet_connection
from .constants import EGIB_WFS_URL
from .wfs.httpsAdapter import get_legacy_session


def get_wfs_egib_dict():
    egib_dict = {}
    if not check_internet_connection():
        return
    try:
        with get_legacy_session().get(url=EGIB_WFS_URL, verify=False) as resp:
            if resp.status_code != 200:
                return
    except requests.exceptions.ConnectionError:
        iface.messageBar().pushWarning("Ostrzeżenie:", 'Brak połączenia z internetem - nie można pobrać adresu WFS.')
        return
    root = etree.HTML(resp.content)
    table = root.xpath('.//table[contains(@class, "table")]')[0]
    if not table:
        return
    for row in table.iterfind('.//tr'):
        cells = list(row.iterfind('td'))
        if len(cells) < 7:
            continue
        teryt = next(cells[3].itertext())
        link = cells[6].find('a').get('href')
        egib_dict[teryt] = link.split("?")[0] if link else ''
    egib_dict["2062"] = (
        "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2062"
    )
    egib_dict["2007"] = (
        "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2007"
    )
    return egib_dict