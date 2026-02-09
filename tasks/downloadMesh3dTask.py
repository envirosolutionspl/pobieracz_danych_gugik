import os
from qgis.core import QgsTask, Qgis
from ..service_api import ServiceAPI
from ..utils import pushLogInfo, create_report
from ..constants import HEADERS_MAPPING


class DownloadMesh3dTask(QgsTask):
    def __init__(self, description, mesh_objs, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.mesh_objs = mesh_objs
        self.folder = folder
        self.exception = None
        self.iface = iface
        self.service_api = ServiceAPI()

    def run(self):
        pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.mesh_objs)
        for obj in self.mesh_objs:
            obj_url = obj.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {obj_url}')
            _, self.exception = self.service_api.retreiveFile(url=obj_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        create_report(os.path.join(self.folder, 'pobieracz_mesh3d'), HEADERS_MAPPING['MESH3D_HEADERS'], self.mesh_objs)
        return True

    def finished(self, result):
        if result and self.exception:
            pushLogInfo('Pobrano dane siatkowego modelu 3D')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane siatkowego modelu 3D zostały pobrane.',
                level=Qgis.Success,
                duration=10
            )
        else:
            if self.exception is None:
                pushLogInfo('Nie udało się pobrać danych siatkowego modelu 3D')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("Nie udało się pobrać danych siatkowego modelu 3D. Wystąpił błąd: " + str(self.exception))
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane modelu siatkowego 3D nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('Anulowano pobieranie danych siatkowego modelu 3D')
        super().cancel()
