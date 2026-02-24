from qgis.core import (
    QgsTask, Qgis
    )

from ..constants import BDOT_FORMAT_URL_MAPPING
from ..utils import MessageUtils, ServiceAPI


class DownloadBdotTask(QgsTask):
    """QgsTask pobierania BDOT10k"""

    def __init__(self, description, folder, level, format_danych, teryt, iface):
        """
        level:
        0 - cały kraj
        1 - województwo
        2 - powiat
        """
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.iface = iface
        self.result = None
        self.level = level
        self.teryt = teryt
        self.format_danych = format_danych
        self._construct_url(level, teryt, format_danych)
        self.service_api = ServiceAPI()

    def _construct_url(self, level: int, teryt: str, data_format: str, upper: bool = False) -> None:
        prefix = BDOT_FORMAT_URL_MAPPING.get(data_format)
        data_format = data_format.strip().split()[0]
        zip_suffix = "zip"
        if upper:
            zip_suffix = zip_suffix.upper()
        if level == 0:
            self.url = f"{prefix}Polska_{data_format}.{zip_suffix}"
        elif level == 1:
            self.url = f"{prefix}{teryt}/{teryt}_{data_format}.{zip_suffix}"
        elif level == 2:
            self.url = f"{prefix}{teryt[:2]}/{teryt}_{data_format}.{zip_suffix}"

    def run(self):
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        MessageUtils.pushLogInfo(f'Pobieram {self.url}')
        is_success, message = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.result = is_success
        self.exception = message
        
        if not self.result:
            self._construct_url(self.level, self.teryt, self.format_danych, upper=True)
            MessageUtils.pushLogInfo(f'Próba 2: Pobieram {self.url}')
            is_success, message = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
            self.result = is_success
            self.exception = message
            
        return self.result and not self.isCanceled()

    def finished(self, result):
        if result:
            MessageUtils.pushLogInfo('Pobrano dane BDOT10k')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane BDOT10k zostały pobrane.')
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            MessageUtils.pushLogWarning(f'Błąd podczas pobierania danych BDOT10k: {error_msg}')
            MessageUtils.pushWarning(self.iface, f'Dane BDOT10k nie zostały pobrane')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych BDOT10k')
        super().cancel()
