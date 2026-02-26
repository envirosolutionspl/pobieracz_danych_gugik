from qgis.core import (
    QgsTask, Qgis
)

from ..constants import BDOT_WMS_URL
from ..utils import MessageUtils, ServiceAPI


class DownloadArchiwalnyBdotTask(QgsTask):
    """QgsTask pobierania dane archiwalne BDOT10k"""

    def __init__(self, description, folder, format_danych, teryt, rok, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.page_exist = None
        self.folder = folder
        self.exception = None
        self.url = f'{BDOT_WMS_URL}{rok}/{format_danych}/{teryt[:2]}/{teryt}_{format_danych}_{rok}.zip'
        self.iface = iface
        self.result = None
        self.service_api = ServiceAPI()

    def run(self):
        MessageUtils.pushLogInfo('Rozpoczęto zadanie: "{}"'.format(self.description()))
        MessageUtils.pushLogInfo(f'Pobieram {self.url}')
        # fileName = self.url.split("/")[-1]
        self.result, self.exception = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        if self.page_exist == 'NO':
            MessageUtils.pushLogWarning(f"Nie znaleniono danych spełniających kryteria: {self.url}")
            MessageUtils.pushWarning(self.iface, "Nie znaleniono danych spełniających kryteria")

        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane archiwalne BDOT10k')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Archiwalne dane BDOT10k zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych archiwalnych BDOT10k')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych archiwalnych BDOT10k. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, "Archiwalne dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych archiwalnych BDOT10k')
        super().cancel()
