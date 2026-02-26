import os, datetime
from qgis.core import QgsApplication, QgsTask, Qgis
from ..utils import MessageUtils, FileUtils, ServiceAPI
from ..constants import HEADERS_MAPPING


class DownloadNmptTask(QgsTask):
    """QgsTask pobierania NMPT"""

    def __init__(self, description, nmptList, folder, isNmpt, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.nmptList = nmptList
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
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.nmptList)
        results = []
        for nmpt in self.nmptList:
            nmpt_url = nmpt.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {nmpt_url}')
            res, self.exception = self.service_api.retreiveFile(url=nmpt_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False

        FileUtils.createReport(
            os.path.join(self.folder, 'pobieracz_nmpt'),
            HEADERS_MAPPING['NMT_HEADERS'],
            self.nmptList
        )
        FileUtils.openFile(self.folder)
        if self.isCanceled():
            return False
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
            MessageUtils.pushLogInfo('Pobrano dane NMPT')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane NMPT zostały pobrane.')

        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych NMPT')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych NMPT. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane NMPT nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych NMPT')
        super().cancel()
