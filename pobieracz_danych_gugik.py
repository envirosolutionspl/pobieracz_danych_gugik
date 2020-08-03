# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QApplication, QMessageBox
from qgis.gui import *
from qgis.core import *
from .tasks import DownloadOrtofotoTask, DownloadAvailableFilesListTask
import asyncio, processing

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .dialogs import PobieraczDanychDockWidget
import os.path

from . import utils, ortofoto_api

"""Wersja wtyczki"""
plugin_version = '0.1'
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
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, 'EnviroSolutions')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'EnviroSolutions')
            self.toolbar.setObjectName(u'EnviroSolutions')

        self.pluginIsActive = False
        self.dockwidget = None

        self.canvas = self.iface.mapCanvas()
        # out click tool will emit a QgsPoint on every click
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.clickTool.canvasClicked.connect(self.canvas_clicked)
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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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
            #self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PobieraczDanychDockWidget()
            # Eventy
            self.dockwidget.capture_btn.clicked.connect(self.capture_btn_clicked)
            self.dockwidget.fromLayer_btn.clicked.connect(self.fromLayer_btn_clicked)
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

    def capture_btn_clicked(self):
        path = self.dockwidget.folder_fileWidget.filePath()
        if path:    # pobrano ściezkę
            self.canvas.setMapTool(self.clickTool)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano wskazano miejsca zapisu plików')

    def fromLayer_btn_clicked(self):
        """na podstawie warstwy"""
        bledy = 0
        layer = self.dockwidget.mapLayerComboBox.currentLayer()
        # TODO: zamien uklad na 92
        if layer:
            if layer.crs() != QgsCoordinateReferenceSystem('EPSG:2180'):
                params = {
                    'INPUT':layer,
                    'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:2180'),
                    'OPERATION':None,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                proc = processing.run("native:reprojectlayer", params)
                layer = proc['OUTPUT']


            points = utils.createPointsFromPolygon(layer)
            print('---', len(points))


            # # pobieranie
            # task = DownloadAvailableFilesListTask(description='Pobieranie plików ortofotomapy',
            #                             points=points)
            # QgsApplication.taskManager().addTask(task)
            # QgsMessageLog.logMessage('runtask')

            ortoList = []

            for point in points:
                subList = ortofoto_api.getOrtoListbyPoint1992(point=point)
                if subList:
                    ortoList.extend(subList)
                else:
                    bledy += 1

            self.iterateAndRunTask(ortoList)
            print("znaleziono %d bledow" % bledy)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy poligonowej')
    def downloadForSinglePoint(self, point):
        """pojedynczy punkt"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        ortoList = ortofoto_api.getOrtoListbyPoint1992(point=point1992)
        self.iterateAndRunTask(ortoList)

    def iterateAndRunTask(self, ortoList):

        print("przed 'set'", len(ortoList))

        # usuwanie duplikatów
        ortoList = list(set(ortoList))
        print("po 'set'", len(ortoList))
        # for el in ortoList:
        #     print(el.url)
        # filtrowanie
        ortoList = self.filterOrtoList(ortoList)
        print("po 'filtrowaniu'", len(ortoList))

        # wyswietl komunikat pytanie
        if len(ortoList) == 0:
            msgbox = QMessageBox(QMessageBox.Information,"Komunikat", "Nie znaleniono danych spełniających kryteria" )
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(ortoList))
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


    def canvas_clicked(self, point):
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.clickTool)
        self.downloadForSinglePoint(point)


    def filterOrtoList(self, ortoList):
        if self.dockwidget.orto_filter_groupBox.isChecked():
            if not (self.dockwidget.kolor_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.kolor == self.dockwidget.kolor_cmbbx.currentText()]
            if not (self.dockwidget.crs_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.ukladWspolrzednych.split(":")[0] == self.dockwidget.crs_cmbbx.currentText()]
            if not self.dockwidget.from_dateTimeEdit.isNull():
                ortoList = [orto for orto in ortoList if orto.aktualnosc >= self.dockwidget.from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not self.dockwidget.to_dateTimeEdit.isNull():
                ortoList = [orto for orto in ortoList if orto.aktualnosc <= self.dockwidget.to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not (self.dockwidget.source_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.zrodloDanych == self.dockwidget.source_cmbbx.currentText()]
            if not (self.dockwidget.full_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.calyArkuszWyeplnionyTrescia == self.dockwidget.full_cmbbx.currentText()]
            if self.dockwidget.pixelFrom_lineEdit.text():
                ortoList = [orto for orto in ortoList if orto.wielkoscPiksela >= float(self.dockwidget.pixelFrom_lineEdit.text())]
            if self.dockwidget.pixelTo_lineEdit.text():
                ortoList = [orto for orto in ortoList if orto.wielkoscPiksela <= float(self.dockwidget.pixelTo_lineEdit.text())]
        return ortoList

    def downloadFiles(self, orto, folder):
        QgsMessageLog.logMessage('start ' + orto.url)
        ortofoto_api.retreiveFile(orto.url, folder)
