import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from qgis.PyQt.QtWidgets import QMessageBox
from .. import service_api, utils
import requests

class DownloadArchiwalnyBdotTask(QgsTask):
    """QgsTask pobierania dane archiwalne BDOT10k"""

    def __init__(self, description, folder, format_danych, teryt, rok, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.page_exist = None
        self.folder = folder
        self.exception = None
        self.url = f"https://opendata.geoportal.gov.pl/Archiwum/bdot10k/{rok}/{format_danych}/{teryt[0:2]}/{teryt}_{format_danych}.zip"
        self.iface = iface

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)

        with requests.get(self.url, verify=True) as req:
            if str(req.status_code) == '404':
                self.page_exist = 'NO'
                return False
            else:
                self.page_exist = 'YES'
                QgsMessageLog.logMessage('pobieram ' + self.url)
                # fileName = self.url.split("/")[-1]
                service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
                # self.setProgress(self.progress() + 100 / total)
                utils.openFile(self.folder)
                if self.isCanceled():
                    return False
                return True


    def finished(self, result):

        if self.page_exist == 'NO':
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Archiwalne dane BDOT10k zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Archiwalne dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
