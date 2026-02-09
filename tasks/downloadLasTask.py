import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, Qgis
    )
from .. import service_api
from ..utils import pushLogInfo




class DownloadLasTask(QgsTask):
    """QgsTask pobierania LAZ"""

    def __init__(self, description, lasList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.lasList = lasList
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
        pushLogInfo(f'Started task "{self.description()}"')
        total = len(self.lasList)
        results = []
        for las in self.lasList:
            las_url = las.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {las_url}')
            success, message = service_api.retreiveFile(url=las_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
            results.append(success)
            if not success:
                self.exception = message
                
        if not any(results):
            return False
            
        if all(results):
            self.exception = True
            
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
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane LAZ zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            error_msg = str(self.exception) if self.exception and self.exception is not True else "Błąd nieznany"
            pushLogInfo(f"Błąd LAZ: {error_msg}")
            self.iface.messageBar().pushWarning(
                'Błąd',
                f'Dane LAZ nie zostały pobrane: {error_msg}'
            )

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()

    def create_report(self):
        headers_mapping = {
            'nazwa_pliku': 'url',
            'godlo': 'godlo',
            'format': 'format',
            'aktualnosc': 'aktulnosc',
            'dokladnosc_pionowa': 'bladSredniWysokosci',
            'uklad_wspolrzednych_plaskich': 'ukladWspolrzednych',
            'uklad_wspolrzednych_wysokosciowych': 'ukladWysokosci',
            'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
            'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
            'aktualnosc_rok': 'aktualnoscRok'
        }
        utils.create_report(
            os.path.join(self.folder, 'pobieracz_las'),
            headers_mapping,
            self.lasList
        )

