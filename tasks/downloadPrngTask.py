import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils


class DownloadPrngTask(QgsTask):
    """QgsTask pobierania PRNG"""

    def __init__(self, description, folder, rodzaj, format_danych, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.rodzaj = rodzaj
        self.format_danych = format_danych
        self.exception = None
        self.iface = iface
        self.url = f"https://opendata.geoportal.gov.pl/prng/PRNG_{self.rodzaj}_{self.format_danych}.zip"

    def run(self):

        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)


        QgsMessageLog.logMessage('pobieram ' + self.url)
        # fileName = self.url.split("/")[-1]
        service_api.retreiveFile(url=self.url, destFolder=self.folder)
        # self.setProgress(self.progress() + 100 / total)

        utils.openFile(self.folder)
        if self.isCanceled():
            return False
        return True

    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane PRNG zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane PRNG nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
