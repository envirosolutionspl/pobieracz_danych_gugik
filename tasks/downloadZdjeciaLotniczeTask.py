import os
from qgis.core import QgsTask
from ..utils import MessageUtils, FileUtils, ServiceAPI
from ..constants import HEADERS_MAPPING


class DownloadZdjeciaLotniczeTask(QgsTask):
    """QgsTask pobierania zdjęć lotniczych"""

    def __init__(self, description, zdjeciaLotniczeList, zdjeciaLotniczeList_brak_url, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.zdjeciaLotniczeList = zdjeciaLotniczeList
        self.zdjeciaLotniczeList_brak_url = zdjeciaLotniczeList_brak_url
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
        total = len(self.zdjeciaLotniczeList)
        results = []
        for zdj in self.zdjeciaLotniczeList:
            zdj_url = zdj.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {zdj_url}')
            res, self.exception = self.service_api.retreiveFile(url=zdj_url, destFolder=self.folder, obj=self)
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
            MessageUtils.pushLogInfo('Pobrano dane zdjęć lotniczych')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane zdjęć lotniczych zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych zdjęć lotniczych')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych zdjęć lotniczych. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane zdjęć lotniczych nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych zdjęć lotniczych')
        super().cancel()

    def _createReport(self):
        zdjeciaLotniczeList_all = self.zdjeciaLotniczeList + self.zdjeciaLotniczeList_brak_url
        obj_list = [{**obj, 'url': obj.get('url', '').split('/')[-1]} for obj in zdjeciaLotniczeList_all]
        FileUtils.createReport(os.path.join(self.folder, 'pobieracz_zdjecia_lotnicze'), HEADERS_MAPPING['AERIAL_PHOTOS'], obj_list)
