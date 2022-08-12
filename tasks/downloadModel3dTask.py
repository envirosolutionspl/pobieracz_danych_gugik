import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QMessageBox
from .. import service_api, utils
import requests


class DownloadModel3dTask(QgsTask):
    """QgsTask pobierania PRG"""

    def __init__(self, description, folder, teryt_powiat, teryt_wojewodztwo, standard, data_lista, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.teryt_wojewodztwo = teryt_wojewodztwo
        self.standard = standard
        self.data_lista = data_lista
        self.liczba_dobrych_url = []
        self.iface = iface

    def run(self):
        list_url = []
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)

        for standard in self.standard:
            for rok in self.data_lista:
                url1 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}.zip"
                url2 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}_gml.zip"
                list_url.append(url1)
                list_url.append(url2)
            url3 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{standard}/{self.teryt_powiat}_gml.zip"
            url4 = f"https://opendata.geoportal.gov.pl/InneDane/Budynki3D/{standard}/{self.teryt_powiat}.zip"
            list_url.append(url3)
            list_url.append(url4)

        for url in list_url:
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
            # print("liczba_dobrych_url", len(self.liczba_dobrych_url))
            utils.openFile(self.folder)
            if self.isCanceled():
                return False
            return True

    def finished(self, result):

        if result:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", f"Pobrano {len(self.liczba_dobrych_url)} pliki z danymi")
            msgbox.exec_()
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushSuccess("Sukces",
                                                "Udało się! Dane modelu 3D budynków zostały pobrane.")
        else:
            if len(self.liczba_dobrych_url) == 0:
                msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                     "Nie znaleniono danych spełniających kryteria")
                msgbox.exec_()
            else:
                self.iface.messageBar().pushWarning("Błąd",
                                                    "Dane modelu 3D budynków nie zostały pobrane.")

            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception


    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
