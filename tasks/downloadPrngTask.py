from qgis.core import QgsTask
from ..constants import PRNG_WMS_URL
from ..utils import MessageUtils, ServiceAPI

class DownloadPrngTask(QgsTask):
    """QgsTask pobierania PRNG"""

    def __init__(self, description, folder, rodzaj, format_danych, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.rodzaj = rodzaj
        self.format_danych = format_danych
        self.exception = None
        self.iface = iface
        self.url = f"{PRNG_WMS_URL}{self.rodzaj}_{self.format_danych}.zip"
        self.service_api = ServiceAPI()

    def run(self):
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        MessageUtils.pushLogInfo(f'Pobieram {self.url}')
        _, self.exception = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane PRNG')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane PRNG zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych PRNG')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych PRNG. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane PRNG nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych PRNG')
        super().cancel()
