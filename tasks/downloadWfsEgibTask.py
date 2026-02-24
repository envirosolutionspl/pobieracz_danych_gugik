from qgis.PyQt.QtGui import QPixmap, QIcon

from qgis.core import QgsApplication, QgsTask, Qgis
from ..utils import MessageUtils, FileUtils
from ..wfs import WfsEgib
from ..constants import STATUS_SUCCESS, STATUS_CANCELED


class DownloadWfsEgibTask(QgsTask):
    """QgsTask pobierania WFS EGiB"""

    def __init__(self, description, folder, teryt, wfs_url, iface, plugin_dir):
        super().__init__(description, QgsTask.CanCancel)
        self.name_error = ""
        self.wfsEgib = None
        self.folder = folder
        self.teryt = teryt
        self.wfs_url = wfs_url
        self.iface = iface
        self.plugin_dir = plugin_dir

    def run(self):
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')

        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.egibWFS(self.teryt, self.wfs_url, self.folder, obj=self)
        
        if self.isCanceled() or self.name_error == STATUS_CANCELED:
            return False

        if self.name_error == STATUS_SUCCESS:
            FileUtils.openFile(self.folder)
            return True
            
        return False

    def finished(self, result):
        # anulowano
        if self.isCanceled() or self.name_error == STATUS_CANCELED:
            MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
            MessageUtils.pushWarning(self.iface, 'Pobieranie danych EGiB zostało przerwane.')
            return

        # sukces
        if result:
            MessageUtils.pushLogInfo('Pobrano dane EGiB')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane EGiB dla powiatów zostały pobrane.')
            return

        # błędy warstw
        MessageUtils.pushLogWarning('Nie udało się pobrać wszystkich danych EGiB')
        MessageUtils.pushWarning(self.iface, 'Niektóre warstwy EGiB nie zostały pobrane. Szczegóły w raporcie błędu.')
        
        if self.name_error and self.name_error != STATUS_SUCCESS:
            title = "Informacje o warstwach EGiB"
            MessageUtils.pushMessageBoxCritical(self.iface.mainWindow(), title, self.name_error)

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych EGiB')
        super().cancel()
