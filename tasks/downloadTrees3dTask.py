from qgis.core import (
    QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QMessageBox
from .. import service_api
from ..wfs.httpsAdapter import get_legacy_session


class DownloadTrees3dTask(QgsTask):
    def __init__(self, description, folder, teryt_powiat):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.url = f'https://opendata.geoportal.gov.pl/InneDane/Drzewa3D/LOD1/2023/{teryt_powiat[:2]}/{teryt_powiat}.zip'

    def run(self):
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        with get_legacy_session().get(url=self.url, verify=False) as resp:
            if str(resp.status_code) == '200':
                if self.isCanceled():
                    QgsMessageLog.logMessage('isCanceled')
                    return False
                QgsMessageLog.logMessage(f'pobieram {self.url}')
                service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
                return True
        return True

    def finished(self, result):
        if result:
            msgbox = QMessageBox(QMessageBox.Information, 'Komunikat', 'Pobrano ')
            msgbox.exec_()
            QgsMessageLog.logMessage('sukces')

        elif self.exception is None:
            QgsMessageLog.logMessage('finished with false')
        else:
            QgsMessageLog.logMessage('exception')
            raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()


