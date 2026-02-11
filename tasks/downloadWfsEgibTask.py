from qgis.PyQt.QtGui import QPixmap, QIcon

from qgis.core import QgsApplication, QgsTask, Qgis
from ..utils import MessageUtils, FileUtils
from ..wfs import WfsEgib


class DownloadWfsEgibTask(QgsTask):
    """QgsTask pobierania WFS EGiB"""

    def __init__(self, description, folder, teryt, wfs_url, iface, plugin_dir):

        super().__init__(description, QgsTask.CanCancel)
        self.name_error = ""
        self.wfsEgib = None
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.teryt = teryt
        self.wfs_url = wfs_url
        self.iface = iface
        self.plugin_dir = plugin_dir

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        MessageUtils.pushLogInfo('Rozpoczęto zadanie: "{}"'.format(self.description()))
        MessageUtils.pushLogInfo('Rozpoczęto ' + self.wfs_url)

        self.wfsEgib = WfsEgib()
        self.name_error = self.wfsEgib.egibWFS(self.teryt, self.wfs_url, self.folder)
        if self.name_error == 'brak':
            FileUtils.openFile(self.folder)
        if self.isCanceled():
            MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
            return False
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

        """W ramach powiatu mogą wystąpić prawidłowe warswy oraz nieprawidłowe - ta informacja zostanie przedstawiona 
        użytkownikowi w osobnym okienku"""
        
        if result and self.name_error == "brak" and self.exception is None:
            MessageUtils.pushLogInfo('Pobrano dane EGiB')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane EGiB dla powiatów zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych EGiB')

                title = "Informacje o warstwach EGiB"
                message = self.name_error
                MessageUtils.pushMessageBoxCritical(self.iface.mainWindow(), title, message)
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych EGiB. Wystąpił błąd: " + str(self.exception))


    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych EGiB')
        super().cancel()
