import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from .. import service_api, utils
import requests

class DownloadEgibExcelTask(QgsTask):
    """QgsTask pobierania zestawień zbiorczych EGiB"""

    def __init__(self, description, folder, egib_excel_zakres_danych, rok, teryt_powiat, teryt_wojewodztwo):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.zakres_danych = egib_excel_zakres_danych
        self.rok = rok
        self.teryt_powiat = teryt_powiat
        self.teryt_wojewodztwo = teryt_wojewodztwo

        self.dic_nazwa_teryt_wojewodztwa = {'02_dolnoslaskie': '02',
                                            '04_kujawsko-pomorskie': '04',
                                            '06_lubelskie': '06',
                                            '08_lubuskie': '08',
                                            '10_lodzkie': '10',
                                            '12_malopolskie': '12',
                                            '14_mazowieckie': '14',
                                            '16_opolskie': '16',
                                            '18_podkarpackie': '18',
                                            '20_podlaskie': '20',
                                            '22_pomorskie': '22',
                                            '24_slaskie': '24',
                                            '26_swietokrzyskie': '26',
                                            '28_warminsko-mazurskie': '28',
                                            '30_wielkopolskie': '30',
                                            '32_zachodniopomorskie': '32'
                                            }

    def run(self):

        list_url = []

        if self.zakres_danych == 'powiat':
            url_czesc = f"https://opendata.geoportal.gov.pl/ZestawieniaZbiorczeEGiB/{self.rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}"
        elif self.zakres_danych == 'wojew':
            nazwa_teryt_wojewodztwa = ''

            for k, v in self.dic_nazwa_teryt_wojewodztwa.items():
                if v == self.teryt_wojewodztwo:
                    nazwa_teryt_wojewodztwa = k

            url_czesc = f"https://opendata.geoportal.gov.pl/ZestawieniaZbiorczeEGiB/{self.rok}/{self.teryt_wojewodztwo}/{nazwa_teryt_wojewodztwa}"
        elif self.zakres_danych == 'kraj':
            url_czesc = f"https://opendata.geoportal.gov.pl/ZestawieniaZbiorczeEGiB/{self.rok}/Polska"

        list_url.append(url_czesc + '.xlsx')
        list_url.append(url_czesc + '.xls')

        for url in list_url:
            r = requests.get(url)
            if str(r.status_code) == '200':
                QgsMessageLog.logMessage('pobieram ' + url)
                # fileName = self.url.split("/")[-2]
                # print(self.folder)
                service_api.retreiveFile(url=url, destFolder=self.folder)
                # self.setProgress(self.progress() + 100 / total)

        utils.openFile(self.folder)
        if self.isCanceled():
            return False
        return True


    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
