from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils

url_prefixes = {
    'GML': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/',
    'SHP': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/',
    'GML 2011': 'https://opendata.geoportal.gov.pl/bdot10k/',
    'GPKG': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/GPKG/',
}


class DownloadBdotTask(QgsTask):
    """QgsTask pobierania BDOT10k"""
    def __init__(self, description, folder, level, format_danych, teryt, iface):
        """
        level:
        0 - cały kraj
        1 - województwo
        2 - powiat
        """
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        # self.total = 0
        # self.iterations = 0
        self.exception = None
        self.iface = iface
        self._construct_url(level, teryt, format_danych)

    def _construct_url(self, level: int, teryt: str, data_format: str) -> None:
        prefix = url_prefixes.get(data_format)
        data_format = data_format.strip().split()[0]
        if level == 0:
            self.url = f"{prefix}Polska_{data_format}.zip"
        elif level == 1:
            self.url = f"{prefix}{teryt}/{teryt}_{data_format}.zip"
        elif level == 2:
            self.url = f"{prefix}{teryt[:2]}/{teryt}_{data_format}.zip"

    def run(self):

        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)


        QgsMessageLog.logMessage('pobieram ' + self.url)
        # fileName = self.url.split("/")[-1]
        pass
        service_api.retreiveFile(url=self.url, destFolder=self.folder, obj=self)
        # self.setProgress(self.progress() + 100 / total)

        utils.openFile(self.folder)
        if self.isCanceled():
            return False
        return True

    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane BDOT10k zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
