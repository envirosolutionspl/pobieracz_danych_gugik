import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QMessageBox
from .. import service_api, utils
import requests


class DownloadModel3dTask(QgsTask):
    """QgsTask pobierania PRG"""

    def __init__(self, description, folder, teryt_powiat, teryt_wojewodztwo, standard, data_lista):

        super().__init__(description, QgsTask.CanCancel)
        self.liczba_dobrych_url = []
        self.list_url = []
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.teryt_wojewodztwo = teryt_wojewodztwo
        self.standard = standard
        self.data_lista = data_lista

    def run(self):

        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)

        for rok in self.data_lista:
            url1 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{self.standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}.zip"
            url2 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{self.standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}_gml.zip"
            url3 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{self.standard}/{self.teryt_powiat}_gml.zip"
            url4 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{self.standard}/{self.teryt_powiat}.zip"
            self.list_url.append(url1)
            self.list_url.append(url2)
            self.list_url.append(url3)
            self.list_url.append(url4)

        for url in self.list_url:
            r = requests.get(url)
            if str(r.status_code) == '200':
                self.liczba_dobrych_url.append(url)
                QgsMessageLog.logMessage('pobieram ' + url)
                # fileName = self.url.split("/")[-2]
                # print(self.folder)
                service_api.retreiveFile(url=url, destFolder=self.folder)
                # self.setProgress(self.progress() + 100 / total)

        if len(self.liczba_dobrych_url) == 0:
            return False
        else:
            utils.openFile(self.folder)
            if self.isCanceled():
                return False
            return True

    def finished(self, result):

        if result:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", f"Pobrano {len(self.liczba_dobrych_url)} pliki z danymi")
            msgbox.exec_()
            QgsMessageLog.logMessage('sukces')
        else:
            if self.exception is None:
                msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
                msgbox.exec_()
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
