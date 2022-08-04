import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)
from .. import service_api, utils


class DownloadZdjeciaLotniczeTask(QgsTask):
    """QgsTask pobierania intensywności"""

    def __init__(self, description, zdjeciaLotniczeList, zdjeciaLotniczeList_brak_url, folder):
        super().__init__(description, QgsTask.CanCancel)
        self.zdjeciaLotniczeList = zdjeciaLotniczeList
        self.zdjeciaLotniczeList_brak_url = zdjeciaLotniczeList_brak_url
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
        total = len(self.zdjeciaLotniczeList)

        for zdj in self.zdjeciaLotniczeList:
            QgsMessageLog.logMessage('start ' + zdj.url)

            # fileName = reflectance.url.split("/")[-1]
            # QgsMessageLog.logMessage('1 ' + fileName + ' ' + reflectance.url + ' ' + self.folder)
            service_api.retreiveFile(url=zdj.url, destFolder=self.folder)
            self.setProgress(self.progress() + 100 / total)
            print("url: ", zdj.url)

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
        for zdj in self.zdjeciaLotniczeList_brak_url:
            zdj.url = "brak zdjęcia"
        for zdj in self.zdjeciaLotniczeList:
            zdj.url = "jest dostępne zdjęcie"
        zdjeciaLotniczeList_all = self.zdjeciaLotniczeList + self.zdjeciaLotniczeList_brak_url
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(self.folder, 'pobieracz_zdjecia_lotnicze_%s.txt' % date), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'numer_szeregu',
                'numer_zdjęcia',
                'rok_wykonania',
                'data_nalotu',
                'charakterystyka_przestrzenna',
                'przestrzeń_barwna',
                'źrodło_danych',
                'numer_zgłoszenia',
                'karta_pracy',
                'dostępność danych'
            ]
            csvFile.write(','.join(naglowki)+'\n')
            for zdj in zdjeciaLotniczeList_all:
                fileName = zdj.url.split("/")[-1]
                csvFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    fileName,
                    zdj.nrSzeregu,
                    zdj.nrZdjecia,
                    zdj.rokWykonania,
                    zdj.dataNalotu,
                    zdj.charakterystykaPrzestrzenna,
                    zdj.przestrzenBarwna,
                    zdj.zrodloDanych,
                    zdj.nrZgloszenia,
                    zdj.kartaPracy,
                    zdj.url
                ))
