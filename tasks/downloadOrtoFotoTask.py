import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils

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

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.ortoList)
        results = []
        for orto in self.ortoList:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            orto_url = orto.get('url')
            if not orto_url:
                continue
            QgsMessageLog.logMessage(f'start {orto_url}')
            res, self.exception = service_api.retreiveFile(url=orto_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
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
        if result and self.exception:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane z ortofotomapy zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane z ortofotomapy nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def create_report(self):
        headers_mapping = {
            'nazwa_pliku': 'url',
            'godlo': 'godlo',
            'aktualnosc': 'aktualnosc',
            'wielkosc_piksela': 'wielkoscPiksela',
            'uklad_wspolrzednych': 'ukladWspolrzednych',
            'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
            'modul_archiwizacji': 'modulArchiwizacji',
            'zrodlo_danych': 'zrodloDanych',
            'kolor': 'kolor',
            'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
            'aktualnosc_rok': 'aktualnoscRok'
        }
        utils.create_report(os.path.join(self.folder, 'pobieracz_ortofoto'), headers_mapping, self.ortoList)
