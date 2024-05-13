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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.nmptList)

        for nmpt in self.nmptList:
            if self.isCanceled():
                QgsMessageLog.logMessage('isCanceled')
                return False
            QgsMessageLog.logMessage('start ' + nmpt.url)
            fileName = nmpt.url.split("/")[-1]
            service_api.retreiveFile(url=nmpt.url, destFolder=self.folder, obj=self)
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
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane NMPT zostały pobrane.",
                                                level=Qgis.Success, duration=10)

        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushMessage("Błąd",
                                                "Dane NMPT nie zostały pobrane.",
                                                level=Qgis.Warning, duration=10)

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def createCsvReport(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        csvFilename = 'pobieracz_nmpt_%s.txt' % date


        with open(os.path.join(self.folder, csvFilename), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'format',
                'godlo',
                'aktualnosc',
                'dokladnosc_pozioma',
                'dokladnosc_pionowa',
                'uklad_wspolrzednych_plaskich',
                'uklad_wspolrzednych_wysokosciowych',
                'caly_arkusz_wypelniony_trescia',
                'numer_zgloszenia_pracy',
                'aktualnosc_rok',
                'data_dodania_do_PZGIK'
            ]

            csvFile.write(','.join(naglowki)+'\n')
            for nmpt in self.nmptList:
                fileName = nmpt.url.split("/")[-1]

                csvFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    fileName,
                    nmpt.godlo,
                    nmpt.format,
                    nmpt.aktualnosc,
                    nmpt.charakterystykaPrzestrzenna,
                    nmpt.bladSredniWysokosci,
                    nmpt.ukladWspolrzednych,
                    nmpt.ukladWysokosci,
                    nmpt.calyArkuszWyeplnionyTrescia,
                    nmpt.numerZgloszeniaPracy,
                    nmpt.aktualnoscRok,
                    nmpt.dt_pzgik
                ))
