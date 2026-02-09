import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, Qgis
    )
from ..service_api import ServiceAPI
from ..utils import pushLogInfo, create_report
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
        pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        results = []
        for las in self.lasList:
            las_url = las.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {las_url}')
            success, message = self.service_api.retreiveFile(url=las_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / self.total)
            results.append(success)
            if success:
                self.success_count += 1
            else:
                self.errors.append(f"{las.get('url')}: {message}")
        
        # jeżeli nie pobrał się żaden plik, to zwracamy False
        if self.success_count == 0:
            return False

        create_report(
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
            pushLogInfo("Nie udało się pobrać żadnych plików LAZ")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Nie udało się pobrać żadnych plików LAZ'
            )
            return

        if self.success_count == self.total:
            pushLogInfo('Pobrano wszystkie dane LAZ')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Wszystkie dane LAZ zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            pushLogInfo(f"Pobrano {self.success_count}/{self.total} plików LAZ")
            if self.errors:
                pushLogInfo("Nie pobrano plików:\n" + "\n".join(self.errors))
            self.iface.messageBar().pushWarning(
                'Częściowy sukces',
                f"Pobrano {self.success_count}/{self.total} plików LAZ"
            )


    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych LAZ')
        super().cancel()



