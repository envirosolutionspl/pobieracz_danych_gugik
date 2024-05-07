from  .wfs.httpsAdapter import get_legacy_session
import requests
class RegionFetch:
    def __init__(self):
        self.wojewodztwoDict = self.__fetchWojewodztwoDict()
        self.powiatDict = self.__fetchPowiatDict()
        self.gminaDict = self.__fetchGminaDict()
        self.filteredPowiatDict = {}
        self.filteredGminaDict = {}

    def __fetchGminaDict(self):
        resp = get_legacy_session().get('https://uldk.gugik.gov.pl/service.php?obiekt=gmina&wynik=gmina,powiat,teryt,wojewodztwo', verify=False)
        gmList = resp.text.strip().split('\n')
        gmDict = {}
        if len(gmList) and gmList[0] == '0':
             gmList = gmList[1:]
             for el in gmList:
                split = el.split('|')
                gmDict[split[2]] = split[0], split[1], split[3]
             return gmDict
        else:
            return {}

    def __fetchPowiatDict(self):
        resp = get_legacy_session().get('https://uldk.gugik.gov.pl/service.php?obiekt=powiat&wynik=powiat,teryt,wojewodztwo', verify=False)
        powList = resp.text.strip().split('\n')
        powDict = {}
        if len(powList) and powList[0] == '0':
            powList = powList[1:]
            for el in powList:
                split = el.split('|')
                powDict[split[1]] = split[0], split[2]
            return powDict
        else:
            return {}

    def __fetchWojewodztwoDict(self):
        resp = get_legacy_session().get('https://uldk.gugik.gov.pl/service.php?obiekt=wojewodztwo&wynik=wojewodztwo,teryt', verify=False)
        wojList = resp.text.strip().split('\n')
        wojDict = {}
        if len(wojList) and wojList[0] == '0':
            wojList = wojList[1:]
            for el in wojList:
                split = el.split('|')
                wojDict[split[0]] = split[1]
            return wojDict
        else:
            return {}

    def getPowiatDictByWojewodztwoName(self, name):
        self.filteredPowiatDict = {v[0]: k for k, v in self.powiatDict.items() if v[1] == name}
        return self.filteredPowiatDict

    def getGminaDictByPowiatName(self, name_powiat):
        self.filteredGminaDict = {}
        for k, v in self.gminaDict.items():
            if v[1] == name_powiat:
                self.filteredGminaDict[v[0]] = k
        return self.filteredGminaDict

    def getTerytByWojewodztwoName(self,name):
        return self.wojewodztwoDict[name]

    def getTerytByPowiatName(self,name):
        # print("teryt ", self.filteredPowiatDict[name])
        return self.filteredPowiatDict[name]

    def getTerytByGminaName(self,name):
        # print("teryt ", self.filteredGminaDict[name])
        return self.filteredGminaDict[name]

if __name__ == '__main__':
    regionFetch = RegionFetch()
    # print(regionFetch.wojewodztwoDict)
    # print(regionFetch.powiatDict)
    # print(regionFetch.getPowiatDictByWojewodztwoName('Lubelskie'))
    # print(regionFetch.gminaDict)
    # print(regionFetch.getGminaDictByPowiatName('warszawski zachodni'))
    # print(regionFetch.getGminaDictByPowiatName('włoszczowski'))


