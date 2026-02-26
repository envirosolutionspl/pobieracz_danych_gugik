import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, Qgis
    )
from ..utils import MessageUtils, FileUtils, ServiceAPI
from ..constants import HEADERS_MAPPING




class DownloadLasTask(QgsTask):
    """QgsTask pobierania LAZ"""

    def __init__(self, description, lasList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.lasList = lasList
        self.folder = folder
        self.total = len(self.lasList)
        self.iterations = 0
        self.exception = None
        self.iface = iface
        self.service_api = ServiceAPI()
        self.errors = []
        self.success_count = 0


    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        results = []
        for las in self.lasList:
            las_url = las.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {las_url}')
            is_success, message = self.service_api.retreiveFile(url=las_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / self.total)
            results.append(is_success)
            if is_success:
                self.success_count += 1
            else:
                self.errors.append(f"{las.get('url')}: {message}")
        
        # jeżeli nie pobrał się żaden plik, to zwracamy False
        if self.success_count == 0:
            return False

        FileUtils.createReport(
            os.path.join(self.folder, 'pobieracz_las'),
            HEADERS_MAPPING['LAS_HEADERS'],
            self.lasList
        )
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
        if not result:
            MessageUtils.pushLogWarning("Nie udało się pobrać żadnych plików LAZ")
            MessageUtils.pushWarning(self.iface, 'Nie udało się pobrać żadnych plików LAZ')
            return

        if self.success_count == self.total:
            MessageUtils.pushLogInfo('Pobrano wszystkie dane LAZ')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Wszystkie dane LAZ zostały pobrane.')
        else:
            MessageUtils.pushLogInfo(f"Pobrano {self.success_count}/{self.total} plików LAZ")
            if self.errors:
                MessageUtils.pushLogWarning("Nie pobrano plików:\n" + "\n".join(self.errors))
            MessageUtils.pushWarning(self.iface, f"Pobrano {self.success_count}/{self.total} plików LAZ")


    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych LAZ')
        super().cancel()



