import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils


class DownloadAerotriangulacjaTask(QgsTask):
    """QgsTask pobierania areotriangulacji"""

    def __init__(self, description, aerotriangulacjaList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.aerotriangulacjaList = aerotriangulacjaList
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
        total = len(self.aerotriangulacjaList)
        for areo in self.aerotriangulacjaList:
            areo_url = areo.get('url')
            if self.isCanceled():
                QgsMessageLog('isCanceled')
                return False
            QgsMessageLog.logMessage(f'start {areo_url}')
            service_api.retreiveFile(url=areo_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
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
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane o areotriangulacji zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage('exception')
                raise self.exception
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane o areotriangulacji nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def create_report(self):
        headers_mapping = {
            'Nazwa pliku': 'url',
            'Identyfikator aerotriangulacji': 'id',
            'Numer zgłoszenia': 'zgloszenie',
            'Rok': 'rok'
        }
        for obj in self.aerotriangulacjaList:
            obj['rok'] = obj.get('zgloszenie').split('.')[3]
        utils.create_report(
            os.path.join(self.folder, 'pobieracz_aerotriangulacja'),
            headers_mapping,
            self.aerotriangulacjaList
        )
