import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from .. import service_api, utils


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

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.zdjeciaLotniczeList)
        for zdj in self.zdjeciaLotniczeList:
            zdj_url = zdj.get('url')
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'start {zdj_url}')
            service_api.retreiveFile(url=zdj_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        self.create_report()
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
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane zdjęć lotniczych zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane zdjęć lotniczych nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def create_report(self):
        zdjeciaLotniczeList_all = self.zdjeciaLotniczeList + self.zdjeciaLotniczeList_brak_url
        headers_mapping = {
            'nazwa_pliku': 'url',
            'numer_szeregu': 'nrSzeregu',
            'numer_zdjęcia': 'nrZdjecia',
            'rok_wykonania': 'rokWykonania',
            'data_nalotu': 'dataNalotu',
            'charakterystyka_przestrzenna': 'charakterystykaPrzestrzenna',
            'kolor': 'kolor',
            'źrodło_danych': 'zrodloDanych',
            'numer_zgłoszenia': 'nrZgloszenia',
            'karta_pracy': 'kartaPracy',
        }
        obj_list = [{**obj, 'url': obj.get('url', '').split('/')[-1]} for obj in zdjeciaLotniczeList_all]
        utils.create_report(os.path.join(self.folder, 'pobieracz_zdjecia_lotnicze'), headers_mapping, obj_list)
