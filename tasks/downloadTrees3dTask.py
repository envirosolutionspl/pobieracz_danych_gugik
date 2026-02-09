from qgis.core import QgsTask, Qgis
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface

from ..constants import TREES3D_URL, TIMEOUT_MS
from ..service_api import ServiceAPI
from ..network_utils import NetworkUtils
from ..utils import pushLogInfo

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
            pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
            
            if self.isCanceled():
                return False

            success_check, result_check = self.network_utils.fetchContent(trees_url, timeout_ms=TIMEOUT_MS)

            if not success_check:
                pushLogInfo(f'Błąd przy sprawdzaniu dostępności {trees_url}: {result_check}')
                self.exception = result_check 
                return False
                
            pushLogInfo(f'pobieram {trees_url}')
            
            self.result, self.exception = self.service_api.retreiveFile(url=trees_url, destFolder=self.folder, obj=self)
            
            if not self.result:
                pushLogInfo(f'Błąd przy pobieraniu modeli 3D: {self.exception}')
                return False
                
            return not self.isCanceled()

    def finished(self, result):
        if result and self.exception:
            pushLogInfo('Pobrano dane z modelami 3D drzew')
            self.iface.messageBar().pushMessage("Sukces",
                                                "Udało się! Dane z modelami 3D drzew zostały pobrane.",
                                                level=Qgis.Success,
                                                duration=10)
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych z modelami 3D drzew')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych z modelami 3D drzew. Wystąpił błąd: " + str(self.exception))
                raise self.exception
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Dane z modelami 3D drzew nie zostały pobrane.',
                level=Qgis.Warning,
                duration=10
            )

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych z modelami 3D drzew')
        super().cancel()


