import os
from qgis.core import QgsTask
from ..utils import MessageUtils, FileUtils, ServiceAPI
from ..constants import HEADERS_MAPPING

class DownloadReflectanceTask(QgsTask):
    """QgsTask pobierania intensywności"""

    def __init__(self, description, reflectanceList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.reflectanceList = reflectanceList
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
        total = len(self.reflectanceList)
        results = []
        for reflectance in self.reflectanceList:
            reflectance_url = reflectance.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {reflectance_url}')
            res, self.exception = self.service_api.retreiveFile(url=reflectance_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
        
        FileUtils.createReport(os.path.join(self.folder, 'pobieracz_intensywnosc'), HEADERS_MAPPING['REFLECTANCE_HEADERS'], self.reflectanceList)

        return True

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
            MessageUtils.pushLogInfo('Pobrano dane obrazów intensywności')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane obrazów intensywności zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych obrazów intensywności')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych obrazów intensywności. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane obrazów intensywności nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych obrazów intensywności')
        super().cancel()
