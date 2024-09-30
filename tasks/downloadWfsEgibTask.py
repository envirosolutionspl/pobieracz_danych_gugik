import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from qgis.PyQt.QtWidgets import QMessageBox
from .. import service_api, utils
from ..wfs import WfsEgib
from PyQt5.QtGui import QPixmap, QIcon


class DownloadWfsEgibTask(QgsTask):
    """QgsTask pobierania WFS EGiB"""

    def __init__(self, description, folder, teryt, wfs_url, iface, plugin_dir):

        super().__init__(description, QgsTask.CanCancel)
        self.name_error = ""
        self.wfsEgib = None
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.teryt = teryt
        self.wfs_url = wfs_url
        self.iface = iface
        self.plugin_dir = plugin_dir

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        QgsMessageLog.logMessage('start ' + self.wfs_url)

        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.egib_wfs(self.teryt, self.wfs_url, self.folder)
        if self.name_error == 'brak':
            utils.openFile(self.folder)
        if self.isCanceled():
            QgsMessageLog.logMessage('isCanceled')
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

        """W ramach powiatu mogą wystąpić prawidłowe warswy oraz nieprawidłowe - ta informacja zostanie przedstawiona 
        użytkownikowi w osobnym okienku"""

        if result and self.name_error == "brak":
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane EGiB dla powiatów zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')

                msgbox = QMessageBox(QMessageBox.Information, "Informacje o warstwach EGiB ", self.name_error)
                msgbox.setIconPixmap(QPixmap(f"{self.plugin_dir}\\img\\lightbulb.png"))
                msgbox.exec_()
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
                raise self.exception


    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
