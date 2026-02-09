from qgis.core import QgsTask, Qgis

from ..constants import OSNOWA_WMS_URL, TIMEOUT_MS
from .. import service_api
from ..network_utils import NetworkUtils
from ..utils import pushLogInfo


class DownloadOsnowaTask(QgsTask):
    def __init__(self, description, folder, teryt_powiat, typ, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.typ = typ
        self.iface = iface

    def run(self):
            pushLogInfo(f'Started task "{self.description()}"')
            
            for typ in self.typ:
                url = f"{OSNOWA_WMS_URL}teryt={self.teryt_powiat}&typ={typ}"
                
                if self.isCanceled():
                    return False
                success_check, result_check = NetworkUtils.fetchContent(url, timeout_ms=TIMEOUT_MS)

                if not success_check:
                    pushLogInfo(f'Błąd przy sprawdzaniu dostępności {url}: {result_check}')
                    return False
                    
                pushLogInfo(f'pobieram {url}')
                
                res, self.exception = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
                
                if not res:
                    pushLogInfo(f'Błąd przy pobieraniu pliku {url}: {self.exception}')
                    return False
            return True

    def finished(self, result):
        if result and self.exception:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane podstawowej osnowy geodezyjnej zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                pushLogInfo('finished with false')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane podstawowej osnowy geodezyjnej nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
