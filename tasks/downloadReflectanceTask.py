import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo, create_report
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
        pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.reflectanceList)
        results = []
        for reflectance in self.reflectanceList:
            reflectance_url = reflectance.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {reflectance_url}')
            res, self.exception = self.service_api.retreiveFile(url=reflectance_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
        
        create_report(os.path.join(self.folder, 'pobieracz_intensywnosc'), HEADERS_MAPPING['REFLECTANCE_HEADERS'], self.reflectanceList)

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
            pushLogInfo('Pobrano dane obrazów intensywności')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane obrazów intensywności zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych obrazów intensywności')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych obrazów intensywności. Wystąpił błąd: " + str(self.exception))
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane obrazów intensywności nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych obrazów intensywności')
        super().cancel()
