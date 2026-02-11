import os, datetime
from qgis.core import QgsTask
from ..utils import MessageUtils, ServiceAPI


class DownloadWizKartoTask(QgsTask):
    """QgsTask pobierania wizualizacji kartograficznej BDOT10k"""

    def __init__(self, description, wizKartoList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.wizKartoList = wizKartoList
        self.folder = folder
        self.total = 0
        self.exception = None
        self.iface = iface
        self.service_api = ServiceAPI()

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.wizKartoList)
        results = []
        for wizKarto in self.wizKartoList:
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {wizKarto.url}')
            res, self.exception = self.service_api.retreiveFile(url=wizKarto.url, destFolder=self.folder, obj=self)
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
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane wizualizacji kartograficznej BDOT10k')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane wizualizacji kartograficznej BDOT10k zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych wizualizacji kartograficznej BDOT10k')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych wizualizacji kartograficznej BDOT10k. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane wizualizacji kartograficznej BDOT10k nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych wizualizacji kartograficznej BDOT10k')
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
