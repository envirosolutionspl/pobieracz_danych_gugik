from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from qgis.PyQt.QtCore import QUrl, QEventLoop


class RegionFetch:
    def __init__(self):
        self.loop = QEventLoop()
        self.wojewodztwoDict = {}
        self.powiatDict = {}
        self.gminaDict = {}
        self.obrebDict = {}
        
        self.filteredPowiatDict = {}
        self.filteredGminaDict = {}
        self.filteredObrebDict = {}

        self.__fetchWojewodztwo()

    def __fetchWojewodztwo(self):
        manager = QNetworkAccessManager()
        resp = QNetworkRequest(QUrl('https://uldk.gugik.gov.pl/service.php?obiekt=wojewodztwo&wynik=nazwa%2Cteryt&teryt='))
        manager.get(resp)
        manager.finished.connect(self.getWojewodztwo)
        self.loop.exec_()
        
    def __fetchPowiat(self, woj_name):
        teryt = self.wojewodztwoDict[woj_name]
        manager = QNetworkAccessManager()
        resp = QNetworkRequest(QUrl(f'https://uldk.gugik.gov.pl/service.php?obiekt=powiat&wynik=nazwa%2Cteryt,wojewodztwo&teryt={teryt}'))
        manager.get(resp)
        manager.finished.connect(self.getPowiat)
        self.loop.exec_()
        
    def __fetchGmina(self, powiat_name):
        teryt = self.powiatDict[powiat_name][0]
        manager = QNetworkAccessManager()                   
        resp = QNetworkRequest(QUrl(f'https://uldk.gugik.gov.pl/service.php?obiekt=gmina&wynik=nazwa,powiat%2Cteryt,wojewodztwo&teryt={teryt}'))
        manager.get(resp)
        manager.finished.connect(self.getGmina)
        self.loop.exec_()
        
    def getWojewodztwo(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data().decode('utf-8')
            data = data.strip().split('\n')            
            if len(data) and data[0] == '0':
                data = data[1:]
                for el in data:
                    split = el.split('|')
                    self.wojewodztwoDict[split[0]] = split[1]
        self.loop.quit()
     
    def getPowiat(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data().decode('utf-8')
            data = data.strip().split('\n')
            if len(data) and data[0] == '0':
                data = data[1:]
                self.powiatDict.clear()
                for el in data:
                    split = el.split('|')
                    self.powiatDict[split[0]] = split[1], split[2]
        self.loop.quit()

    def getGmina(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data().decode('utf-8')
            data = data.strip().split('\n')
            if len(data) and data[0] == '0':
                data = data[1:]
                self.gminaDict.clear()
                for el in data:
                    split = el.split('|')
                    # self.gminaDict[split[2]] = split[0], split[1], split[3]
                    self.gminaDict[split[0]] = split[1], split[2], split[3]
        self.loop.exit(0)

        
    def getPowiatDictByWojewodztwoName(self, woj_name):
        if not woj_name:
            return {}
        self.__fetchPowiat(woj_name)
        return self.powiatDict

    def getGminaDictByPowiatName(self, name_powiat):
        if not name_powiat:
            return {}
        self.__fetchGmina(name_powiat)
        return self.gminaDict


if __name__ == '__main__':
    # app = QtCore.QCoreApplication([])
    regionFetch = RegionFetch()
    # app.exec_()
    