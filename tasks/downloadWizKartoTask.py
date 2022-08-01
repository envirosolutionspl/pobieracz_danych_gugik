import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)
from .. import service_api, utils


class DownloadwizKartoTask(QgsTask):
    """QgsTask pobierania LAS"""

    def __init__(self, description, wizKartoList, folder):
        super().__init__(description, QgsTask.CanCancel)
        self.wizKartoList = wizKartoList
        self.folder = folder
        self.total = 0
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
        total = len(self.wizKartoList)

        for wizKarto in self.wizKartoList:
            QgsMessageLog.logMessage('start ' + wizKarto.url)
            fileName = wizKarto.url.split("/")[-1]
            service_api.retreiveFile(url=wizKarto.url, destFolder=self.folder)
            self.setProgress(self.progress() + 100 / total)

        # utworz plik csv z podsumowaniem
        self.createCsvReport()

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
        csvFilename = 'pobieracz_wizualizacja_kartograficzna_BDOT10k_%s.txt' % date

        with open(os.path.join(self.folder, csvFilename), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'Data',
                'Skala',
                'Godło'
            ]
            csvFile.write(','.join(naglowki) + '\n')
            for wizKarto in self.wizKartoList:
                fileName = wizKarto.url.split("/")[-1]
                csvFile.write('%s,%s,%s,%s\n' % (
                    fileName,
                    wizKarto.data,
                    wizKarto.skala,
                    wizKarto.godlo
                ))
