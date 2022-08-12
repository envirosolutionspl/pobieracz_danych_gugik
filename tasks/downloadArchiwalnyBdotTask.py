import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)
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

        r = requests.get(self.url)
        if str(r.status_code) == '404':
            self.page_exist = 'NO'
            return False
        else:
            self.page_exist = 'YES'
            QgsMessageLog.logMessage('pobieram ' + self.url)
            # fileName = self.url.split("/")[-1]
            service_api.retreiveFile(url=self.url, destFolder=self.folder)
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
            self.iface.messageBar().pushSuccess("Sukces",
                                                "Udało się! Dane archiwalnej bazy BDOT10k zostały pobrane.")
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane archiwalnej bazy BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
