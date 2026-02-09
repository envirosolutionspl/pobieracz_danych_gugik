from qgis.core import (
    QgsTask, Qgis
    )

from ..constants import BDOT_FORMAT_URL_MAPPING
from .. import service_api
from ..utils import pushLogInfo


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
        pushLogInfo(f'Started task "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        success, message = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.result = success
        self.exception = message
        
        if not self.result:
            self._construct_url(self.level, self.teryt, self.format_danych, upper=True)
            pushLogInfo(f'Próba 2: pobieram {self.url}')
            success, message = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
            self.result = success
            self.exception = message
            
        return self.result and not self.isCanceled()

    def finished(self, result):
        if result:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane BDOT10k zostały pobrane.',
                level=Qgis.Success,
                duration=10
            )
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            pushLogInfo(f'Błąd pobierania: {error_msg}')
            self.iface.messageBar().pushWarning(
                'Błąd',
                f'Dane BDOT10k nie zostały pobrane: {error_msg}'
            )

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
