# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QApplication, QMessageBox
from qgis.gui import *
from qgis.core import *
from .tasks import DownloadOrtofotoTask, DownloadNmtTask, DownloadLasTask, DownloadReflectanceTask
import asyncio, processing

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .dialogs import PobieraczDanychDockWidget
import os.path

from . import utils, ortofoto_api, nmt_api, nmpt_api, service_api, las_api, reflectance_api

"""Wersja wtyczki"""
plugin_version = '0.5.1'
plugin_name = 'Pobieracz Danych GUGiK'


class PobieraczDanychGugik:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.settings = QgsSettings()

        # Declare instance attributes
        self.actions = []
        self.menu = u'&EnviroSolutions'
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, 'EnviroSolutions')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'EnviroSolutions')
            self.toolbar.setObjectName(u'EnviroSolutions')

        self.pluginIsActive = False
        self.dockwidget = None

        self.canvas = self.iface.mapCanvas()
        # out click tool will emit a QgsPoint on every click
        self.ortoClickTool = QgsMapToolEmitPoint(self.canvas)
        self.ortoClickTool.canvasClicked.connect(self.canvasOrto_clicked)
        self.nmtClickTool = QgsMapToolEmitPoint(self.canvas)
        self.nmtClickTool.canvasClicked.connect(self.canvasNmt_clicked)
        self.lasClickTool = QgsMapToolEmitPoint(self.canvas)
        self.lasClickTool.canvasClicked.connect(self.canvasLas_clicked)
        self.reflectanceClickTool = QgsMapToolEmitPoint(self.canvas)
        self.reflectanceClickTool.canvasClicked.connect(self.canvasReflectance_clicked)
        # --------------------------------------------------------------------------

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/pobieracz_danych_gugik/img/icon_pw2.png'
        self.add_action(
            icon_path,
            text=u'Pobieracz Danych GUGiK',
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginMenu(
                u'&EnviroSolutions',
                action)
            # self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PobieraczDanychDockWidget()
            # Eventy
            self.dockwidget.orto_capture_btn.clicked.connect(self.orto_capture_btn_clicked)
            self.dockwidget.orto_fromLayer_btn.clicked.connect(self.orto_fromLayer_btn_clicked)

            self.dockwidget.nmt_capture_btn.clicked.connect(self.nmt_capture_btn_clicked)
            self.dockwidget.nmt_fromLayer_btn.clicked.connect(self.nmt_fromLayer_btn_clicked)

            self.dockwidget.las_capture_btn.clicked.connect(self.las_capture_btn_clicked)
            self.dockwidget.las_fromLayer_btn.clicked.connect(self.las_fromLayer_btn_clicked)

            self.dockwidget.reflectance_capture_btn.clicked.connect(self.reflectance_capture_btn_clicked)
            self.dockwidget.reflectance_fromLayer_btn.clicked.connect(self.reflectance_fromLayer_btn_clicked)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            self.dockwidget.folder_fileWidget.setFilePath(
                self.settings.value("pobieracz_danych_gugik/settings/defaultPath", ""))
            self.dockwidget.folder_fileWidget.fileChanged.connect(
                lambda: self.settings.setValue("pobieracz_danych_gugik/settings/defaultPath",
                                               self.dockwidget.folder_fileWidget.filePath()))

            # informacje o wersji
            self.dockwidget.lbl_pluginVersion.setText('%s %s' % (plugin_name, plugin_version))

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    # region ORTOFOTOMAPA
    def orto_capture_btn_clicked(self):
        """Kliknięcie plawisza pobierania ortofotomapy przez wybór z mapy"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if path:  # pobrano ściezkę
            self.canvas.setMapTool(self.ortoClickTool)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano wskazano miejsca zapisu plików')

    def orto_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania ortofotomapy przez wybórwarstwą wektorową"""
        bledy = 0
        layer = self.dockwidget.orto_mapLayerComboBox.currentLayer()
        # zamiana układu na 92
        if layer:
            points = self.pointsFromVectorLayer(layer)

            # zablokowanie klawisza pobierania
            self.dockwidget.orto_fromLayer_btn.setEnabled(False)

            ortoList = []
            for point in points:
                subList = ortofoto_api.getOrtoListbyPoint1992(point=point)
                if subList:
                    ortoList.extend(subList)
                else:
                    bledy += 1

            self.filterOrtoListAndRunTask(ortoList)
            print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.orto_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadOrtoForSinglePoint(self, point):
        """Pobiera ortofotomapę dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        ortoList = ortofoto_api.getOrtoListbyPoint1992(point=point1992)
        self.filterOrtoListAndRunTask(ortoList)

    def filterOrtoListAndRunTask(self, ortoList):
        """Filtruje listę dostępnych plików ortofotomap i uruchamia wątek QgsTask"""
        print("przed 'set'", len(ortoList))

        # usuwanie duplikatów
        ortoList = list(set(ortoList))
        print("po 'set'", len(ortoList))
        # filtrowanie
        ortoList = self.filterOrtoList(ortoList)
        print("po 'filtrowaniu'", len(ortoList))

        # wyswietl komunikat pytanie
        if len(ortoList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     ortoList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            print(reply)
            if reply == QMessageBox.Yes:
                # pobieranie
                task = DownloadOrtofotoTask(description='Pobieranie plików ortofotomapy',
                                            ortoList=ortoList,
                                            folder=self.dockwidget.folder_fileWidget.filePath())
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasOrto_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór ortofotomapy z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.ortoClickTool)
        self.downloadOrtoForSinglePoint(point)

    def filterOrtoList(self, ortoList):
        """Filtruje listę ortofotomap"""
        if self.dockwidget.orto_filter_groupBox.isChecked():
            if not (self.dockwidget.orto_kolor_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.kolor == self.dockwidget.orto_kolor_cmbbx.currentText()]
            if not (self.dockwidget.orto_crs_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.ukladWspolrzednych.split(":")[0] == self.dockwidget.orto_crs_cmbbx.currentText()]
            if self.dockwidget.orto_from_dateTimeEdit.date():
                ortoList = [orto for orto in ortoList if
                            orto.aktualnosc >= self.dockwidget.orto_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.orto_to_dateTimeEdit.date():
                ortoList = [orto for orto in ortoList if
                            orto.aktualnosc <= self.dockwidget.orto_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not (self.dockwidget.orto_source_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.zrodloDanych == self.dockwidget.orto_source_cmbbx.currentText()]
            if not (self.dockwidget.orto_full_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.calyArkuszWyeplnionyTrescia == self.dockwidget.orto_full_cmbbx.currentText()]
            if self.dockwidget.orto_pixelFrom_lineEdit.text():
                ortoList = [orto for orto in ortoList if
                            orto.wielkoscPiksela >= float(self.dockwidget.orto_pixelFrom_lineEdit.text())]
            if self.dockwidget.orto_pixelTo_lineEdit.text():
                ortoList = [orto for orto in ortoList if
                            orto.wielkoscPiksela <= float(self.dockwidget.orto_pixelTo_lineEdit.text())]
        return ortoList

    def downloadOrtoFile(self, orto, folder):
        """Pobiera plik ortofotomapy"""
        QgsMessageLog.logMessage('start ' + orto.url)
        service_api.retreiveFile(url=orto.url, destFolder=folder)

    # endregion

    # region NMT/NMPT
    def nmt_capture_btn_clicked(self):
        """Kliknięcie plawisza pobierania NMT/NMPT przez wybór z mapy"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if path:  # pobrano ściezkę
            self.canvas.setMapTool(self.nmtClickTool)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano wskazano miejsca zapisu plików')

    def nmt_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania NMT/NMPT przez wybór warstwą wektorową"""
        bledy = 0
        layer = self.dockwidget.nmt_mapLayerComboBox.currentLayer()

        isNmpt = True if self.dockwidget.nmpt_rdbtn.isChecked() else False
        isEvrf2007 = True if self.dockwidget.evrf2007_rdbtn.isChecked() else False

        if layer:
            points = self.pointsFromVectorLayer(layer, density=1500)

            # zablokowanie klawisza pobierania
            self.dockwidget.nmt_fromLayer_btn.setEnabled(False)

            nmtList = []
            for point in points:
                subList = nmpt_api.getNmptListbyPoint1992(point=point,
                                                          isEvrf2007=isEvrf2007) if isNmpt else nmt_api.getNmtListbyPoint1992(
                    point=point, isEvrf2007=isEvrf2007)
                if subList:
                    nmtList.extend(subList)
                else:
                    bledy += 1

            self.filterNmtListAndRunTask(nmtList)
            print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.nmt_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadNmtForSinglePoint(self, point):
        """Pobiera NMT/NMPT dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        isNmpt = True if self.dockwidget.nmpt_rdbtn.isChecked() else False
        isEvrf2007 = True if self.dockwidget.evrf2007_rdbtn.isChecked() else False
        nmtList = nmpt_api.getNmptListbyPoint1992(point=point1992,
                                                  isEvrf2007=isEvrf2007) if isNmpt else nmt_api.getNmtListbyPoint1992(
            point=point1992, isEvrf2007=isEvrf2007)

        self.filterNmtListAndRunTask(nmtList)

    def filterNmtListAndRunTask(self, nmtList):
        """Filtruje listę dostępnych plików NMT/NMPT i uruchamia wątek QgsTask"""
        print("przed 'set'", len(nmtList))

        # usuwanie duplikatów
        nmtList = list(set(nmtList))
        print("po 'set'", len(nmtList))
        # filtrowanie
        nmtList = self.filterNmtList(nmtList)
        print("po 'filtrowaniu'", len(nmtList))

        # wyswietl komunikat pytanie
        if len(nmtList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     nmtList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie w zależności od typu NMT lub NMTP
                task = DownloadNmtTask(description='Pobieranie plików NMT/NMPT',
                                       nmtList=nmtList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       isNmpt=True if self.dockwidget.nmpt_rdbtn.isChecked() else False)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasNmt_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór NMT/NMPT z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.nmtClickTool)
        self.downloadNmtForSinglePoint(point)

    def filterNmtList(self, nmtList):
        """Filtruje listę NMT/NMPT"""
        # wybór formatu
        if self.dockwidget.arcinfo_rdbtn.isChecked():
            nmtList = [nmt for nmt in nmtList if nmt.format == "ARC/INFO ASCII GRID"]
        elif self.dockwidget.xyz_rdbtn.isChecked():
            nmtList = [nmt for nmt in nmtList if nmt.format == "ASCII XYZ GRID"]

        if self.dockwidget.nmt_filter_groupBox.isChecked():
            if not (self.dockwidget.nmt_crs_cmbbx.currentText() == 'wszystkie'):
                nmtList = [nmt for nmt in nmtList if
                           nmt.ukladWspolrzednych.split(":")[0] == self.dockwidget.nmt_crs_cmbbx.currentText()]
            if self.dockwidget.nmt_from_dateTimeEdit.date():
                nmtList = [nmt for nmt in nmtList if
                           nmt.aktualnosc >= self.dockwidget.nmt_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.nmt_to_dateTimeEdit.date():
                nmtList = [nmt for nmt in nmtList if
                           nmt.aktualnosc <= self.dockwidget.nmt_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not (self.dockwidget.nmt_full_cmbbx.currentText() == 'wszystkie'):
                nmtList = [nmt for nmt in nmtList if
                           nmt.calyArkuszWyeplnionyTrescia == self.dockwidget.nmt_full_cmbbx.currentText()]
            if self.dockwidget.nmt_pixelFrom_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           nmt.charakterystykaPrzestrzenna >= float(self.dockwidget.nmt_pixelFrom_lineEdit.text())]
            if self.dockwidget.nmt_pixelTo_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           nmt.charakterystykaPrzestrzenna <= float(self.dockwidget.nmt_pixelTo_lineEdit.text())]
            if self.dockwidget.nmt_mhFrom_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           nmt.bladSredniWysokosci >= float(self.dockwidget.nmt_mhFrom_lineEdit.text())]
            if self.dockwidget.nmt_mhTo_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           nmt.bladSredniWysokosci <= float(self.dockwidget.nmt_mhTo_lineEdit.text())]
        return nmtList

    def downloadNmtFile(self, nmt, folder):
        """Pobiera plik NMT/NMPT"""
        QgsMessageLog.logMessage('start ' + nmt.url)
        service_api.retreiveFile(url=nmt.url, destFolder=folder)

    # endregion

    # region LAS
    def las_capture_btn_clicked(self):
        """Kliknięcie plawisza pobierania LAS przez wybór z mapy"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if path:  # pobrano ściezkę
            self.canvas.setMapTool(self.lasClickTool)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano wskazano miejsca zapisu plików')

    def las_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania LAS przez wybór warstwą wektorową"""
        bledy = 0
        layer = self.dockwidget.las_mapLayerComboBox.currentLayer()
        isEvrf2007 = True if self.dockwidget.las_evrf2007_rdbtn.isChecked() else False

        if layer:
            points = self.pointsFromVectorLayer(layer, density=500)

            # zablokowanie klawisza pobierania
            self.dockwidget.las_fromLayer_btn.setEnabled(False)

            lasList = []
            for point in points:
                subList = las_api.getLasListbyPoint1992(point=point, isEvrf2007=isEvrf2007)
                if subList:
                    lasList.extend(subList)
                else:
                    bledy += 1

            self.filterLasListAndRunTask(lasList)
            print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.las_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadLasForSinglePoint(self, point):
        """Pobiera LAS dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        isEvrf2007 = True if self.dockwidget.las_evrf2007_rdbtn.isChecked() else False
        lasList = las_api.getLasListbyPoint1992(point=point1992, isEvrf2007=isEvrf2007)

        self.filterLasListAndRunTask(lasList)

    def filterLasListAndRunTask(self, lasList):
        """Filtruje listę dostępnych plików LAS i uruchamia wątek QgsTask"""
        print("przed 'set'", len(lasList))

        # usuwanie duplikatów
        lasList = list(set(lasList))
        print("po 'set'", len(lasList))
        # filtrowanie
        lasList = self.filterLasList(lasList)
        print("po 'filtrowaniu'", len(lasList))

        # wyswietl komunikat pytanie
        if len(lasList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     lasList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie LAS
                task = DownloadLasTask(description='Pobieranie plików LAS',
                                       lasList=lasList,
                                       folder=self.dockwidget.folder_fileWidget.filePath())
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasLas_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór LAS z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.lasClickTool)
        self.downloadLasForSinglePoint(point)

    def filterLasList(self, lasList):
        """Filtruje listę LAS"""

        if self.dockwidget.las_filter_groupBox.isChecked():
            if not (self.dockwidget.las_crs_cmbbx.currentText() == 'wszystkie'):
                lasList = [las for las in lasList if
                           las.ukladWspolrzednych.split(":")[0] == self.dockwidget.las_crs_cmbbx.currentText()]
            if self.dockwidget.las_from_dateTimeEdit.date():
                lasList = [las for las in lasList if
                           las.aktualnosc >= self.dockwidget.las_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.las_to_dateTimeEdit.date():
                lasList = [las for las in lasList if
                           las.aktualnosc <= self.dockwidget.las_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not (self.dockwidget.las_full_cmbbx.currentText() == 'wszystkie'):
                lasList = [las for las in lasList if
                           las.calyArkuszWyeplnionyTrescia == self.dockwidget.las_full_cmbbx.currentText()]
            if self.dockwidget.las_pixelFrom_lineEdit.text():
                lasList = [las for las in lasList if
                           las.charakterystykaPrzestrzenna >= float(self.dockwidget.las_pixelFrom_lineEdit.text())]
            if self.dockwidget.las_pixelTo_lineEdit.text():
                lasList = [las for las in lasList if
                           las.charakterystykaPrzestrzenna <= float(self.dockwidget.las_pixelTo_lineEdit.text())]
            if self.dockwidget.las_mhFrom_lineEdit.text():
                lasList = [las for las in lasList if
                           las.bladSredniWysokosci >= float(self.dockwidget.las_mhFrom_lineEdit.text())]
            if self.dockwidget.las_mhTo_lineEdit.text():
                lasList = [las for las in lasList if
                           las.bladSredniWysokosci <= float(self.dockwidget.las_mhTo_lineEdit.text())]
        return lasList

    def downloadLaFile(self, las, folder):
        """Pobiera plik LAS"""
        QgsMessageLog.logMessage('start ' + las.url)
        service_api.retreiveFile(url=las.url, destFolder=folder)

    # endregion

    # region Reflectance
    def reflectance_capture_btn_clicked(self):
        """Kliknięcie plawisza pobierania Intensywności przez wybór z mapy"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if path:  # pobrano ściezkę
            self.canvas.setMapTool(self.reflectanceClickTool)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano wskazano miejsca zapisu plików')

    def reflectance_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Intensywności przez wybór warstwą wektorową"""
        bledy = 0
        layer = self.dockwidget.reflectance_mapLayerComboBox.currentLayer()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=1000)

            # zablokowanie klawisza pobierania
            self.dockwidget.reflectance_fromLayer_btn.setEnabled(False)

            reflectanceList = []
            for point in points:
                subList = reflectance_api.getReflectanceListbyPoint1992(point=point)
                if subList:
                    reflectanceList.extend(subList)
                else:
                    bledy += 1

            self.filterReflectanceListAndRunTask(reflectanceList)
            print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.reflectance_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadReflectanceForSinglePoint(self, point):
        """Pobiera Intensywność dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        reflectanceList = reflectance_api.getReflectanceListbyPoint1992(point=point1992)

        self.filterReflectanceListAndRunTask(reflectanceList)

    def filterReflectanceListAndRunTask(self, reflectanceList):
        """Filtruje listę dostępnych plików Intensywności i uruchamia wątek QgsTask"""
        print("przed 'set'", len(reflectanceList))

        # usuwanie duplikatów
        reflectanceList = list(set(reflectanceList))
        print("po 'set'", len(reflectanceList))
        # filtrowanie
        reflectanceList = self.filterReflectanceList(reflectanceList)
        print("po 'filtrowaniu'", len(reflectanceList))

        # wyswietl komunikat pytanie
        if len(reflectanceList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     reflectanceList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie reflectance
                task = DownloadReflectanceTask(description='Pobieranie plików Obrazów Intensywności',
                                               reflectanceList=reflectanceList,
                                               folder=self.dockwidget.folder_fileWidget.filePath())
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasReflectance_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Intensywności z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.reflectanceClickTool)
        self.downloadReflectanceForSinglePoint(point)

    def filterReflectanceList(self, reflectanceList):
        """Filtruje listę Intensywności"""

        if self.dockwidget.reflectance_filter_groupBox.isChecked():
            if not (self.dockwidget.reflectance_crs_cmbbx.currentText() == 'wszystkie'):
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.ukladWspolrzednych.split(":")[0] == self.dockwidget.reflectance_crs_cmbbx.currentText()]
            if self.dockwidget.reflectance_from_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.aktualnosc >= self.dockwidget.reflectance_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.reflectance_to_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.aktualnosc <= self.dockwidget.reflectance_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.reflectance_pixelFrom_lineEdit.text():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.wielkoscPiksela >= float(self.dockwidget.reflectance_pixelFrom_lineEdit.text())]
            if self.dockwidget.reflectance_pixelTo_lineEdit.text():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.wielkoscPiksela <= float(self.dockwidget.las_pixelTo_lineEdit.text())]
            if not (self.dockwidget.reflectance_source_cmbbx.currentText() == 'wszystkie'):
                reflectanceList = [reflectance for reflectance in reflectanceList if
                            reflectance.zrodloDanych == self.dockwidget.reflectance_source_cmbbx.currentText()]
        return reflectanceList

    def downloadReflectanceFile(self, reflectance, folder):
        """Pobiera plik LAS"""
        QgsMessageLog.logMessage('start ' + reflectance.url)
        service_api.retreiveFile(url=reflectance.url, destFolder=folder)

    # endregion

    def pointsFromVectorLayer(self, layer, density=1000):
        """tworzy punkty do zapytań na podstawie warstwy wektorowej"""
        # zamiana na 1992
        if layer.crs() != QgsCoordinateReferenceSystem('EPSG:2180'):
            params = {
                'INPUT': layer,
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
                'OPERATION': None,
                'OUTPUT': 'TEMPORARY_OUTPUT'}
            proc = processing.run("qgis:reprojectlayer", params)
            layer = proc['OUTPUT']

        if layer.geometryType() == QgsWkbTypes.LineGeometry:
            points = utils.createPointsFromLineLayer(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            points = utils.createPointsFromPolygon(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PointGeometry:
            points = utils.createPointsFromPointLayer(layer)

        return points
