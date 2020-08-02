from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )
from . import ortofoto_api

class DownloadOrtofotoTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, ortoList, folder):
        super().__init__(description, QgsTask.CanCancel)
        self.ortoList = ortoList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.ortoList)

        for orto in self.ortoList:
            QgsMessageLog.logMessage('start ' + orto.url)
            self.setProgress(self.progress()+100/total)
            fileName = orto.url.split("/")[-1]
            ortofoto_api.retreiveFile(orto.url, self.folder)

        if self.isCanceled():
            return False
        return True

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
        if result:
            QgsMessageLog.logMessage('sukces')
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('ggg')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()