import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo, create_report
from ..constants import HEADERS_MAPPING


class DownloadNmtTask(QgsTask):
    """QgsTask pobierania NMT/NMPT"""

    def __init__(self, description, nmtList, folder, isNmpt, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.nmtList = nmtList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.isNmpt = isNmpt
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
        total = len(self.nmtList)
        results = []
        for nmt in self.nmtList:
            nmt_url = nmt.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {nmt_url}')
            res, self.exception = self.service_api.retreiveFile(url=nmt_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
        
        create_report(
            os.path.join(self.folder, 'pobieracz_nmpt' if self.isNmpt else 'pobieracz_nmt'),
            HEADERS_MAPPING['NMT_HEADERS'],
            self.nmtList
        )
        return not self.isCanceled()

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
            pushLogInfo('Pobrano dane NMT')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane NMT/NMPT zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )

        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych NMT')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych NMT. Wystąpił błąd: " + str(self.exception))
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane NMT/NMPT nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych NMT')
        super().cancel()


