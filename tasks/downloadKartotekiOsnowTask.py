import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, Qgis
)
from ..utils import MessageUtils, ServiceAPI, FileUtils
from ..constants import HEADERS_MAPPING


class DownloadKartotekiOsnowTask(QgsTask):
    """QgsTask pobierania archiwalnych kartotek osnów"""

    def __init__(self, description, kartotekiOsnowList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.kartotekiOsnowList = kartotekiOsnowList
        self.folder = folder
        self.total = 0
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
        total = len(self.kartotekiOsnowList)
        results = []
        for kartotekaOsnow in self.kartotekiOsnowList:
            obj_url = kartotekaOsnow.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {obj_url}')
            res, self.exception = self.service_api.retreiveFile(url=obj_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False

        FileUtils.createReport(
            os.path.join(self.folder, 'pobieracz_archiwalnych_katalogów_osnów_geodezyjnych'),
            HEADERS_MAPPING['CONTROL_POINT_RECORDS_HEADERS'],
            self.kartotekiOsnowList
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
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane archiwalnych kartotek osnów')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane archiwalnych kartotek osnów zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych archiwalnych kartotek osnów')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych archiwalnych kartotek osnów. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Nie udało się pobrać danych archiwalnych kartotek osnów.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych archiwalnych kartotek osnów')
        super().cancel()
