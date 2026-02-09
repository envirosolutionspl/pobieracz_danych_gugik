from qgis.core import (
    QgsTask, Qgis
)

from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import BDOT_WMS_URL
from ..service_api import ServiceAPI
from ..utils import pushLogInfo


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
        self.service_api = ServiceAPI()

    def run(self):
        pushLogInfo('Rozpoczęto zadanie: "{}"'.format(self.description()))
        pushLogInfo(f'pobieram {self.url}')
        # fileName = self.url.split("/")[-1]
        self.result, self.exception = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        if self.page_exist == 'NO':
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()

        if result and self.exception:
            pushLogInfo('Pobrano dane archiwalne BDOT10k')
            self.iface.messageBar().pushMessage(
                "Sukces", 
                "Udało się! Archiwalne dane BDOT10k zostały pobrane.",
                level=Qgis.Success, 
                duration=0
            )
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrac dane archiwalne BDOT10k')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("exception")
            self.iface.messageBar().pushWarning("Błąd",
                                                "Archiwalne dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych archiwalnych BDOT10k')
        super().cancel()
