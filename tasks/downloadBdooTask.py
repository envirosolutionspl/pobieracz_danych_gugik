import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )

from ..constants import BDOO_WMS_URL
from .. import service_api, utils


class DownloadBdooTask(QgsTask):
    """QgsTask pobierania BDOO"""

    def __init__(self, description, folder, level, rok, teryt, iface):
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
        if level == 0:
            self.url = f"{BDOO_WMS_URL}{rok}/Polska_BDOO.zip"
        elif level == 1:
            self.url = f"{BDOO_WMS_URL}{rok}/PL.PZGiK.201.{teryt}.zip"
        elif level == 2:
            pass
            # self.url = f"https://opendata.geoportal.gov.pl/bdot10k/{teryt[:2]}/{teryt}_GML.zip"

        self.iface = iface

    def run(self):
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        QgsMessageLog.logMessage(f'pobieram {self.url}')
        success, message = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.exception = message
        return success and not self.isCanceled()

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane BDOO zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            QgsMessageLog.logMessage(f"Błąd BDOO: {error_msg}")
            self.iface.messageBar().pushWarning(
                'Błąd',
                f'Dane BDOO nie zostały pobrane: {error_msg}'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
