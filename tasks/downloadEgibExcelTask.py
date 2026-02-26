from qgis.core import (
    QgsTask, Qgis
)

from ..constants import EGIB_WMS_URL, EGIB_TERYT_MAPPING, TIMEOUT_MS
from ..utils import MessageUtils, NetworkUtils, ServiceAPI

class DownloadEgibExcelTask(QgsTask):
    """QgsTask pobierania zestawień zbiorczych EGiB"""

    def __init__(self, description, folder, egib_excel_zakres_danych, rok, teryt_powiat, teryt_wojewodztwo, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.zakres_danych = egib_excel_zakres_danych
        self.rok = rok
        self.teryt_powiat = teryt_powiat
        self.teryt_wojewodztwo = teryt_wojewodztwo
        self.iface = iface
        self.service_api = ServiceAPI()
        self.network_utils = NetworkUtils()

    def run(self):
        list_url = []
        if self.zakres_danych == 'powiat':
            url_czesc = f"{EGIB_WMS_URL}{self.rok}/{self.teryt_wojewodztwo}/{self.teryt_powiat}"
        elif self.zakres_danych == 'wojew':
            nazwa_teryt_wojewodztwa = ''

            for k, v in EGIB_TERYT_MAPPING.items():
                if v == self.teryt_wojewodztwo:
                    nazwa_teryt_wojewodztwa = k

            url_czesc = f"{EGIB_WMS_URL}{self.rok}/{self.teryt_wojewodztwo}/{nazwa_teryt_wojewodztwa}"
        elif self.zakres_danych == 'kraj':
            # zmiana nazwy pliku dla całego kraju od 2024 z Polska na PL
            if self.rok < '2024':
                url_czesc = f"{EGIB_WMS_URL}{self.rok}/Polska"
            else:
                url_czesc = f"{EGIB_WMS_URL}{self.rok}/PL"

        list_url.append(url_czesc + '.xlsx')
        list_url.append(url_czesc + '.xls')

        for url in list_url:
            if self.isCanceled():
                return False
            success_check, result_check = self.network_utils.fetchContent(url, timeout_ms=TIMEOUT_MS)
            if not success_check:
                MessageUtils.pushLogWarning(f"Błąd sprawdzania dostępności {url}: {result_check}. Pomijam.")
                continue
            MessageUtils.pushLogInfo('pobieram ' + url)
            res, self.exception = self.service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
            if res:
                return True
            else:
                MessageUtils.pushLogWarning(f"Błąd pobierania pliku {url}: {self.exception}. Pomijam.")
                continue
        return False

    def finished(self, result):
        
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane zestawień zbiorczych EGiB')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane zestawień zbiorczych EGiB zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych zestawień zbiorczych EGiB')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych zestawień zbiorczych EGiB. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Nie udało się pobrać danych zestawień zbiorczych EGiB.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych zestawień zbiorczych EGiB')
        super().cancel()
