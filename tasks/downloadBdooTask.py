import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )
from .. import service_api, utils


class DownloadBdooTask(QgsTask):
    """QgsTask pobierania BDOO"""

    def __init__(self, description, folder, level=1, teryt=None):
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
        if level == 0:
            pass
            # self.url = "https://opendata.geoportal.gov.pl/bdot10k/Polska_GML.zip"
        elif level == 1:
            self.url = f"http://opendata.geoportal.gov.pl/bdoo/PL.PZGiK.201.{teryt}.zip"
        elif level == 2:
            pass
            # self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{teryt[:2]}/{teryt}_GML.zip"

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
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()