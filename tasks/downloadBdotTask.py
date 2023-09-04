import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils


class DownloadBdotTask(QgsTask):
    """QgsTask pobierania BDOT10k"""

    def __init__(self, description, folder, level, format_danych, teryt, iface):
        """
        level:
        0 - cały kraj
        1 - województwo
        2 - powiat
        """
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        # self.total = 0
        # self.iterations = 0
        self.exception = None
        self.format_danych=format_danych
        self.iface = iface

        if format_danych == 'GML':
            if level == 0:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/Polska_{format_danych}.zip"
            elif level == 1:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{teryt}/{teryt}_{format_danych}.zip"
            elif level == 2:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{teryt[:2]}/{teryt}_{format_danych}.zip"
        elif format_danych == 'SHP':
            if level == 0:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{format_danych}/Polska_{format_danych}.zip"
            elif level == 1:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{format_danych}/{teryt}/{teryt}_{format_danych}.zip"
            elif level == 2:
                self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{format_danych}/{teryt[:2]}/{teryt}_{format_danych}.zip"

    def run(self):

        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)


        QgsMessageLog.logMessage('pobieram ' + self.url)
        # fileName = self.url.split("/")[-1]
        service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        # self.setProgress(self.progress() + 100 / total)

        utils.openFile(self.folder)
        if self.isCanceled():
            return False
        return True

    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane BDOT10k zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
