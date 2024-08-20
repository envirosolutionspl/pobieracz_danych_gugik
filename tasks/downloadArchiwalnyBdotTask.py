from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)
from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import BDOT_WMS_URL
from .. import service_api, utils
from ..wfs.httpsAdapter import get_legacy_session

class DownloadArchiwalnyBdotTask(QgsTask):
    """QgsTask pobierania dane archiwalne BDOT10k"""

    def __init__(self, description, folder, format_danych, teryt, rok, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.page_exist = None
        self.folder = folder
        self.exception = None
        self.url = f'{BDOT_WMS_URL}{rok}/{format_danych}/{teryt[:2]}/{teryt}_{format_danych}.zip'
        self.iface = iface
        self.result = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        with get_legacy_session().get(url=self.url, verify=False) as resp:
            if str(resp.status_code) == '404':
                self.page_exist = 'NO'
                return False
            else:
                self.page_exist = 'YES'
                QgsMessageLog.logMessage(f'pobieram {self.url}')
                # fileName = self.url.split("/")[-1]
                self.result, self.exception = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
                return not self.isCanceled()


    def finished(self, result):
        if self.page_exist == 'NO':
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Archiwalne dane BDOT10k zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise ConnectionError(self.exception)
            self.iface.messageBar().pushWarning("Błąd",
                                                "Archiwalne dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
