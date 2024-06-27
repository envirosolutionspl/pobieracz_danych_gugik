from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
    )

from qgis.PyQt.QtCore import pyqtSignal

from ..constants import BDOT_FORMAT_URL_MAPPING
from .. import service_api, utils


class DownloadBdotTask(QgsTask):
    """QgsTask pobierania BDOT10k"""
    task_finished = pyqtSignal(object, object)

    def __init__(self, description, folder, level, format_danych, teryt, iface):
        """
        level:
        0 - cały kraj
        1 - województwo
        2 - powiat
        """
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        # self.total = 0
        # self.iterations = 0
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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        QgsMessageLog.logMessage('pobieram ' + self.url)
        self.result = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.task_finished.emit(self.result, self.exception)
        if self.isCanceled():
            return False
        return True

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
