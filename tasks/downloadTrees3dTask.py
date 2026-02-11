from qgis.core import QgsTask, Qgis

from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface

from ..constants import TREES3D_URL, TIMEOUT_MS
from ..utils import MessageUtils, NetworkUtils, ServiceAPI

class DownloadTrees3dTask(QgsTask):
    """QgsTask pobierania modeli 3D drzew"""

    def __init__(self, description, folder, teryt_powiat, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.result = None
        self.iface = iface
        self.service_api = ServiceAPI()
        self.network_utils = NetworkUtils()

    def run(self):
        trees_url = f'{TREES3D_URL}{self.teryt_powiat[:2]}/{self.teryt_powiat}.zip'
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        
        if self.isCanceled():
            return False

        success_check, result_check = self.network_utils.fetchContent(trees_url, timeout_ms=TIMEOUT_MS)

        if not success_check:
            MessageUtils.pushLogCritical(f'Błąd przy sprawdzaniu dostępności {trees_url}: {result_check}')
            self.exception = result_check 
            return False
            
        MessageUtils.pushLogInfo(f'Pobieram {trees_url}')
        
        self.result, self.exception = self.service_api.retreiveFile(url=trees_url, destFolder=self.folder, obj=self)
        
        if not self.result:
            MessageUtils.pushLogCritical(f'Błąd przy pobieraniu modeli 3D: {self.exception}')
            return False
            
        return not self.isCanceled()

    def finished(self, result):
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane z modelami 3D drzew')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane z modelami 3D drzew zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych z modelami 3D drzew')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych z modelami 3D drzew. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane z modelami 3D drzew nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych z modelami 3D drzew')
        super().cancel()


