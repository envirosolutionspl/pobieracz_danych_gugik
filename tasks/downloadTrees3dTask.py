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
    """QgsTask pobierania modeli 3D drzew"""

    def __init__(self, description, folder, teryt_powiat, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.result = None
        self.iface = iface

    def run(self):
        trees_url = f'{TREES3D_URL}{self.teryt_powiat[:2]}/{self.teryt_powiat}.zip'
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        with get_legacy_session().get(url=trees_url, verify=False) as resp:
            if str(resp.status_code) != '200':
                return False
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'pobieram {trees_url}')
            self.result, self.exception = service_api.retreiveFile(url=trees_url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        if result and not self.exception:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces",
                                                "Udało się! Dane z modelami 3D drzew zostały pobrane.",
                                                level=Qgis.Success,
                                                duration=10)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Dane z modelami 3D drzew nie zostały pobrane.',
                level=Qgis.Warning,
                duration=10
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()


