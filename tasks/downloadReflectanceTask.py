import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils

class DownloadReflectanceTask(QgsTask):
    """QgsTask pobierania intensywności"""

    def __init__(self, description, reflectanceList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.reflectanceList = reflectanceList
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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.reflectanceList)

        for reflectance in self.reflectanceList:
            QgsMessageLog.logMessage('start ' + reflectance.url)

            # fileName = reflectance.url.split("/")[-1]
            # QgsMessageLog.logMessage('1 ' + fileName + ' ' + reflectance.url + ' ' + self.folder)
            service_api.retreiveFile(url=reflectance.url, destFolder=self.folder)
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
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane obrazów intensywności zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane obrazów intensywności nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def createCsvReport(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(self.folder, 'pobieracz_intensywnosc_%s.txt' % date), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'godlo',
                'aktualnosc',
                'wielkosc_piksela',
                'uklad_wspolrzednych',
                'modul_archiwizacji',
                'zrodlo_danych',
                'metoda_zapisu',
                'zakres intensywnosci',
                'numer_zgloszenia_pracy',
                'aktualnosc_rok'
            ]
            csvFile.write(','.join(naglowki)+'\n')
            for reflectance in self.reflectanceList:
                fileName = reflectance.url.split("/")[-1]
                csvFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    fileName,
                    reflectance.godlo,
                    reflectance.aktualnosc,
                    reflectance.wielkoscPiksela,
                    reflectance.ukladWspolrzednych,
                    reflectance.modulArchiwizacji,
                    reflectance.zrodloDanych,
                    reflectance.metodaZapisu,
                    reflectance.zakresIntensywnosci,
                    reflectance.numerZgloszeniaPracy,
                    reflectance.aktualnoscRok
                ))
