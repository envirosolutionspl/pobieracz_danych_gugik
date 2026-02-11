from qgis.core import QgsApplication, QgsTask, Qgis
from ..utils import MessageUtils, ServiceAPI


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
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        MessageUtils.pushLogInfo(f'Pobieram {self.url}')
        _, self.exception = self.service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        return not self.isCanceled()

    def finished(self, result):

        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane opracowania tyflologicznego')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane opracowania tyflologicznego zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych opracowania tyflologicznego')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych opracowania tyflologicznego. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, "Dane opracowania tyflologicznego nie zostały pobrane.")

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie opracowania tyflologicznego')
        super().cancel()
