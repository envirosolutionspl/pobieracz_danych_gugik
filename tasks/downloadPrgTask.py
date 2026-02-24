from qgis.core import QgsApplication, QgsTask, Qgis
from ..utils import MessageUtils, ServiceAPI


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
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        MessageUtils.pushLogInfo(f'Pobieram {self.url}')
        is_success, message = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.exception = message
        return is_success and not self.isCanceled()

    def finished(self, result):
        if result:
            MessageUtils.pushLogInfo('Pobrano dane PRG')
            MessageUtils.pushSuccess(self.iface, "Udało się! Dane PRG zostały pobrane.")
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            MessageUtils.pushLogInfo(f"Nie udało się pobrać danych PRG. Wystąpił błąd: {error_msg}")
            MessageUtils.pushWarning(self.iface, f"Dane PRG nie zostały pobrane: {error_msg}")

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych PRG')
        super().cancel()
