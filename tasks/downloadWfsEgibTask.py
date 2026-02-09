import os, datetime

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QPixmap, QIcon

from qgis.core import QgsApplication, QgsTask, Qgis

from .. import service_api
from ..utils import pushLogInfo, openFile
from ..wfs import WfsEgib


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
        pushLogInfo('Rozpoczęto zadanie: "{}"'.format(self.description()))
        pushLogInfo('start ' + self.wfs_url)

        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.egib_wfs(self.teryt, self.wfs_url, self.folder)
        if self.name_error == 'brak':
            openFile(self.folder)
        if self.isCanceled():
            pushLogInfo('isCanceled')
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
        
        if result and self.name_error == "brak" and self.exception is None:
            pushLogInfo('Pobrano dane EGiB')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane EGiB dla powiatów zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych EGiB')

                msgbox = QMessageBox(QMessageBox.Information, "Informacje o warstwach EGiB ", self.name_error)
                msgbox.setIconPixmap(QPixmap(f"{self.plugin_dir}\\img\\lightbulb.png"))
                msgbox.exec_()
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych EGiB. Wystąpił błąd: " + str(self.exception))


    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych EGiB')
        super().cancel()
