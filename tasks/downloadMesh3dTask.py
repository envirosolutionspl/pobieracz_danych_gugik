import os
import datetime
from qgis.core import QgsTask, QgsMessageLog, Qgis
from .. import service_api, utils


class DownloadMesh3dTask(QgsTask):
    def __init__(self, description, mesh_objs, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.mesh_objs = mesh_objs
        self.folder = folder
        self.exception = None
        self.iface = iface

    def run(self):
        QgsMessageLog.logMessage(f'Started task "{self.description()}"')
        total = len(self.mesh_objs)
        for obj in self.mesh_objs:
            if self.isCanceled():
                QgsMessageLog('isCanceled')
                return False
            QgsMessageLog.logMessage('start ' + obj.url)
            service_api.retreiveFile(url=obj.url, destFolder=self.folder, obj=self)
            self.setProgress(self.progress() + 100 / total)
        self.create_report()
        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                'Sukces',
                'Udało się! Dane siatkowego modelu 3D zostały pobrane.',
                level=Qgis.Success,
                duration=0
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage('exception')
                raise self.exception
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Dane modelu siatkowego 3D nie zostały pobrane.',
                level=Qgis.Warning,
                duration=10
            )

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def create_report(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(self.folder, f'pobieracz_mesh3d_{date}.txt'), 'w') as report_file:
            naglowki = [
                'Nazwa pliku',
                'Identyfikator modelu 3d',
                'Numer zgłoszenia',
                'Rok'
            ]
            report_file.write(','.join(naglowki)+'\n')
            for mesh_obj in self.mesh_objs:
                fileName = mesh_obj.url.split("/")[-1]
                report_file.write('%s,%s,%s,%s\n' % (
                    fileName,
                    mesh_obj.modul,
                    mesh_obj.numerZgloszeniaPracy,
                    mesh_obj.aktualnosc[0:4]
                ))
