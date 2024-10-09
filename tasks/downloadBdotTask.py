from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
    )


from ..constants import BDOT_FORMAT_URL_MAPPING
from .. import service_api


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
        self._construct_url(level, teryt, format_danych)

    def _construct_url(self, level: int, teryt: str, data_format: str) -> None:
        prefix = BDOT_FORMAT_URL_MAPPING.get(data_format)
        data_format = data_format.strip().split()[0]
        if level == 0:
            self.url = f"{prefix}Polska_{data_format}.zip"
        elif level == 1:
            self.url = f"{prefix}{teryt}/{teryt}_{data_format}.zip"
        elif level == 2:
            self.url = f"{prefix}{teryt[:2]}/{teryt}_{data_format}.zip"

    def run(self):
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        QgsMessageLog.logMessage(f'pobieram {self.url}')
        self.result, self.exception = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        print(self.exception)
        if result and self.exception != 'Połączenie zostało przerwane':
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane BDOT10k zostały pobrane.',
                level=Qgis.Success,
                duration=10
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage('exception')
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane BDOT10k nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
