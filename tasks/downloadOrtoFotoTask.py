import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo, create_report
from ..constants import HEADERS_MAPPING

class DownloadOrtofotoTask(QgsTask):
    """QgsTask pobierania ortofotomap"""

    def __init__(self, description, ortoList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.ortoList = ortoList
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
        total = len(self.ortoList)
        results = []
        for orto in self.ortoList:
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            orto_url = orto.get('url')
            if not orto_url:
                continue
            pushLogInfo(f'start {orto_url}')
            success, message = self.service_api.retreiveFile(url=orto_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(success)
            if not success:
                self.exception = message

        if not any(results):
            return False
            
        if all(results):
            self.exception = True
            
        create_report(os.path.join(self.folder, 'pobieracz_ortofoto'), HEADERS_MAPPING['ORTHOPHOTO_HEADERS'], self.ortoList)
        
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
            pushLogInfo('Pobrano dane ortofotomapy')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane z ortofotomapy zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Nieznany błąd"
            pushLogInfo(f"Nie udało się pobrać danych ortofotomapy. Wystąpił błąd: {error_msg}")
            self.iface.messageBar().pushWarning(
                'Błąd',
                f'Dane z ortofotomapy nie zostały pobrane: {error_msg}'
            )

    def cancel(self):
        pushLogInfo('Anulowano pobieranie ortofotomapy')
        super().cancel()

 