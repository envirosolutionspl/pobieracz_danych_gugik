from qgis.core import (
    QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface

from constants import TREES3D_URL
from .. import service_api
from ..wfs.httpsAdapter import get_legacy_session


class DownloadTrees3dTask(QgsTask):
    task_finished = pyqtSignal(object, object)

    def __init__(self, description, folder, teryt_powiat):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.result = None
        self.task_finished.connect(self.finished)

    def run(self):
        trees_url = f'{TREES3D_URL}{self.teryt_powiat[:2]}/{self.teryt_powiat}.zip'
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        with get_legacy_session().get(url=trees_url, verify=False) as resp:
            if str(resp.status_code) == '200':
                if self.isCanceled():
                    QgsMessageLog.logMessage('isCanceled')
                    return False
                QgsMessageLog.logMessage(f'pobieram {trees_url}')
                self.result = service_api.retreiveFile(url=trees_url, destFolder=self.folder, obj=self)
        self.task_finished.emit(self.result, self.exception)
        return True

    def finished(self, result):
        if result:
            msgbox = QMessageBox(QMessageBox.Information, 'Komunikat', 'Pobrano ')
            msgbox.exec_()
            QgsMessageLog.logMessage('sukces')
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage('exception')
                raise self.exception
            iface.messageBar().pushWarning(
                'Błąd',
                'Dane nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()


