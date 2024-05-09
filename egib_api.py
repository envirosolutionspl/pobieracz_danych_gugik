from bs4 import BeautifulSoup

from .wfs.httpsAdapter import get_legacy_session


def get_wfs_egib_dict():
    egib_url = ("https://integracja.gugik.gov.pl/eziudp/index.php?teryt=&rodzaj=powiaty&nazwa=&zbior=&temat=1.6&usluga"
                "=pobierania&adres=")
    egib_dict = {}
    with get_legacy_session().get(url=egib_url, verify=False) as resp:
        if resp.status_code != 200:
            return
    parser = BeautifulSoup(resp.content, 'html.parser')
    table = parser.find('table', class_='table')
    if not table:
        return
    rows = table.find_all('tr')
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
        teryt = cells[3].get_text()
        link = cells[5].find('a')['href']
        egib_dict.update({teryt: link.split("?")[0]})
    egib_dict.update({"2062": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2062"})
    egib_dict.update({"2007": "https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2007"})
    return egib_dict