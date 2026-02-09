import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo


class DownloadPrgTask(QgsTask):
    """QgsTask pobierania PRG"""

    def __init__(self, description, folder, url, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.url = url
        self.iface = iface
        self.service_api = ServiceAPI()

    def run(self):
        pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        success, message = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.exception = message
        return success and not self.isCanceled()

    def finished(self, result):
        if result:
            pushLogInfo('Pobrano dane PRG')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane PRG zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            pushLogInfo(f"Nie udało się pobrać danych PRG. Wystąpił błąd: {error_msg}")
            self.iface.messageBar().pushWarning("Błąd",
                                                f"Dane PRG nie zostały pobrane: {error_msg}")

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych PRG')
        super().cancel()
