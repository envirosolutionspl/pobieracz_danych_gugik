from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)

from ..constants import OSNOWA_WMS_URL
from .. import service_api, utils
from ..wfs.httpsAdapter import get_legacy_session


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
            with get_legacy_session().get(url, verify=False) as resp:
                if str(resp.status_code) != '200':
                    return False
                if self.isCanceled():
                    QgsMessageLog.logMessage('isCanceled')
                    return False
                QgsMessageLog.logMessage(f'pobieram {url}')
                res, exp = service_api.retreiveFile(url=url, destFolder=self.folder, obj=self)
                if not res:
                    self.exception = exp
                    return False
        return True

    def finished(self, result):
        if result and not self.exception:
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
