from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)

from ..constants import OSNOWA_WMS_URL, TIMEOUT_MS
from .. import service_api, utils
from ..network_utils import NetworkUtils


class DownloadOsnowaTask(QgsTask):
    def __init__(self, description, folder, teryt_powiat, typ, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.typ = typ
        self.iface = iface

    def run(self):
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        for typ in self.typ:
            url = f"{OSNOWA_WMS_URL}teryt={self.teryt_powiat}&typ={typ}"
            
            if self.isCanceled():
                return False
                
            try:
                NetworkUtils.fetch_content(url, timeout_ms=TIMEOUT_MS)
                QgsMessageLog.logMessage(f'pobieram {url}')
                res, exp = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
                self.exception = exp
                if not res:
                    return False
            except Exception as e:
                QgsMessageLog.logMessage(f'Błąd przy sprawdzaniu/pobieraniu {url}: {str(e)}')
                return False
        return True

    def finished(self, result):
        if result and self.exception:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane podstawowej osnowy geodezyjnej zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            elif isinstance(self.exception, BaseException):
                QgsMessageLog.logMessage("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane podstawowej osnowy geodezyjnej nie zostały pobrane.'
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
