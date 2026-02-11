import os
from qgis.core import QgsTask, Qgis
from ..utils import MessageUtils, FileUtils, ServiceAPI
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
        MessageUtils.pushLogInfo(f'Rozpoczęto zadanie: "{self.description()}"')
        total = len(self.mesh_objs)
        for obj in self.mesh_objs:
            obj_url = obj.get('url')
            if self.isCanceled():
                MessageUtils.pushLogWarning(f'Przerwano zadanie: "{self.description()}"')
                return False
            MessageUtils.pushLogInfo(f'Rozpoczęto pobieranie danych z linku: {obj_url}')
            _, self.exception = self.service_api.retreiveFile(url=obj_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        FileUtils.createReport(os.path.join(self.folder, 'pobieracz_mesh3d'), HEADERS_MAPPING['MESH3D_HEADERS'], self.mesh_objs)
        return True

    def finished(self, result):
        if result and self.exception:
            MessageUtils.pushLogInfo('Pobrano dane siatkowego modelu 3D')
            MessageUtils.pushSuccess(self.iface, 'Udało się! Dane siatkowego modelu 3D zostały pobrane.')
        else:
            if self.exception is None:
                MessageUtils.pushLogWarning('Nie udało się pobrać danych siatkowego modelu 3D')
            elif isinstance(self.exception, BaseException):
                MessageUtils.pushLogWarning("Nie udało się pobrać danych siatkowego modelu 3D. Wystąpił błąd: " + str(self.exception))
            MessageUtils.pushWarning(self.iface, 'Dane modelu siatkowego 3D nie zostały pobrane.')

    def cancel(self):
        MessageUtils.pushLogWarning('Anulowano pobieranie danych siatkowego modelu 3D')
        super().cancel()
