from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)
from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import BUDYNKI_3D_WMS_URL
from .. import service_api, utils
from ..wfs.httpsAdapter import get_legacy_session


class DownloadModel3dTask(QgsTask):
    """QgsTask pobierania modeli 3D"""

    def __init__(self, description, folder, teryt_powiat, teryt_wojewodztwo, standard, data_lista, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.teryt_wojewodztwo = teryt_wojewodztwo
        self.standard = standard
        self.data_lista = data_lista
        self.iface = iface

    def run(self):
        list_url = []
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        for standard in self.standard:
            for rok in self.data_lista:
                list_url.extend(
                    (
                        f'{BUDYNKI_3D_WMS_URL}{standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}.zip',
                        f'{BUDYNKI_3D_WMS_URL}{standard}/{rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}_gml.zip',
                    )
                )
            list_url.extend(
                (
                    f'{BUDYNKI_3D_WMS_URL}{standard}/{self.teryt_powiat}_gml.zip',
                    f'{BUDYNKI_3D_WMS_URL}{standard}/{self.teryt_powiat}.zip',
                )
            )
        results = []
        for url in list_url:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'pobieram {url}')
            res, self.exception = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
            results.append(res)
        return any(results)

    def finished(self, result):
        if result and self.exception:
            msgbox = QMessageBox(
                QMessageBox.Information,
                'Komunikat',
                f'Pobrano {len(self.liczba_dobrych_url)} pliki z danymi'
            )
            msgbox.exec_()
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane modelu 3D budynków zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane modelu 3D budynków nie zostały pobrane.'
            )
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")


    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
