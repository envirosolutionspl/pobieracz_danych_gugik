# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QApplication
from qgis.gui import *
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .dialogs import PobieraczDanychDockWidget
import os.path
from .gugik_api import GugikAPI

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

        icon_path = ':/plugins/pobieracz_danych_gugik/icon_pw2.png'
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

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PobieraczDanychDockWidget()
            # Eventy
            self.dockwidget.capture_btn.clicked.connect(self.capture_btn_clicked)
            self.dockwidget.fromLayer_btn.clicked.connect(self.fromLayer_btn_clicked)
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)



            # informacje o wersji
            self.dockwidget.lbl_pluginVersion.setText('%s %s' % (plugin_name, plugin_version))

            # show the dockwidget
            # TODO: fix to allow choice of dock location
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
        layer = self.dockwidget.mapLayerComboBox.currentLayer()
        if layer:
            # siatka co 1000 m

            pass

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy poligonowej')

    def canvas_clicked(self, point):
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.clickTool)
        self.captureOrtoList(point)

    def pointTo2180(self, point):
        """zamiana układu na 1992"""
        projectCrs = QgsProject.instance().crs()
        crsDest = QgsCoordinateReferenceSystem(2180)  # PL 1992
        xform = QgsCoordinateTransform(projectCrs, crsDest, QgsProject.instance())
        point1992 = xform.transform(point)
        return point1992

    def captureOrtoList(self, point):
        point1992 = self.pointTo2180(point)
        ortoList = self.filterOrtoList(self.getOrtoListWithPoint1992(point1992=point1992))

        print(len(ortoList))
        if ortoList:
            for orto in ortoList:
                task = QgsTask.fromFunction('Pobieranie pliku ortofotomapy', self.downloadFiles, orto=orto)
                QgsApplication.taskManager().addTask(task)
            self.iface.messageBar().pushSuccess("Sukces:",
                                                'Pobrano dane (%d plików) dla wskazanego punktu' % len(ortoList))
        else:
            # błąd usługi lub brak połączenia z internetem
            self.iface.messageBar().pushCritical("Błąd usługi:",
                                                 'Brak połączenia z serwerem, sprawdź czy działa połączenie z internetem', )

    def getOrtoListWithPoint1992(self, point1992):
        ortoList = GugikAPI.getOrtoListbyXY(y=point1992.x(), x=point1992.y())
        return ortoList

    def filterOrtoList(self, ortoList):
        if self.dockwidget.orto_filter_groupBox.isChecked():
            if not (self.dockwidget.kolor_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.kolor == self.dockwidget.kolor_cmbbx.currentText()]
            if not (self.dockwidget.crs_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if orto.ukladWspolrzednych.split(":")[0] == self.dockwidget.crs_cmbbx.currentText()]
            if self.dockwidget.from_dateTimeEdit.date():
                ortoList = [orto for orto in ortoList if orto.aktualnosc >= self.dockwidget.from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.to_dateTimeEdit.date():
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

    def downloadFiles(self, task, orto):
        GugikAPI.retreiveFile(orto.url, self.dockwidget.folder_fileWidget.filePath())
