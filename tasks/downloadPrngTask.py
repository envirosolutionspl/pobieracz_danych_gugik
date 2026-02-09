import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis

from ..constants import PRNG_WMS_URL
from .. import service_api
from ..utils import pushLogInfo


class DownloadPrngTask(QgsTask):
    """QgsTask pobierania PRNG"""

    def __init__(self, description, folder, rodzaj, format_danych, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.rodzaj = rodzaj
        self.format_danych = format_danych
        self.exception = None
        self.iface = iface
        self.url = f"{PRNG_WMS_URL}{self.rodzaj}_{self.format_danych}.zip"

    def run(self):
        pushLogInfo(f'Started task "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        _, self.exception = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):
        if result and self.exception:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane PRNG zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                pushLogInfo('finished with false')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane PRNG nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
