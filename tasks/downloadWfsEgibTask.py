
from qgis.core import QgsApplication, QgsTask
from ..utils import MessageUtils, FileUtils
from ..wfs import WfsEgib
from ..constants import STATUS_SUCCESS, STATUS_CANCELED


class DownloadWfsEgibTask(QgsTask):
    """QgsTask pobierania pliku GetCapabilities WFS EGiB"""

    def __init__(self, description, folder, teryt, wfs_url, iface, plugin_dir):
        super().__init__(description, QgsTask.Flag.CanCancel)
        self.name_error = ""
        self.wfsEgib = None
        self.folder = folder
        self.teryt = teryt
        self.wfs_url = wfs_url
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.path = None
        self.caps_url = None

    def run(self):
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')

        self.caps_url = WfsEgib.capabilitiesUrl(self.wfs_url)
        self.path = WfsEgib.createFolder(self.teryt, self.folder)

        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.saveXml(self.path, self.caps_url, self.teryt, obj=self)
        self.wfsEgib = None

        if self.isCanceled():
            return False

        return self.name_error == STATUS_SUCCESS

    def finished(self, result):
        # anulowano
        if self.isCanceled():
            MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
            MessageUtils.pushWarning(self.iface, 'Pobieranie danych EGiB zostało przerwane.')
            return

        # parsowanie XML w głównym wątku - lxml w wątku zadania powodował crash QGIS
        if result:
            self.name_error, name_layers, prefix = WfsEgib.workOnXml(self.path, self.caps_url, self.teryt)

        # sukces - pobieranie warstw w osobnym zadaniu
        if result and self.name_error == STATUS_SUCCESS:
            task = DownloadWfsEgibLayersTask(
                description=self.description(),
                folder=self.folder,
                path=self.path,
                caps_url=self.caps_url,
                teryt=self.teryt,
                name_layers=name_layers,
                prefix=prefix,
                iface=self.iface
            )
            QgsApplication.taskManager().addTask(task)
            return

        # błędy
        MessageUtils.pushLogWarning('Nie udało się pobrać wszystkich danych EGiB')
        MessageUtils.pushWarning(self.iface, 'Niektóre warstwy EGiB nie zostały pobrane. Szczegóły w raporcie błędu.')

        if self.name_error and self.name_error != STATUS_SUCCESS:
            title = "Informacje o warstwach EGiB"
            MessageUtils.pushMessageBoxCritical(self.iface.mainWindow(), title, self.name_error)

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych EGiB')
        super().cancel()


class DownloadWfsEgibLayersTask(QgsTask):
    """QgsTask pobierania warstw WFS EGiB"""

    def __init__(self, description, folder, path, caps_url, teryt, name_layers, prefix, iface):
        super().__init__(description, QgsTask.Flag.CanCancel)
        self.name_error = ""
        self.wfsEgib = None
        self.folder = folder
        self.path = path
        self.caps_url = caps_url
        self.teryt = teryt
        self.name_layers = name_layers
        self.prefix = prefix
        self.iface = iface

    def run(self):
        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.saveGML(
            self.path, self.caps_url, self.teryt, self.name_layers, self.prefix, obj=self
        )
        self.wfsEgib = None

        if self.isCanceled() or self.name_error == STATUS_CANCELED:
            return False

        return self.name_error == STATUS_SUCCESS

    def finished(self, result):
        # anulowano
        if self.isCanceled() or self.name_error == STATUS_CANCELED:
            MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
            MessageUtils.pushWarning(self.iface, 'Pobieranie danych EGiB zostało przerwane.')
            return

        # sukces
        if result:
            FileUtils.openFile(self.folder)
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
