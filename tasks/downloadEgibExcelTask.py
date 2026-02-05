from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)

from ..constants import EGIB_WMS_URL, EGIB_TERYT_MAPPING, TIMEOUT_MS
from .. import service_api, utils
from ..network_utils import NetworkUtils

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
                
            try:
                NetworkUtils.fetch_content(url, timeout_ms=TIMEOUT_MS)
                QgsMessageLog.logMessage('pobieram ' + url)
                res, self.exception = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
                if res:
                    return True
                else:
                    return False
            except (TimeoutError, ConnectionError, Exception):
                QgsMessageLog.logMessage(f"Błąd pobierania pliku {url}, pomijam.")
                continue
        
        return False

    def finished(self, result):
        
        if result and self.exception:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane zestawień zbiorczych EGiB zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane zestawień zbiorczych EGiB nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
