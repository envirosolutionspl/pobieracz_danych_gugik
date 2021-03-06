import requests
class RegionFetch:
    def __init__(self):
        self.wojewodztwoDict = self.__fetchWojewodztwoDict()
        self.powiatDict = self.__fetchPowiatDict()
        self.filteredPowiatDict = {}

    def __fetchPowiatDict(self):
        resp = requests.get('https://uldk.gugik.gov.pl/service.php?obiekt=powiat&wynik=powiat,teryt,wojewodztwo')
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
        resp = requests.get('https://uldk.gugik.gov.pl/service.php?obiekt=wojewodztwo&wynik=wojewodztwo,teryt')
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

    def getTerytByWojewodztwoName(self,name):
        return self.wojewodztwoDict[name]

    def getTerytByPowiatName(self,name):
        return self.filteredPowiatDict[name]

if __name__ == '__main__':
    regionFetch = RegionFetch()
    print(regionFetch.wojewodztwoDict)
    print(regionFetch.powiatDict)
    print(regionFetch.getPowiatDictByWojewodztwoName('Lubelskie'))