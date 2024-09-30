import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils


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

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.nmtList)
        for nmt in self.nmtList:
            nmt_url = nmt.get('url')
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'start {nmt_url}')
            service_api.retreiveFile(url=nmt_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        self.create_report()
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
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane NMT/NMPT zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )

        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane NMT/NMPT nie zostały pobrane.'
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
            'zrodlo_danych': 'zrDanych'
        }
        utils.create_report(
            os.path.join(self.folder, 'pobieracz_nmpt' if self.isNmpt else 'pobieracz_nmt'),
            headers_mapping,
            self.nmtList
        )
