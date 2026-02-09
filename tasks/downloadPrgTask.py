import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from .. import service_api
from ..utils import pushLogInfo


class DownloadPrgTask(QgsTask):
    """QgsTask pobierania PRG"""

    def __init__(self, description, folder, url, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.url = url
        self.iface = iface

    def run(self):
        pushLogInfo(f'Started task "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        success, message = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        self.exception = message
        return success and not self.isCanceled()

    def finished(self, result):
        if result:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane PRG zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            pushLogInfo(f"Błąd PRG: {error_msg}")
            self.iface.messageBar().pushWarning("Błąd",
                                                f"Dane PRG nie zostały pobrane: {error_msg}")

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
