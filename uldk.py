from .utils import MessageUtils, NetworkUtils
from .constants import LOCAL_API_URL, GET_VOIVODESHIP_ENDPOINT, GET_COUNTY_ENDPOINT, GET_COMMUNE_ENDPOINT, TIMEOUT_MS


class RegionFetch:
    def __init__(self):
        self.network_utils = NetworkUtils()
        self.wojewodztwoDict = self.getWojewodztwoDict()

    def fetchUnitDict(self, endpoint):
        unit_dict = {}
        url = f"{LOCAL_API_URL}{endpoint}"
        MessageUtils.pushLogInfo(f"Pobieranie danych z: {url}")
        is_success, result = self.network_utils.fetchJson(url, timeout_ms=TIMEOUT_MS)
        if not is_success:
            MessageUtils.pushLogWarning(result)
            return unit_dict
        try:
            for item in result:
                unit_dict[item['teryt']] = item['name']
        except KeyError as e:
            MessageUtils.pushLogWarning(f"Struktura danych jest niepoprawna: {str(e)}")
        except Exception as e:
            MessageUtils.pushLogWarning(f"Inny błąd przy pobieraniu: {str(e)}")
        return unit_dict

    def getWojewodztwoDict(self):
        return self.fetchUnitDict(GET_VOIVODESHIP_ENDPOINT)

    def getPowiatByTeryt(self, teryt):
        if not teryt:
            return {}
        return self.fetchUnitDict(GET_COUNTY_ENDPOINT.format(teryt=teryt))

    def getGminaByTeryt(self, teryt):
        if not teryt:
            return {}
        return self.fetchUnitDict(GET_COMMUNE_ENDPOINT.format(teryt=teryt))

