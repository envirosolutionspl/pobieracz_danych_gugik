import os
from qgis.core import QgsTask
from ..utils import MessageUtils, ServiceAPI

class DownloadWfsTask(QgsTask):
    """QgsTask pobierania WFS"""

    def __init__(self, description, urlList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.urlList = urlList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.iface = iface
        self.service_api = ServiceAPI()


    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.urlList)
        objs = 0

        for url in self.urlList:
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            fileName = url.split("/")[-1]
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {fileName}')
            status, self.exception = self.service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
            if status is True:
                objs += 1
            self.setProgress(self.progress() + 100 / total)
        return objs == total

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane WFS')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane WFS zostały pobrane.')

        elif result is False:
            MessageUtils.pushLogWarning('Nie pobrano pełnego zbioru danych')
            MessageUtils.pushWarning(self.iface, 'Nie pobrano pełnego zbioru danych')
        else:
            if self.exception is None:
               MessageUtils.pushLogWarning('Nie udało się pobrać danych WFS')
            elif isinstance(self.exception, BaseException):
               MessageUtils.pushLogWarning('Nie udało się pobrać danych WFS. Wystąpił błąd: ' + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane WFS nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych WFS')
        super().cancel()
