import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from .. import service_api, utils


class DownloadKartotekiOsnowTask(QgsTask):
    """QgsTask pobierania archiwalnych kartotek osnów"""

    def __init__(self, description, kartotekiOsnowList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.kartotekiOsnowList = kartotekiOsnowList
        self.folder = folder
        self.total = 0
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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.kartotekiOsnowList)

        for kartotekaOsnow in self.kartotekiOsnowList:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage('start ' + kartotekaOsnow.url)
            fileName = kartotekaOsnow.url.split("/")[-1]
            service_api.retreiveFile(url=kartotekaOsnow.url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)

        # utworz plik csv z podsumowaniem
        self.createCsvReport()

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
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane archiwalnych kartotek osnów zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane archiwalnych kartotek osnów nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def createCsvReport(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        csvFilename = 'pobieracz_archiwalnych_katalogów_osnów_geodezyjnych_%s.txt' % date

        with open(os.path.join(self.folder, csvFilename), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'rodzaj_katalogu',
                'Godlo'
            ]
            csvFile.write(','.join(naglowki) + '\n')
            for kartotekaOsnow in self.kartotekiOsnowList:
                fileName = kartotekaOsnow.url.split("/")[-1]
                csvFile.write('%s,%s,%s\n' % (
                    fileName,
                    kartotekaOsnow.rodzaj_katalogu,
                    kartotekaOsnow.godlo
                ))
