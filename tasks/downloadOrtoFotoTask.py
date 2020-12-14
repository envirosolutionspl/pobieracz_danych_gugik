import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )
from .. import service_api, utils

class DownloadOrtofotoTask(QgsTask):
    """QgsTask pobierania ortofotomap"""

    def __init__(self, description, ortoList, folder):
        super().__init__(description, QgsTask.CanCancel)
        self.ortoList = ortoList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.ortoList)

        for orto in self.ortoList:
            QgsMessageLog.logMessage('start ' + orto.url)

            fileName = orto.url.split("/")[-1]
            # QgsMessageLog.logMessage('1 ' + fileName + ' ' + orto.url + ' ' + self.folder)
            service_api.retreiveFile(url=orto.url, destFolder=self.folder)
            self.setProgress(self.progress() + 100 / total)

        # utworz plik csv z podsumowaniem
        self.createCsvReport()

        utils.openFile(self.folder)
        if self.isCanceled():
            QgsMessageLog.logMessage('isCanceled')
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
        if result:
            QgsMessageLog.logMessage('sukces')
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def createCsvReport(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(self.folder, 'pobieracz_ortofoto_%s.txt' % date), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'godlo',
                'aktualnosc',
                'wielkosc_piksela',
                'uklad_wspolrzednych',
                'caly_arkusz_wypelniony_trescia',
                'modul_archiwizacji',
                'zrodlo_danych',
                'kolor',
                'numer_zgloszenia_pracy',
                'aktualnosc_rok'
            ]
            csvFile.write(','.join(naglowki)+'\n')
            for orto in self.ortoList:
                fileName = orto.url.split("/")[-1]
                csvFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    fileName,
                    orto.godlo,
                    orto.aktualnosc,
                    orto.wielkoscPiksela,
                    orto.ukladWspolrzednych,
                    orto.calyArkuszWyeplnionyTrescia,
                    orto.modulArchiwizacji,
                    orto.zrodloDanych,
                    orto.kolor,
                    orto.numerZgloszeniaPracy,
                    orto.aktualnoscRok
                ))
