import requests
from qgis.core import QgsMessageLog
from .constants import LOCAL_API_URL, GET_VOIVODESHIP_ENDPOINT, GET_COUNTY_ENDPOINT, GET_COMMUNE_ENDPOINT


class RegionFetch:
    def __init__(self):
        self.wojewodztwoDict = self.get_wojewodztwo_dict()

    @staticmethod
    def fetch_unit_dict(endpoint):
        unit_dict = {}
        url = f"{LOCAL_API_URL}{endpoint}"
        try:
            QgsMessageLog.logMessage(f"Pobieranie danych z: {url}", "PobieraczDanych")
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    unit_dict[item['teryt']] = item['name']
            else:
                QgsMessageLog.logMessage(f"Błąd HTTP {resp.status_code} przy pobieraniu: {url}", "PobieraczDanych")
        except Exception as e:
            QgsMessageLog.logMessage(f"Wyjątek przy pobieraniu {url}: {str(e)}", "PobieraczDanych")
        return unit_dict

    def get_wojewodztwo_dict(self):
        return self.fetch_unit_dict(GET_VOIVODESHIP_ENDPOINT)

    def get_powiat_by_teryt(self, teryt):
        if not teryt:
            return {}
        return self.fetch_unit_dict(GET_COUNTY_ENDPOINT.format(teryt=teryt))

    def get_gmina_by_teryt(self, teryt):
        if not teryt:
            return {}
        return self.fetch_unit_dict(GET_COMMUNE_ENDPOINT.format(teryt=teryt))


if __name__ == '__main__':
    regionFetch = RegionFetch()
