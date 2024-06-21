from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface

from ..constants import TREES3D_URL
from .. import service_api
from ..wfs.httpsAdapter import get_legacy_session


class DownloadTrees3dTask(QgsTask):
    def __init__(self, description, folder, teryt_powiat, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.result = None
        self.iface = iface
        self.liczba_poprawny_plik = []

    def run(self):
        trees_url = f'{TREES3D_URL}{self.teryt_powiat[:2]}/{self.teryt_powiat}.zip'
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        with get_legacy_session().get(url=trees_url, verify=False) as resp:
            if str(resp.status_code) == '200':
                if self.isCanceled():
                    QgsMessageLog.logMessage('isCanceled')
                    return False
                self.liczba_poprawny_plik.append(trees_url)
                QgsMessageLog.logMessage(f'pobieram {trees_url}')
                self.result = service_api.retreiveFile(url=trees_url, destFolder=self.folder, obj=self)

        if len(self.liczba_poprawny_plik) == 0:
            return False
        else:
            return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces",
                                                "Udało się! Dane z modelami 3D drzew zostały pobrane.",
                                                level=Qgis.Success,
                                                duration=10)
        else:
            if len(self.liczba_poprawny_plik) == 0:
                msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                     "Nie znaleniono danych spełniających kryteria")
                msgbox.exec_()
            else:
                self.iface.messageBar().pushMessage("Błąd",
                                                    "z modelami 3D drzew nie zostały pobrane.",
                                                    level=Qgis.Warning,
                                                    duration=10)

            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception


    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()


