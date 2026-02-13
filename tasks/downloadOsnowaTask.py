from qgis.core import QgsTask, Qgis

from ..constants import OSNOWA_WMS_URL, TIMEOUT_MS
from ..utils import MessageUtils, NetworkUtils, ServiceAPI


class DownloadOsnowaTask(QgsTask):
    def __init__(self, description, folder, teryt_powiat, typ, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.typ = typ
        self.iface = iface
        self.service_api = ServiceAPI()
        self.network_utils = NetworkUtils()

    def run(self):
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
            
        for typ in self.typ:
            url = f"{OSNOWA_WMS_URL}teryt={self.teryt_powiat}&typ={typ}"
                
            if self.isCanceled():
                return False
            success_check, result_check = self.network_utils.fetchContent(url, timeout_ms=TIMEOUT_MS*2)

            if not success_check:
                MessageUtils.pushLogCritical(f'Błąd przy sprawdzaniu dostępności {url}: {result_check}')
                return False
                    
            MessageUtils.pushLogInfo(f'Pobieram {url}')
                
            res, self.exception = self.service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
                
            if not res:
                MessageUtils.pushLogCritical(f'Błąd przy pobieraniu pliku {url}: {self.exception}')
                return False
        return True

    def finished(self, result):
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane podstawowej osnowy geodezyjnej')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane podstawowej osnowy geodezyjnej zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych podstawowej osnowy geodezyjnej')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych podstawowej osnowy geodezyjnej. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane podstawowej osnowy geodezyjnej nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych podstawowej osnowy geodezyjnej')
        super().cancel()
