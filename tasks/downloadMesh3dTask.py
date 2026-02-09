import os
from qgis.core import QgsTask, Qgis
from .. import service_api
from ..utils import pushLogInfo, create_report


class DownloadMesh3dTask(QgsTask):
    def __init__(self, description, mesh_objs, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.mesh_objs = mesh_objs
        self.folder = folder
        self.exception = None
        self.iface = iface

    def run(self):
        pushLogInfo(f'Started task "{self.description()}"')
        total = len(self.mesh_objs)
        for obj in self.mesh_objs:
            obj_url = obj.get('url')
            if self.isCanceled():
                pushLogInfo('isCanceled')
                return False
            pushLogInfo(f'start {obj_url}')
            _, self.exception = service_api.retreiveFile(url=obj_url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        self.create_report()
        return True

    def finished(self, result):
        if result and self.exception:
            pushLogInfo('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane siatkowego modelu 3D zostały pobrane.',
                level=Qgis.Success,
                duration=10
            )
        else:
            if self.exception is None:
                pushLogInfo('finished with false')
            elif isinstance(self.exception, BaseException):
                pushLogInfo("exception")
            self.iface.messageBar().pushWarning(
                'Błąd',
                'Dane modelu siatkowego 3D nie zostały pobrane.'
            )

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()

    def create_report(self):
        headers_mapping = {
            'nazwa_pliku': 'url',
            'modul': 'modul',
            'aktualnosc': 'aktualnosc',
            'format': 'format',
            'blad_sredni_wysokosci': 'bladSredniWysokosci',
            'blad_sredni_polozenia': 'bladSredniPolozenia',
            'uklad_wspolrzednych_poziomych': 'ukladWspolrzednychPoziomych',
            'uklad_wspolrzednych_pionowych': 'ukladWspolrzednychPionowych',
            'modul_archiwizacji': 'modulArchiwizacji',
            'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
            'aktualnosc_rok': 'aktualnoscRok',
            'zrodlo_danych': 'zrDanych',
        }
        create_report(os.path.join(self.folder, 'pobieracz_mesh3d'), headers_mapping, self.mesh_objs)
