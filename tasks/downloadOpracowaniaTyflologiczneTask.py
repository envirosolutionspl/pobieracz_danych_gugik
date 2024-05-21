import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils

class DownloadOpracowaniaTyflologiczneTask(QgsTask):
    """QgsTask pobierania opracowań tyflologicznych"""

    def __init__(self, description, folder, url, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.url = url
        self.iface = iface

    def run(self):

        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)

        QgsMessageLog.logMessage('pobieram ' + self.url)
        # fileName = self.url.split("/")[-2]
        print(self.folder)
        service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        if self.isCanceled():
            return False
        return True

    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane opracowania tyflologicznego zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane opracowania tyflologicznego nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
