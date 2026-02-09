from qgis.core import QgsApplication, QgsTask, Qgis
from .. import service_api
from ..utils import pushLogInfo


class DownloadOpracowaniaTyflologiczneTask(QgsTask):
    """QgsTask pobierania opracowań tyflologicznych"""

    def __init__(self, description, folder, url, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.url = url
        self.iface = iface

    def run(self):
        pushLogInfo(f'Started task "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        _, self.exception = service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):

        if result and self.exception:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane opracowania tyflologicznego zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                pushLogInfo('finished with false')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("exception")
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane opracowania tyflologicznego nie zostały pobrane.")

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
