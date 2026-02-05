from .network_utils import NetworkUtils
from qgis.core import QgsMessageLog
from .constants import LOCAL_API_URL, GET_VOIVODESHIP_ENDPOINT, GET_COUNTY_ENDPOINT, GET_COMMUNE_ENDPOINT, TIMEOUT_MS


class RegionFetch:
    def __init__(self):
        self.wojewodztwoDict = self.get_wojewodztwo_dict()

    @staticmethod
    def fetch_unit_dict(endpoint):
        unit_dict = {}
        url = f"{LOCAL_API_URL}{endpoint}"
        try:
            QgsMessageLog.logMessage(f"Pobieranie danych z: {url}", "PobieraczDanych")
            data = NetworkUtils.fetch_json(url, timeout_ms=TIMEOUT_MS)
            for item in data:
                unit_dict[item['teryt']] = item['name']
        except (TimeoutError, ConnectionError) as e:
            QgsMessageLog.logMessage(f"Błąd połączenia przy pobieraniu {url}: {str(e)}", "PobieraczDanych", level=2)
        except Exception as e:
            QgsMessageLog.logMessage(f"Inny błąd przy pobieraniu {url}: {str(e)}", "PobieraczDanych", level=2)
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
