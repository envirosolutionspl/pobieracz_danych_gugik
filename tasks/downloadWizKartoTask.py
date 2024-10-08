import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from .. import service_api, utils


class DownloadWizKartoTask(QgsTask):
    """QgsTask pobierania wizualizacji kartograficznej BDOT10k"""

    def __init__(self, description, wizKartoList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.wizKartoList = wizKartoList
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
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.wizKartoList)
        results = []
        for wizKarto in self.wizKartoList:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage(f'start {wizKarto.url}')
            res, self.exception = service_api.retreiveFile(url=wizKarto.url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(res)
        if not any(results):
            return False
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
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane wizualizacji kartograficznej BDOT10k zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                            "Dane wizualizacji kartograficznej BDOT10k nie zostały pobrane.")

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
