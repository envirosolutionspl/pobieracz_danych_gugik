from qgis.utils import iface
from .utils import pushWarning
from lxml import etree

from .network_utils import NetworkUtils
from .constants import EGIB_WFS_URL, TIMEOUT_MS 

class EgibApi:
    def __init__(self):
        self.network_utils = NetworkUtils()

    def getWfsDict(self, filter_name):
        data_dict = {}
        success, content = self.network_utils.fetchContent(EGIB_WFS_URL, timeout_ms=TIMEOUT_MS * 2)
        if not success:
            pushWarning(iface, 'Ostrzeżenie:', content)
            return


        root = etree.HTML(content)
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
    
    def getWfsEgibDict(self):
        return self.getWfsDict("Ewidencja Gruntów i Budynków (EGIB)")
