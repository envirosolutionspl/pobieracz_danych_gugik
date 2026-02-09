from .network_utils import NetworkUtils
from .utils import pushLogInfo
from .constants import LOCAL_API_URL, GET_VOIVODESHIP_ENDPOINT, GET_COUNTY_ENDPOINT, GET_COMMUNE_ENDPOINT, TIMEOUT_MS


class RegionFetch:
    def __init__(self):
        self.network_utils = NetworkUtils()
        self.wojewodztwoDict = self.get_wojewodztwo_dict()

    def fetch_unit_dict(self, endpoint):
        unit_dict = {}
        url = f"{LOCAL_API_URL}{endpoint}"
        pushLogInfo(f"Pobieranie danych z: {url}")
        success, result = self.network_utils.fetchJson(url, timeout_ms=TIMEOUT_MS)
        if not success:
            pushLogInfo(result)
            return unit_dict
        try:
            for item in result:
                unit_dict[item['teryt']] = item['name']
        except KeyError as e:
            pushLogInfo(f"Struktura danych jest niepoprawna: {str(e)}")
        except Exception as e:
            pushLogInfo(f"Inny błąd przy pobieraniu: {str(e)}")
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

