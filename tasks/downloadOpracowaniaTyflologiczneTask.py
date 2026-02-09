from qgis.core import QgsApplication, QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo


class DownloadOpracowaniaTyflologiczneTask(QgsTask):
    """QgsTask pobierania opracowań tyflologicznych"""

    def __init__(self, description, folder, url, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.url = url
        self.iface = iface
        self.service_api = ServiceAPI()

    def run(self):
        pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        pushLogInfo(f'pobieram {self.url}')
        _, self.exception = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):

        if result and self.exception:
            pushLogInfo('Pobrano dane opracowania tyflologicznego')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane opracowania tyflologicznego zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych opracowania tyflologicznego')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych opracowania tyflologicznego. Wystąpił błąd: " + str(self.exception))
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane opracowania tyflologicznego nie zostały pobrane.")

    def cancel(self):
        pushLogInfo('Anulowano pobieranie opracowania tyflologicznego')
        super().cancel()
