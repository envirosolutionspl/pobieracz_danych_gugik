import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, Qgis
    )
from ..utils import FileUtils, MessageUtils, ServiceAPI
from ..constants import HEADERS_MAPPING


class DownloadAerotriangulacjaTask(QgsTask):
    """QgsTask pobierania aerotriangulacji"""

    def __init__(self, description, aerotriangulacjaList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.aerotriangulacjaList = aerotriangulacjaList
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
        total = len(self.aerotriangulacjaList)
        results = []
        for aero in self.aerotriangulacjaList:
            aero_url = aero.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {aero_url}')
            res, self.exception = self.service_api.retreiveFile(url=aero_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
        self._createReport()
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
            MessageUtils.pushLogInfo('Pobrano dane o aerotriangulacji')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane o aerotriangulacji zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych o aerotriangulacji')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych o aerotriangulacji. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane o aerotriangulacji nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych o aerotriangulacji')
        super().cancel()

    def _createReport(self):
        for obj in self.aerotriangulacjaList:
            obj['rok'] = obj.get('zgloszenie').split('.')[3]
        FileUtils.createReport(
            os.path.join(self.folder, 'pobieracz_aerotriangulacja'),
            HEADERS_MAPPING['AEROTRIANGULATION_HEADERS'],
            self.aerotriangulacjaList
        )
