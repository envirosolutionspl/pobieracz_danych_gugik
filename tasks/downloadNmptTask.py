import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils


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

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.nmptList)
        results = []
        for nmpt in self.nmptList:
            nmpt_url = nmpt.get('url')
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'start {nmpt_url}')
            res, self.exception = service_api.retreiveFile(url=nmpt_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
        self.create_report()
        utils.openFile(self.folder)
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
        if result and not self.exception:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane NMPT zostały pobrane.',
                level=Qgis.Success,
                duration=10
            )

        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Dane NMPT nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def create_report(self):
        headers_mapping = {
            'nazwa_pliku': 'url',
            'format': 'format',
            'godlo': 'godlo',
            'aktualnosc': 'aktualnosc',
            'dokladnosc_pozioma': 'charakterystykaPrzestrzenna',
            'dokladnosc_pionowa': 'bladSredniWysokosci',
            'uklad_wspolrzednych_plaskich': 'ukladWspolrzednych',
            'uklad_wspolrzednych_wysokosciowych': 'ukladWysokosci',
            'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
            'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
            'aktualnosc_rok': 'aktualnoscRok',
            'zrodlo_danych': 'zrDanych',
            'data_dodania_do_PZGIK': 'dt_pzgik'
        }
        utils.create_report(
            os.path.join(self.folder, 'pobieracz_nmpt'),
            headers_mapping,
            self.nmptList
        )
