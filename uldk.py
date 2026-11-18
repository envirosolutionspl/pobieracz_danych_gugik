import json
from functools import partial

from .utils import MessageUtils, NetworkUtils
from .constants import LOCAL_API_URL, GET_VOIVODESHIP_ENDPOINT, GET_COUNTY_ENDPOINT, GET_COMMUNE_ENDPOINT, TIMEOUT_MS


class RegionFetch:
    """Jednostki administracyjne z REST."""

    # nazwy z ADMINISTRATIVE_UNITS_OBJECTS -> endpoint REST
    UNIT_ENDPOINTS = {
        'getPowiatByTeryt': GET_COUNTY_ENDPOINT,
        'getGminaByTeryt': GET_COMMUNE_ENDPOINT,
    }

    def __init__(self):
        self.network_utils = NetworkUtils()
        self.wojewodztwoDict = {}
        self._fetchingWojewodztwa = False

    def fetchUnitDict(self, endpoint):
        unit_dict = {}
        url = f"{LOCAL_API_URL}{endpoint}"
        MessageUtils.pushLogInfo(f"Pobieranie danych z: {url}")
        is_success, result = self.network_utils.fetchJson(url, timeout_ms=TIMEOUT_MS)
        if not is_success:
            MessageUtils.pushLogWarning(result)
            return unit_dict
        return self._toUnitDict(result)

    @staticmethod
    def _toUnitDict(items):
        unit_dict = {}
        try:
            for item in items:
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

    # ------------------------------------------------------- bez blokowania

    def _fetchUnitDictAsync(self, endpoint, on_done):
        url = f"{LOCAL_API_URL}{endpoint}"
        MessageUtils.pushLogInfo(f"Pobieranie danych z: {url}")
        self.network_utils.fetchContentAsync(
            url,
            partial(self._onUnitDictFetched, on_done),
            timeout_ms=TIMEOUT_MS
        )

    def _onUnitDictFetched(self, on_done, fetch_result):
        """Odpowiedź REST -> słownik {teryt: nazwa}; pusty słownik przy błędzie."""
        is_success, result = fetch_result
        if not is_success:
            MessageUtils.pushLogWarning(result)
            on_done({})
            return
        try:
            items = json.loads(result)
        except json.JSONDecodeError as e:
            MessageUtils.pushLogWarning(f"Błąd JSON: {str(e)}")
            on_done({})
            return
        on_done(self._toUnitDict(items))

    def isFetchingWojewodztwa(self):
        return self._fetchingWojewodztwa

    def fetchWojewodztwaAsync(self, on_done):
        """Pobiera województwa bez blokowania i zapamiętuje je w `wojewodztwoDict`."""
        self._fetchingWojewodztwa = True
        self._fetchUnitDictAsync(
            GET_VOIVODESHIP_ENDPOINT,
            partial(self._onWojewodztwaFetched, on_done)
        )

    def _onWojewodztwaFetched(self, on_done, unit_dict):
        self._fetchingWojewodztwa = False
        if unit_dict:
            self.wojewodztwoDict = unit_dict
        on_done(unit_dict)

    def fetchUnitsByTerytAsync(self, func_name, teryt, on_done):
        """Pobiera powiaty/gminy bez blokowania; `func_name` jak w ADMINISTRATIVE_UNITS_OBJECTS."""
        if not teryt:
            on_done({})
            return
        endpoint = self.UNIT_ENDPOINTS[func_name].format(teryt=teryt)
        self._fetchUnitDictAsync(endpoint, on_done)
