from .constants import ULDK_GMINA_DICT_URL, ULDK_POWIAT_DICT_URL, ULDK_WOJEWODZTWO_DICT_URL
from .wfs.httpsAdapter import get_legacy_session


class RegionFetch:
    def __init__(self):
        self.wojewodztwoDict = self.__fetchWojewodztwoDict()
        self.powiatDict = self.__fetchPowiatDict()
        self.gminaDict = self.__fetchGminaDict()
        self.filteredPowiatDict = {}
        self.filteredGminaDict = {}

    @staticmethod
    def fetch_unit_dict(url):
        unit_dict = {}
        with get_legacy_session().get(url=url, verify=False) as resp:
            resp_text = resp.text.strip().split('\n')
            if not resp_text:
                return
            for el in resp_text[1:]:
                split = el.split('|')
                unit_dict[split[1]] = split[0]
        return unit_dict

    def __fetchGminaDict(self):
        return self.fetch_unit_dict(ULDK_GMINA_DICT_URL)

    def __fetchPowiatDict(self):
        return self.fetch_unit_dict(ULDK_POWIAT_DICT_URL)

    def __fetchWojewodztwoDict(self):
        return self.fetch_unit_dict(ULDK_WOJEWODZTWO_DICT_URL)

    def get_powiat_by_teryt(self, teryt):
        return {key: val for key, val in self.powiatDict.items() if key.startswith(teryt)}

    def get_gmina_by_teryt(self, teryt):
        return {key: val for key, val in self.gminaDict.items() if key.startswith(teryt)}


if __name__ == '__main__':
    regionFetch = RegionFetch()
