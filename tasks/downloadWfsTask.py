import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils

class DownloadWfsTask(QgsTask):
    """QgsTask pobierania WFS"""

    def __init__(self, description, urlList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.urlList = urlList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.iface = iface


    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.urlList)
        objs = 0

        for url in self.urlList:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            fileName = url.split("/")[-1]
            QgsMessageLog.logMessage(f'start {fileName}')
            status, _ = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
            if status is True:
                objs += 1
            self.setProgress(self.progress() + 100 / total)
        return objs == total

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        
        if result is True:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane WFS zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )

        elif result is False:
            self.iface.messageBar().pushMessage(
                'Ostrzeżenie:', 
                'Nie pobrano pełnego zbioru danych',
                level=Qgis.Warning,
                duration=5)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage('exception')
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane WFS nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
