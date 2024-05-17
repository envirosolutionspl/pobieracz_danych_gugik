# -*- coding: utf-8 -*-
from PyQt5.uic.properties import QtWidgets
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QApplication, QMessageBox
from qgis.gui import *
from qgis.core import *
from .tasks import (
    DownloadOrtofotoTask, DownloadNmtTask, DownloadNmptTask, DownloadLasTask, DownloadReflectanceTask,
    DownloadBdotTask, DownloadBdooTask, DownloadWfsTask, DownloadWfsEgibTask, DownloadPrngTask,
    DownloadPrgTask, DownloadModel3dTask, DownloadEgibExcelTask, DownloadOpracowaniaTyflologiczneTask,
    DownloadOsnowaTask, DownloadAerotriangulacjaTask, DownloadMozaikaTask, DownloadWizKartoTask,
    DownloadKartotekiOsnowTask, DownloadArchiwalnyBdotTask, DownloadZdjeciaLotniczeTask)
import asyncio, processing

# Initialize Qt resources from file resources.py
from .resources import *
import requests

# Import the code for the DockWidget
from .dialogs import PobieraczDanychDockWidget
import os.path
import sys
import subprocess

from . import utils, ortofoto_api, nmt_api, nmpt_api, service_api, las_api, reflectance_api, aerotriangulacja_api, \
    mozaika_api, wizualizacja_karto_api, kartoteki_osnow_api, zdjecia_lotnicze_api, egib_api

"""Wersja wtyczki"""
plugin_version = '1.1.0'
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

        if Qgis.QGIS_VERSION_INT >= 31000:
            from .qgis_feed import QgisFeed
            self.feed = QgisFeed()
            self.feed.initFeed()

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
        self.wfsClickTool = QgsMapToolEmitPoint(self.canvas)
        self.wfsClickTool.canvasClicked.connect(self.canvasWfs_clicked)
        self.aerotriangulacjaClickTool = QgsMapToolEmitPoint(self.canvas)
        self.aerotriangulacjaClickTool.canvasClicked.connect(self.canvasAerotriangulacja_clicked)
        self.mozaikaClickTool = QgsMapToolEmitPoint(self.canvas)
        self.mozaikaClickTool.canvasClicked.connect(self.canvasMozaika_clicked)
        self.wizualizacja_kartoClickTool = QgsMapToolEmitPoint(self.canvas)
        self.wizualizacja_kartoClickTool.canvasClicked.connect(self.canvasWizualizacja_karto_clicked)
        self.kartoteki_osnowClickTool = QgsMapToolEmitPoint(self.canvas)
        self.kartoteki_osnowClickTool.canvasClicked.connect(self.canvasKartoteki_osnow_clicked)
        self.zdjecia_lotniczeClickTool = QgsMapToolEmitPoint(self.canvas)
        self.zdjecia_lotniczeClickTool.canvasClicked.connect(self.canvasZdjecia_lotnicze_clicked)

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
                try:
                    # Create the dockwidget (after translation) and keep reference
                    self.dockwidget = PobieraczDanychDockWidget()
                except requests.exceptions.ConnectionError:
                    self.iface.messageBar().pushWarning("Ostrzeżenie:", 'Brak połączenia z internetem')
                    self.pluginIsActive = False
                    return

            # Eventy

            self.dockwidget.wms_rdbtn.toggled.connect(self.btnstate)
            self.dockwidget.wms_rdbtn.toggled.emit(True)

            self.dockwidget.paczka_rdbtn.toggled.connect(self.btnstate)
            self.dockwidget.paczka_rdbtn.toggled.emit(True)

            self.dockwidget.inne_rdbtn.toggled.connect(self.btnstate)
            self.dockwidget.inne_rdbtn.toggled.emit(True)

            self.dockwidget.wfs_rdbtn.toggled.connect(self.btnstate)
            self.dockwidget.wfs_rdbtn.toggled.emit(True)
            self.dockwidget.wfs_capture_btn.clicked.connect(lambda: self.capture_btn_clicked(self.wfsClickTool))
            self.dockwidget.wfs_fromLayer_btn.clicked.connect(self.wfs_fromLayer_btn_clicked)

            self.dockwidget.orto_capture_btn.clicked.connect(lambda: self.capture_btn_clicked(self.ortoClickTool))
            self.dockwidget.orto_fromLayer_btn.clicked.connect(self.orto_fromLayer_btn_clicked)

            self.dockwidget.nmt_capture_btn.clicked.connect(lambda: self.capture_btn_clicked(self.nmtClickTool))
            self.dockwidget.nmt_fromLayer_btn.clicked.connect(self.nmt_fromLayer_btn_clicked)

            self.dockwidget.las_capture_btn.clicked.connect(lambda: self.capture_btn_clicked(self.lasClickTool))
            self.dockwidget.las_fromLayer_btn.clicked.connect(self.las_fromLayer_btn_clicked)

            self.dockwidget.reflectance_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.reflectanceClickTool))
            self.dockwidget.reflectance_fromLayer_btn.clicked.connect(self.reflectance_fromLayer_btn_clicked)

            self.dockwidget.bdot_selected_powiat_btn.clicked.connect(self.bdot_selected_powiat_btn_clicked)
            self.dockwidget.bdot_selected_woj_btn.clicked.connect(self.bdot_selected_woj_btn_clicked)
            self.dockwidget.bdot_polska_btn.clicked.connect(self.bdot_polska_btn_clicked)

            self.dockwidget.bdoo_selected_woj_btn.clicked.connect(self.bdoo_selected_woj_btn_clicked)
            self.dockwidget.bdoo_selected_polska_btn.clicked.connect(self.bdoo_selected_polska_btn_clicked)

            self.dockwidget.prng_selected_btn.clicked.connect(self.prng_selected_btn_clicked)

            self.dockwidget.prg_gml_rdbtn.toggled.connect(self.radioButtonState_PRG)
            # self.dockwidget.prg_gml_rdbtn.toggled.emit(True)
            self.dockwidget.radioButton_adres_powiat.toggled.connect(self.radioButton_powiaty_PRG)
            self.dockwidget.radioButton_adres_wojew.toggled.connect(self.radioButton_wojewodztwa_PRG)
            self.dockwidget.radioButton_jend_admin_wojew.toggled.connect(self.radioButton_wojewodztwa_PRG)
            self.dockwidget.radioButton_adres_kraj.toggled.connect(self.radioButton_kraj_PRG)
            self.dockwidget.radioButton_granice_spec.toggled.connect(self.radioButton_kraj_PRG)
            self.dockwidget.radioButton_jedn_admin_kraj.toggled.connect(self.radioButton_kraj_PRG)
            self.dockwidget.radioButton_adres_gmin.toggled.connect(self.radioButton_gmina_PRG)
            self.dockwidget.prg_selected_btn.clicked.connect(self.prg_selected_btn_clicked)

            self.dockwidget.model3d_selected_powiat_btn.clicked.connect(self.model3d_selected_powiat_btn_clicked)

            self.dockwidget.wfs_egib_selected_pow_btn.clicked.connect(self.wfs_egib_selected_pow_btn_clicked)

            self.dockwidget.powiat_egib_excel_rdbtn.toggled.connect(self.radioButton_powiaty_egib_excel)
            self.dockwidget.wojew_egib_excel_rdbtn.toggled.connect(self.radioButton_wojewodztwa_egib_excel)
            self.dockwidget.kraj_egib_excel_rdbtn.toggled.connect(self.radioButton_kraj_egib_excel)
            self.dockwidget.egib_excel_selected_btn.clicked.connect(self.egib_excel_selected_btn_clicked)

            self.dockwidget.tyflologiczne_selected_btn.clicked.connect(self.tyflologiczne_selected_btn_clicked)

            self.dockwidget.osnowa_selected_btn.clicked.connect(self.osnowa_selected_btn_clicked)

            self.dockwidget.aerotriangulacja_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.aerotriangulacjaClickTool))
            self.dockwidget.aerotriangulacja_fromLayer_btn.clicked.connect(self.aerotriangulacja_fromLayer_btn_clicked)

            self.dockwidget.linie_mozaikowania_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.mozaikaClickTool))
            self.dockwidget.linie_mozaikowania_arch_fromLayer_btn.clicked.connect(
                self.linie_mozaikowania_arch_fromLayer_btn_clicked)

            self.dockwidget.wizualizacja_karto_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.wizualizacja_kartoClickTool))
            self.dockwidget.wizualizacja_karto_fromLayer_btn.clicked.connect(
                self.wizualizacja_karto_fromLayer_btn_clicked)

            self.dockwidget.osnowa_arch_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.kartoteki_osnowClickTool))
            self.dockwidget.osnowa_arch_fromLayer_btn.clicked.connect(self.osnowa_arch_fromLayer_btn_clicked)

            self.dockwidget.archiwalne_bdot_selected_powiat_btn.clicked.connect(
                self.archiwalne_bdot_selected_powiat_btn_clicked)

            self.dockwidget.zdjecia_lotnicze_capture_btn.clicked.connect(
                lambda: self.capture_btn_clicked(self.zdjecia_lotniczeClickTool))
            self.dockwidget.zdjecia_lotnicze_fromLayer_btn.clicked.connect(self.zdjecia_lotnicze_fromLayer_btn_clicked)

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

    # region WFS
    def btnstate(self):
        if self.dockwidget.wfs_rdbtn.isChecked():
            self.dockwidget.wfs_groupBox.setVisible(True)
            self.dockwidget.orto_groupBox.setVisible(False)
            self.dockwidget.nmt_groupBox.setVisible(False)
            self.dockwidget.las_groupBox.setVisible(False)
            self.dockwidget.reflectance_groupBox.setVisible(False)
            self.dockwidget.bdot_groupBox.setVisible(False)
            self.dockwidget.bdoo_groupBox.setVisible(False)
            self.dockwidget.wfs_egib_groupBox.setVisible(False)
            self.dockwidget.prng_groupBox.setVisible(False)
            self.dockwidget.prg_groupBox.setVisible(False)
            self.dockwidget.model3d_groupBox.setVisible(False)
            self.dockwidget.egib_excel_groupBox.setVisible(False)
            self.dockwidget.tyflologiczne_groupBox.setVisible(False)
            self.dockwidget.osnowa_groupBox.setVisible(False)
            self.dockwidget.aerotriangulacja_groupBox.setVisible(False)
            self.dockwidget.linie_mozaikowania_groupBox.setVisible(False)
            self.dockwidget.wizualizacja_karto_groupBox.setVisible(False)
            self.dockwidget.archiwalne_bdot_groupBox.setVisible(False)
            self.dockwidget.zdjecia_lotnicze_groupBox.setVisible(False)
            # print('wfs')
        if self.dockwidget.wms_rdbtn.isChecked():
            self.dockwidget.wfs_groupBox.setVisible(False)
            self.dockwidget.orto_groupBox.setVisible(True)
            self.dockwidget.nmt_groupBox.setVisible(True)
            self.dockwidget.las_groupBox.setVisible(True)
            self.dockwidget.reflectance_groupBox.setVisible(True)
            self.dockwidget.bdot_groupBox.setVisible(False)
            self.dockwidget.bdoo_groupBox.setVisible(False)
            self.dockwidget.wfs_egib_groupBox.setVisible(False)
            self.dockwidget.prng_groupBox.setVisible(False)
            self.dockwidget.prg_groupBox.setVisible(False)
            self.dockwidget.model3d_groupBox.setVisible(False)
            self.dockwidget.egib_excel_groupBox.setVisible(False)
            self.dockwidget.tyflologiczne_groupBox.setVisible(False)
            self.dockwidget.osnowa_groupBox.setVisible(False)
            self.dockwidget.aerotriangulacja_groupBox.setVisible(False)
            self.dockwidget.linie_mozaikowania_groupBox.setVisible(False)
            self.dockwidget.wizualizacja_karto_groupBox.setVisible(False)
            self.dockwidget.archiwalne_bdot_groupBox.setVisible(False)
            self.dockwidget.zdjecia_lotnicze_groupBox.setVisible(False)
            # print('wms')
        if self.dockwidget.paczka_rdbtn.isChecked():
            self.dockwidget.wfs_groupBox.setVisible(False)
            self.dockwidget.orto_groupBox.setVisible(False)
            self.dockwidget.nmt_groupBox.setVisible(False)
            self.dockwidget.las_groupBox.setVisible(False)
            self.dockwidget.reflectance_groupBox.setVisible(False)
            self.dockwidget.bdot_groupBox.setVisible(True)
            self.dockwidget.bdoo_groupBox.setVisible(True)
            self.dockwidget.wfs_egib_groupBox.setVisible(True)
            self.dockwidget.prng_groupBox.setVisible(True)
            self.dockwidget.prg_groupBox.setVisible(True)
            self.dockwidget.model3d_groupBox.setVisible(True)
            self.dockwidget.egib_excel_groupBox.setVisible(False)
            self.dockwidget.tyflologiczne_groupBox.setVisible(False)
            self.dockwidget.osnowa_groupBox.setVisible(False)
            self.dockwidget.aerotriangulacja_groupBox.setVisible(False)
            self.dockwidget.linie_mozaikowania_groupBox.setVisible(False)
            self.dockwidget.wizualizacja_karto_groupBox.setVisible(False)
            self.dockwidget.archiwalne_bdot_groupBox.setVisible(True)
            self.dockwidget.zdjecia_lotnicze_groupBox.setVisible(False)
            # print('paczka danych')
        if self.dockwidget.inne_rdbtn.isChecked():
            self.dockwidget.wfs_groupBox.setVisible(False)
            self.dockwidget.orto_groupBox.setVisible(False)
            self.dockwidget.nmt_groupBox.setVisible(False)
            self.dockwidget.las_groupBox.setVisible(False)
            self.dockwidget.reflectance_groupBox.setVisible(False)
            self.dockwidget.bdot_groupBox.setVisible(False)
            self.dockwidget.bdoo_groupBox.setVisible(False)
            self.dockwidget.wfs_egib_groupBox.setVisible(False)
            self.dockwidget.prng_groupBox.setVisible(False)
            self.dockwidget.prg_groupBox.setVisible(False)
            self.dockwidget.model3d_groupBox.setVisible(False)
            self.dockwidget.egib_excel_groupBox.setVisible(True)
            self.dockwidget.tyflologiczne_groupBox.setVisible(True)
            self.dockwidget.osnowa_groupBox.setVisible(True)
            self.dockwidget.aerotriangulacja_groupBox.setVisible(True)
            self.dockwidget.linie_mozaikowania_groupBox.setVisible(True)
            self.dockwidget.wizualizacja_karto_groupBox.setVisible(True)
            self.dockwidget.archiwalne_bdot_groupBox.setVisible(False)
            self.dockwidget.zdjecia_lotnicze_groupBox.setVisible(True)

    def wfs_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania danych WFS przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.wfs_mapLayerComboBox.currentLayer()

        # zablokowanie klawisza pobierania
        self.dockwidget.wfs_fromLayer_btn.setEnabled(False)

        # zamiana układu na 92
        if layer:
            self.downloadWfsForLayer(layer)

            # odblokowanie klawisza pobierania
            self.dockwidget.wfs_fromLayer_btn.setEnabled(True)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def test(self):
        print('test')

    def downloadWfsForLayer(self, layer):
        """Pobiera dane WFS """

        if (isinstance(layer, QgsPointXY)):
            print('isinstance xy')
            crs = QgsProject.instance().crs().authid()
            vp = QgsVectorLayer("Point?crs=" + crs, "vectpoi", "memory")
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(layer))
            dp = vp.dataProvider()
            dp.addFeature(feature)
            layer = vp

        layer1992 = utils.layerTo2180(layer=layer)

        skorowidzeLayer = self.dockwidget.wfsFetch.getWfsListbyLayer1992(
            layer=layer1992,
            wfsService=self.dockwidget.wfs_service_cmbbx.currentText(),
            typename=self.dockwidget.wfs_layer_cmbbx.currentText())
        skorowidzeLayer.updatedFields.connect(self.test)
        if skorowidzeLayer.isValid():
            urls = []
            QgsProject.instance().addMapLayer(skorowidzeLayer)
            layerWithAttributes = QgsProject.instance().mapLayer(skorowidzeLayer.id())

            for feat in layerWithAttributes.getFeatures():
                urls.append(feat['url_do_pobrania'])

            # wyswietl komunikat pytanie
            if len(urls) == 0:
                msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                     "Nie znaleziono danych we wskazanej warstwie WFS lub obszar wyszukiwania jest zbyt duży dla usługi WFS")
                msgbox.exec_()
                QgsProject.instance().removeMapLayer(skorowidzeLayer.id())
                return
            else:
                msgbox = QMessageBox(QMessageBox.Question,
                                     "Potwierdź pobieranie",
                                     "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                         urls))
                msgbox.addButton(QMessageBox.Yes)
                msgbox.addButton(QMessageBox.No)
                msgbox.setDefaultButton(QMessageBox.No)
                reply = msgbox.exec()

                if reply == QMessageBox.Yes:
                    # pobieranie
                    self.runWfsTask(urls)
                else:
                    QgsProject.instance().removeMapLayer(skorowidzeLayer.id())

    def runWfsTask(self, urlList):
        """Filtruje listę dostępnych plików ortofotomap i uruchamia wątek QgsTask"""
        task = DownloadWfsTask(description='Pobieranie plików z WFS',
                               urlList=urlList,
                               folder=self.dockwidget.folder_fileWidget.filePath(),
                               iface=self.iface)
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def canvasWfs_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór ortofotomapy z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.wfsClickTool)
        self.downloadWfsForLayer(point)

    def downloadWfsFile(self, orto, folder):
        """Pobiera plik z wfs"""
        QgsMessageLog.logMessage('start ' + orto.url)
        service_api.retreiveFile(url=orto.url, destFolder=folder)

    # endregion

    # region ORTOFOTOMAPA

    def orto_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania ortofotomapy przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

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
        # print("przed 'set'", len(urlList))

        # usuwanie duplikatów
        ortoList = list(set(ortoList))
        # print("po 'set'", len(urlList))
        # filtrowanie
        ortoList = self.filterOrtoList(ortoList)
        # print("po 'filtrowaniu'", len(urlList))

        # wyswietl komunikat pytanie
        if len(ortoList) == 0:
            QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria").exec_()
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

            if reply == QMessageBox.Yes:
                # pobieranie
                task = DownloadOrtofotoTask(description='Pobieranie plików ortofotomapy',
                                            ortoList=ortoList,
                                            folder=self.dockwidget.folder_fileWidget.filePath(),
                                            iface=self.iface)
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

        # ograniczenie tylko do najnowszego
        if self.dockwidget.orto_newest_chkbx.isChecked():
            ortoList = utils.onlyNewest(ortoList)
            # print(ortoList)
        return ortoList

    def downloadOrtoFile(self, orto, folder):
        """Pobiera plik ortofotomapy"""
        QgsMessageLog.logMessage('start ' + orto.url)
        service_api.retreiveFile(url=orto.url, destFolder=folder)

    # endregion

    # region NMT/NMPT

    def nmt_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania NMT/NMPT przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

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
                resp = nmpt_api.getNmptListbyPoint1992(point=point,
                                                       isEvrf2007=isEvrf2007) if isNmpt else nmt_api.getNmtListbyPoint1992(
                    point=point, isEvrf2007=isEvrf2007)
                if resp[0]:
                    nmtList.extend(resp[1])
                else:
                    bledy += 1

            self.filterNmtListAndRunTask(nmtList, isNmpt)
            # print("%d zapytań się nie powiodło" % bledy)

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
        resp = nmpt_api.getNmptListbyPoint1992(point=point1992,
                                               isEvrf2007=isEvrf2007) if isNmpt else nmt_api.getNmtListbyPoint1992(
            point=point1992, isEvrf2007=isEvrf2007)
        if resp[0]:
            nmtList = resp[1]
            self.filterNmtListAndRunTask(nmtList, isNmpt)
        else:
            self.iface.messageBar().pushCritical("Błąd pobierania",
                                                 f"Nie udało się pobrać danych z serwera. Powód:{resp[1]}")

    def filterNmtListAndRunTask(self, nmtList, isNmpt):
        """Filtruje listę dostępnych plików NMT/NMPT i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        nmtList = list(set(nmtList))
        # filtrowanie
        nmtList = self.filterNmtList(nmtList)

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

            if reply == QMessageBox.Yes and isNmpt is False and self.dockwidget.nmt_rdbtn.isChecked():
                # pobieranie NMT
                task = DownloadNmtTask(description='Pobieranie plików NMT',
                                       nmtList=nmtList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       isNmpt=False,
                                       iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')
            
            else:
                # pobieranie NMTP
                task = DownloadNmptTask(description='Pobieranie plików NMPT',
                                       nmptList=nmtList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       isNmpt=True,
                                       iface=self.iface)
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

        # ograniczenie tylko do najnowszego
        if self.dockwidget.nmt_newest_chkbx.isChecked():
            nmtList = utils.onlyNewest(nmtList)
        return nmtList

    def downloadNmtFile(self, nmt, folder):
        """Pobiera plik NMT/NMPT"""
        QgsMessageLog.logMessage('start ' + nmt.url)
        service_api.retreiveFile(url=nmt.url, destFolder=folder)

    # endregion

    # region LAS

    def las_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania LAS przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False
        layer = self.dockwidget.las_mapLayerComboBox.currentLayer()
        if layer:
            points = self.pointsFromVectorLayer(layer, density=250)
            las_list = []
            # zablokowanie klawisza pobierania
            self.dockwidget.las_fromLayer_btn.setEnabled(False)
            for point in points:
                sub_list = las_api.getLasListbyPoint1992(point, self.dockwidget.las_evrf2007_rdbtn.isChecked())
                if not sub_list:
                    continue
                las_list.extend(sub_list)
            self.filterLasListAndRunTask(las_list)
        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:", 'Nie wskazano warstwy wektorowej')

        # odblokowanie klawisza pobierania
        self.dockwidget.las_fromLayer_btn.setEnabled(True)

    def downloadLasForSinglePoint(self, point):
        """Pobiera LAS dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        isEvrf2007 = True if self.dockwidget.las_evrf2007_rdbtn.isChecked() else False
        lasList = las_api.getLasListbyPoint1992(
            point=point1992,
            isEvrf2007=isEvrf2007
            # isLaz=True if self.dockwidget.las_laz_rdbtn.isChecked() else False
        )

        self.filterLasListAndRunTask(lasList)

    def filterLasListAndRunTask(self, lasList):
        """Filtruje listę dostępnych plików LAS i uruchamia wątek QgsTask"""
        # print("przed 'set'", len(lasList))

        # usuwanie duplikatów
        lasList = list(set(lasList))
        # print("po 'set'", len(lasList))
        # filtrowanie
        lasList = self.filterLasList(lasList)
        # print("po 'filtrowaniu'", len(lasList))

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
                task = DownloadLasTask(description='Pobieranie plików LAZ',
                                       lasList=lasList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       iface=self.iface)
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

    def reflectance_fromLayer_btn_clicked(self):
        """Kliknięcie klawisza pobierania Intensywności przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

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
        # zablokowanie klawisza pobierania
        # self.dockwidget.reflectance_capture_btn.setEnabled(False)

        reflectanceList = reflectance_api.getReflectanceListbyPoint1992(point=point1992)
        # print("reflectanceList: ", list(reflectanceList))
        self.filterReflectanceListAndRunTask(reflectanceList)

        # odblokowanie klawisza pobierania
        # self.dockwidget.reflectance_capture_btn.setEnabled(True)

    def filterReflectanceListAndRunTask(self, reflectanceList):
        """Filtruje listę dostępnych plików Intensywności i uruchamia wątek QgsTask"""
        # print("przed 'set'", len(reflectanceList))

        # usuwanie duplikatów
        reflectanceList = list(set(reflectanceList))
        # print("po 'set'", len(reflectanceList))
        # filtrowanie
        reflectanceList = self.filterReflectanceList(reflectanceList)
        # print("po 'filtrowaniu'", len(reflectanceList))

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
                                               folder=self.dockwidget.folder_fileWidget.filePath(),
                                               iface=self.iface)
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
                                   reflectance.ukladWspolrzednych.split(":")[
                                       0] == self.dockwidget.reflectance_crs_cmbbx.currentText()]
            if self.dockwidget.reflectance_from_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.aktualnosc >= self.dockwidget.reflectance_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.reflectance_to_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.aktualnosc <= self.dockwidget.reflectance_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.reflectance_pixelFrom_lineEdit.text():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.wielkoscPiksela >= float(
                                       self.dockwidget.reflectance_pixelFrom_lineEdit.text())]
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

    # region BDOT10k
    def bdot_selected_powiat_btn_clicked(self):
        """Pobiera paczkę danych BDOT10k dla powiatu"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        format_danych = None

        if self.dockwidget.bdot_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.bdot_shp_rdbtn.isChecked():
            format_danych = "SHP"
        elif self.dockwidget.bdot_old_gml_rdbtn.isChecked():
            format_danych = "GML 2011"
        elif self.dockwidget.bdot_gpkg_rdbtn.isChecked():
            format_danych = "GPKG"

        powiatName = self.dockwidget.powiat_cmbbx.currentText()
        if not powiatName:
            self.no_area_specified_warning()
            return
        teryt = self.dockwidget.regionFetch.getTerytByPowiatName(powiatName)

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie powiatowej paczki BDOT10k dla {powiatName}({teryt})',
                                            level=Qgis.Info, duration=10)
        task = DownloadBdotTask(
            description=f'Pobieranie powiatowej paczki BDOT10k dla {powiatName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=2,
            format_danych=format_danych,
            teryt=teryt,
            iface=self.iface
        )
        task.task_finished.connect(self.bdot_task_finished)
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def bdot_selected_woj_btn_clicked(self):
        """Pobiera paczkę danych BDOT10k dla województwa"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        format_danych = None

        if self.dockwidget.bdot_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.bdot_shp_rdbtn.isChecked():
            format_danych = "SHP"
        elif self.dockwidget.bdot_old_gml_rdbtn.isChecked():
            format_danych = "GML 2011"
        elif self.dockwidget.bdot_gpkg_rdbtn.isChecked():
            format_danych = "GPKG"

        wojewodztwoName = self.dockwidget.wojewodztwo_cmbbx.currentText()
        if not wojewodztwoName:
            self.no_area_specified_warning()
            return
        teryt = self.dockwidget.regionFetch.getTerytByWojewodztwoName(wojewodztwoName)
        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie wojewódzkiej paczki BDOT10k dla {wojewodztwoName}({teryt})',
                                            level=Qgis.Info, duration=10)
        task = DownloadBdotTask(
            description=f'Pobieranie wojewódzkiej paczki BDOT10k dla {wojewodztwoName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=1,
            format_danych=format_danych,
            teryt=teryt,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def bdot_polska_btn_clicked(self):
        """Pobiera paczkę danych BDOT10k dla całej Polski"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        format_danych = None

        if self.dockwidget.bdot_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.bdot_shp_rdbtn.isChecked():
            format_danych = "SHP"
        elif self.dockwidget.bdot_old_gml_rdbtn.isChecked():
            format_danych = "GML 2011"
        elif self.dockwidget.bdot_gpkg_rdbtn.isChecked():
            format_danych = "GPKG"
        self.iface.messageBar().pushMessage("Informacja",
                                            'Pobieranie paczki BDOT10k dla całego kraju',
                                            level=Qgis.Info, duration=10)
        task = DownloadBdotTask(
            description='Pobieranie paczki BDOT10k dla całego kraju',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=0,
            format_danych=format_danych,
            teryt=None,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def bdot_task_finished(self, result, exception):
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage(
                "Sukces",
                "Udało się! Dane BDOT10k zostały pobrane.",
                level=Qgis.Success,
                duration=10
            )
        else:
            if exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise exception
            self.iface.messageBar().pushMessage(
                "Błąd",
                "Dane BDOT10k nie zostały pobrane.",
                level=Qgis.Warning,
                duration=10
            )


    # region BDOO
    def bdoo_selected_woj_btn_clicked(self):
        """Pobiera paczkę danych BDOO dla województwa"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        rok = self.dockwidget.bdoo_dateEdit_comboBox.currentText()
        wojewodztwoName = self.dockwidget.bdoo_wojewodztwo_cmbbx.currentText()
        if not wojewodztwoName:
            self.no_area_specified_warning()
            return
        teryt = self.dockwidget.regionFetch.getTerytByWojewodztwoName(wojewodztwoName)

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie wojewódzkiej paczki BDOO dla {wojewodztwoName}({teryt})',
                                            level=Qgis.Info, duration=10)
        task = DownloadBdooTask(
            description=f'Pobieranie wojewódzkiej paczki BDOO dla {wojewodztwoName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=1,
            rok=rok,
            teryt=teryt,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def bdoo_selected_polska_btn_clicked(self):
        """Pobiera paczkę danych BDOO dla całej Polski"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        rok = self.dockwidget.bdoo_dateEdit_comboBox.currentText()
        self.iface.messageBar().pushMessage("Informacja",
                                            'Pobieranie paczki BDOO dla całego kraju',
                                            level=Qgis.Info, duration=10)
        task = DownloadBdooTask(
            description='Pobieranie paczki BDOO dla całego kraju',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=0,
            rok=rok,
            teryt=None,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion PRNG
    def prng_selected_btn_clicked(self):
        """Pobiera paczkę danych PRNG"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        rodzaj = None
        format_danych = None

        if self.dockwidget.prng_miejsco_rdbtn.isChecked():
            rodzaj = "MIEJSCOWOSCI"
            description = 'Pobieranie danych z Państwowego Rejestru Nazw Geograficznych - nazwy miejscowości RP'
        elif self.dockwidget.prng_fizjog_rdbtn.isChecked():
            rodzaj = "OBIEKTY_FIZJOGRAFICZNE"
            description = 'Pobieranie danych z Państwowego Rejestru Nazw Geograficznych - nazwy obiektów ' \
                          'fizjografocznych RP '
        elif self.dockwidget.prng_swiat_rdbtn.isChecked():
            rodzaj = "SWIAT"
            description = 'Pobieranie danych z Państwowego Rejestru Nazw Geograficznych - polskie nazwy geograficzne ' \
                          'świata '

        if self.dockwidget.prng_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.prng_shp_rdbtn.isChecked():
            format_danych = "SHP"
        elif self.dockwidget.prng_xlsx_rdbtn.isChecked():
            format_danych = "XLSX"

        self.iface.messageBar().pushMessage("Informacja",
                                            f'{description} w formacie {format_danych}',
                                            level=Qgis.Info, duration=10)
        task = DownloadPrngTask(
            description=f'{description} w formacie {format_danych}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            rodzaj=rodzaj,
            format_danych=format_danych,
            iface=self.iface
        )

        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # endregion PRG
    def radioButtonState_PRG(self):
        """Ustala dostępność rodzaju danych PRG na podstawie formatu danych"""
        self.dockwidget.radioButton_adres_kraj.setEnabled(True)
        self.dockwidget.radioButton_granice_spec.setEnabled(True)
        self.dockwidget.radioButton_jedn_admin_kraj.setEnabled(True)

        if self.dockwidget.prg_gml_rdbtn.isChecked():
            self.dockwidget.radioButton_adres_kraj.setChecked(True)
            self.dockwidget.radioButton_adres_gmin.setEnabled(False)
            self.dockwidget.radioButton_adres_powiat.setEnabled(False)
            self.dockwidget.radioButton_adres_wojew.setEnabled(False)
            self.dockwidget.radioButton_adres_wojew.setEnabled(False)
            self.dockwidget.radioButton_jend_admin_wojew.setEnabled(False)
        else:
            self.dockwidget.radioButton_adres_gmin.setChecked(True)
            self.dockwidget.radioButton_adres_gmin.setEnabled(True)
            self.dockwidget.radioButton_adres_powiat.setEnabled(True)
            self.dockwidget.radioButton_adres_wojew.setEnabled(True)
            self.dockwidget.radioButton_adres_wojew.setEnabled(True)
            self.dockwidget.radioButton_jend_admin_wojew.setEnabled(True)

    def radioButton_gmina_PRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych gminy"""
        if self.dockwidget.radioButton_adres_gmin.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(True)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(True)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButton_powiaty_PRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych powiatowych"""
        if self.dockwidget.radioButton_adres_powiat.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(True)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButton_wojewodztwa_PRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych wojewódzkich"""
        if self.dockwidget.radioButton_adres_wojew.isChecked() or self.dockwidget.radioButton_jend_admin_wojew.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(False)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButton_kraj_PRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych krajowych"""
        if self.dockwidget.radioButton_adres_kraj.isChecked() or self.dockwidget.radioButton_granice_spec.isChecked() or self.dockwidget.radioButton_jedn_admin_kraj.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(False)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(False)

    def prg_selected_btn_clicked(self):
        """Pobiera paczkę danych PRG"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return
        prg_format_danych = ''

        if self.dockwidget.prg_shp_rdbtn.isChecked():
            prg_format_danych = 'shp'
        elif self.dockwidget.prg_gml_rdbtn.isChecked():
            prg_format_danych = 'gml'

        if self.dockwidget.radioButton_adres_gmin.isChecked():
            gmina_name = self.dockwidget.prg_gmina_cmbbx.currentText()
            teryt = self.dockwidget.regionFetch.getTerytByGminaName(gmina_name)
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?teryt={teryt}&adresy"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z gminy {gmina_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_powiat.isChecked():
            powiat_name = self.dockwidget.prg_powiat_cmbbx.currentText()
            teryt = self.dockwidget.regionFetch.getTerytByPowiatName(powiat_name)
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?teryt={teryt}&adresy_pow"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z powiatu {powiat_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_wojew.isChecked():
            wojewodztwo_name = self.dockwidget.prg_wojewodztwo_cmbbx.currentText()
            teryt = self.dockwidget.regionFetch.getTerytByWojewodztwoName(wojewodztwo_name)
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?teryt={teryt}&adresy_woj"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z województwa {wojewodztwo_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_kraj.isChecked():
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?adresy_zbiorcze_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z całego kraju - format {prg_format_danych}'
        elif self.dockwidget.radioButton_granice_spec.isChecked():
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?granice_specjalne_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - granice specjalne z całego kraju - format {prg_format_danych}'
        elif self.dockwidget.radioButton_jend_admin_wojew.isChecked():
            wojewodztwo_name = self.dockwidget.prg_wojewodztwo_cmbbx.currentText()
            teryt = self.dockwidget.regionFetch.getTerytByWojewodztwoName(wojewodztwo_name)
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?teryt={teryt}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - jednostki administracyjne województwa {wojewodztwo_name} ({teryt})'
        elif self.dockwidget.radioButton_jedn_admin_kraj.isChecked():
            self.url = f"https://integracja.gugik.gov.pl/PRG/pobierz.php?jednostki_administracyjne_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - jednostki administracyjne całego kraju - format {prg_format_danych}'

        self.iface.messageBar().pushMessage("Informacja", description, level=Qgis.Info, duration=10)

        task = DownloadPrgTask(
            description=f'Pobieranie danych z Państwowego Rejestru Granic',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            url=self.url,
            iface=self.iface
        )

        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # endregion modele 3D
    def model3d_selected_powiat_btn_clicked(self):
        """Pobiera paczkę danych modulu 3D budynków"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        standard = []
        if self.dockwidget.model3d_lod1_rdbtn.isChecked() and not self.dockwidget.model3d_lod2_rdbtn.isChecked():
            standard = ["LOD1"]
        elif self.dockwidget.model3d_lod2_rdbtn.isChecked() and not self.dockwidget.model3d_lod1_rdbtn.isChecked():
            standard = ["LOD2"]
        elif self.dockwidget.model3d_lod1_rdbtn.isChecked() and self.dockwidget.model3d_lod2_rdbtn.isChecked():
            standard = ["LOD1", "LOD2"]
        elif not self.dockwidget.model3d_lod1_rdbtn.isChecked() and not self.dockwidget.model3d_lod2_rdbtn.isChecked():
            msgbox = QMessageBox(QMessageBox.Information, "Ostrzeżenie:",
                                 f"Nie wybrano standardu")
            msgbox.exec_()
            return False

        od_data = int(str(self.dockwidget.model3d_dateEdit_1.dateTime().toPyDateTime().date())[0:4])
        do_data = int(str(self.dockwidget.model3d_dateEdit_2.dateTime().toPyDateTime().date())[0:4])
        roznica = do_data - od_data

        data_lista = []
        if roznica < 0:
            msgbox = QMessageBox(QMessageBox.Information, "Ostrzeżenie:",
                                 f"Data początkowa ({od_data}) jest większa od daty końcowej ({do_data})")
            msgbox.exec_()
            return False
        else:
            for rok in range(int(od_data), int(do_data) + 1):
                data_lista.append(rok)

        powiat_name = self.dockwidget.model3d_powiat_cmbbx.currentText()
        if not powiat_name:
            self.no_area_specified_warning()
            return
        teryt_powiat = self.dockwidget.regionFetch.getTerytByPowiatName(powiat_name)
        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie powiatowej paczki modelu 3D dla {powiat_name}({teryt_powiat})',
                                            level=Qgis.Info, duration=10)
        task = DownloadModel3dTask(
            description=f'Pobieranie powiatowej paczki modelu 3D dla {powiat_name}({teryt_powiat})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt_powiat=teryt_powiat,
            teryt_wojewodztwo=teryt_powiat[0:2],
            standard=standard,
            data_lista=data_lista,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # region EGiB WFS
    def wfs_egib_selected_pow_btn_clicked(self):
        """Pobiera paczkę danych WFS EGiB dla powiatów"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        powiatName = self.dockwidget.wfs_egib_powiat_cmbbx.currentText()
        if not powiatName:
            self.no_area_specified_warning()
            return
        teryt = self.dockwidget.regionFetch.getTerytByPowiatName(powiatName)
        self.iface.messageBar().pushMessage(
            "Informacja",
            f'Pobieranie powiatowej paczki WFS dla EGiB {powiatName}({teryt})',
            level=Qgis.Info,
            duration=10
        )
        if not hasattr(self, 'egib_wfs_dict'):
            setattr(self, 'egib_wfs_dict', egib_api.get_wfs_egib_dict())
        if not self.egib_wfs_dict:
            return

        task = DownloadWfsEgibTask(
            description=f'Pobieranie powiatowej paczki WFS dla EGiB {powiatName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt=teryt,
            wfs_url=self.egib_wfs_dict.get(teryt),
            iface=self.iface,
            plugin_dir=self.plugin_dir
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    def radioButton_powiaty_egib_excel(self):
        if self.dockwidget.powiat_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(True)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(True)

    def radioButton_wojewodztwa_egib_excel(self):
        if self.dockwidget.wojew_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(False)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(True)

    def radioButton_kraj_egib_excel(self):
        if self.dockwidget.kraj_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(False)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(False)

    def egib_excel_selected_btn_clicked(self):
        """Pobiera excela z Zestawieniami Zbiorczymi EGiB"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return
        egib_excel_zakres_danych = ''

        if self.dockwidget.powiat_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'powiat'
        elif self.dockwidget.wojew_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'wojew'
        elif self.dockwidget.kraj_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'kraj'

        rok = self.dockwidget.egib_excel_dateEdit_comboBox.currentText()
        powiatName = self.dockwidget.egib_excel_powiat_cmbbx.currentText()
        if not powiatName:
            self.no_area_specified_warning()
            return
        teryt_powiat = self.dockwidget.regionFetch.getTerytByPowiatName(powiatName)

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie danych z Zestawień Zbiorczych EGiB dla {powiatName}({teryt_powiat}) z roku {rok}',
                                            level=Qgis.Info, duration=10)

        task = DownloadEgibExcelTask(
            description=f'Pobieranie danych z Zestawień Zbiorczych EGiB dla {powiatName}({teryt_powiat}) z roku {rok}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            egib_excel_zakres_danych=egib_excel_zakres_danych,
            rok=rok,
            teryt_powiat=teryt_powiat,
            teryt_wojewodztwo=teryt_powiat[0:2],
            iface=self.iface
        )

        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # region opracowania tyflologiczne
    def tyflologiczne_selected_btn_clicked(self):
        """Pobiera opracowania tyflologiczne"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return

        if self.dockwidget.radioButton_atlas_swiata.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_SWIATA/atlas_swiata_2012_sitodruk.ZIP"
            atlas_rodzaj = f'atlas świata sitodruk z roku 2012'
        elif self.dockwidget.radioButton_atlas_europa.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_EUROPY/atlas_europy_2006_puchnacy.ZIP"
            atlas_rodzaj = f'atlas Europy puchnący z roku 2006'
        elif self.dockwidget.radioButton_atlas_polska_1.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2020_termoformowanie.ZIP"
            atlas_rodzaj = f'atlas Polski termoformowanie z roku 2020'
        elif self.dockwidget.radioButton_atlas_polska_2.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2004_puchnacy.ZIP"
            atlas_rodzaj = f'atlas Polski puchnący z roku 2004'
        elif self.dockwidget.radioButton_atlas_polska_3.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2020_puchnacy.ZIP"
            atlas_rodzaj = f'atlas Polski puchnący z roku 2020'
        elif self.dockwidget.radioButton_atlas_warszawa.isChecked():
            self.url = "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_WARSZAWY/atlas_warszawy_2005_puchnacy.ZIP"
            atlas_rodzaj = f'atlas Warszawy puchnący z roku 2005'

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie danych z Opracowań Tyflologicznych - {atlas_rodzaj}',
                                            level=Qgis.Info, duration=10)

        task = DownloadOpracowaniaTyflologiczneTask(
            description=f'Pobieranie danych z Opracowań Tyflologicznych - {atlas_rodzaj}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            url=self.url,
            iface=self.iface
        )

        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # region podstawowa osnowa geodezyjna
    def osnowa_selected_btn_clicked(self):
        """Pobiera podstawową osnowę geodezyjną"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        typ = []
        if self.dockwidget.osnowa_H_rdbtn.isChecked() and not self.dockwidget.osnowa_XY_rdbtn.isChecked():
            typ = ["H"]
        elif self.dockwidget.osnowa_XY_rdbtn.isChecked() and not self.dockwidget.osnowa_H_rdbtn.isChecked():
            typ = ["XY"]
        elif self.dockwidget.osnowa_H_rdbtn.isChecked() and self.dockwidget.osnowa_XY_rdbtn.isChecked():
            typ = ["H", "XY"]
        elif not self.dockwidget.osnowa_H_rdbtn.isChecked() and not self.dockwidget.osnowa_XY_rdbtn.isChecked():
            msgbox = QMessageBox(QMessageBox.Information, "Ostrzeżenie:",
                                 f"Nie wybrano typu osnowy")
            msgbox.exec_()
            return False

        powiat_name = self.dockwidget.osnowa_powiat_cmbbx.currentText()
        if not powiat_name:
            self.no_area_specified_warning()
            return
        teryt_powiat = self.dockwidget.regionFetch.getTerytByPowiatName(powiat_name)

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie danych z Podstawowej Osnowy Geodezyjnej - dla powiatu {powiat_name} ({teryt_powiat}) - typ osnowy {typ}',
                                            level=Qgis.Info, duration=10)

        task = DownloadOsnowaTask(
            description=f'Pobieranie danych z Podstawowej Osnowy Geodezyjnej - dla powiatu {powiat_name} ({teryt_powiat})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt_powiat=teryt_powiat,
            typ=typ,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # region areotriangulacja
    def aerotriangulacja_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Aerotriangulacji przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.aerotriangulacja_mapLayerComboBox.currentLayer()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=1000)

            # zablokowanie klawisza pobierania
            self.dockwidget.aerotriangulacja_fromLayer_btn.setEnabled(False)

            aerotriangulacjaList = []
            for point in points:
                subList = aerotriangulacja_api.getAerotriangulacjaListbyPoint1992(point=point)
                if subList:
                    aerotriangulacjaList.extend(subList)
                else:
                    bledy += 1
            # print("list: ", aerotriangulacjaList)
            self.filterAerotriangulacjaListAndRunTask(aerotriangulacjaList)
            # print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.aerotriangulacja_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadAerotriangulacjiForSinglePoint(self, point):
        """Pobiera Aerotriangulacji dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        aerotriangulacjaList = aerotriangulacja_api.getAerotriangulacjaListbyPoint1992(point=point1992)

        self.filterAerotriangulacjaListAndRunTask(aerotriangulacjaList)

    def filterAerotriangulacjaListAndRunTask(self, aerotriangulacjaList):
        """Filtruje listę dostępnych plików Areotriangulacji i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        aerotriangulacjaList = list(set(aerotriangulacjaList))
        # print("po 'set'", len(aerotriangulacjaList))

        # wyswietl komunikat pytanie
        if len(aerotriangulacjaList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     aerotriangulacjaList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie areotriangulacji
                task = DownloadAerotriangulacjaTask(description='Pobieranie plików danych o aerotriangulacji',
                                                    aerotriangulacjaList=aerotriangulacjaList,
                                                    folder=self.dockwidget.folder_fileWidget.filePath(),
                                                    iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasAerotriangulacja_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Aerotriangulacji z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.aerotriangulacjaClickTool)
        self.downloadAerotriangulacjiForSinglePoint(point)

    # endregion

    # region linie mozaikowania
    def linie_mozaikowania_arch_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Linii Mozaikowania przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.linie_mozaikowania_mapLayerComboBox.currentLayer()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=1000)

            # zablokowanie klawisza pobierania
            self.dockwidget.linie_mozaikowania_arch_fromLayer_btn.setEnabled(False)

            mozaikaList = []
            for point in points:
                subList = mozaika_api.getMozaikaListbyPoint1992(point=point)
                if subList:
                    mozaikaList.extend(subList)
                else:
                    bledy += 1

            # print("list: ", mozaikaList)
            self.filterMozaikaListAndRunTask(mozaikaList)
            # print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.linie_mozaikowania_arch_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadMozaikaForSinglePoint(self, point):
        """Pobiera Linie Mozaikowania dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        mozaikaList = mozaika_api.getMozaikaListbyPoint1992(point=point1992)

        self.filterMozaikaListAndRunTask(mozaikaList)

    def filterMozaikaListAndRunTask(self, mozaikaList):
        """Filtruje listę dostępnych plików Linii Mozaikowania i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        mozaikaList = list(set(mozaikaList))
        # print("po 'set'", len(mozaikaList))

        # wyswietl komunikat pytanie
        if len(mozaikaList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                 "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     mozaikaList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie linii mozaikowania
                task = DownloadMozaikaTask(description='Pobieranie plików danych o linii mozaikowania',
                                           mozaikaList=mozaikaList,
                                           folder=self.dockwidget.folder_fileWidget.filePath(),
                                           iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasMozaika_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Linii Mozaikowania z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.mozaikaClickTool)
        self.downloadMozaikaForSinglePoint(point)

    # endregion

    # region wizualizacja kartograficzna BDOT10k
    def wizualizacja_karto_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Wizualizacji kartograficznej BDOT10k przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.wizualizacja_karto_mapLayerComboBox.currentLayer()
        skala_10000 = True if self.dockwidget.wizualizacja_karto_10_rdbtn.isChecked() else False

        if layer:
            points = self.pointsFromVectorLayer(layer, density=500)

            # zablokowanie klawisza pobierania
            self.dockwidget.wizualizacja_karto_fromLayer_btn.setEnabled(False)

            wizKartoList = []
            for point in points:
                subList = wizualizacja_karto_api.getWizualizacjaKartoListbyPoint1992(point=point,
                                                                                     skala_10000=skala_10000)
                if subList:
                    wizKartoList.extend(subList)
                else:
                    bledy += 1
            # print("list: ", wizKartoList)
            self.filterWizualizacjaKartoListAndRunTask(wizKartoList)
            # print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.wizualizacja_karto_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadWizualizacjaKartoForSinglePoint(self, point):
        """Pobiera Wizualizacji Kartograficznej BDOT10k dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        skala_10000 = True if self.dockwidget.wizualizacja_karto_10_rdbtn.isChecked() else False
        wizKartoList = wizualizacja_karto_api.getWizualizacjaKartoListbyPoint1992(point=point1992,
                                                                                  skala_10000=skala_10000)
        self.filterWizualizacjaKartoListAndRunTask(wizKartoList)

    def filterWizualizacjaKartoListAndRunTask(self, wizKartoList):
        """Filtruje listę dostępnych plików Wizualizacji Kartograficznej BDOT10k i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        wizKartoList = list(set(wizKartoList))
        # print("po 'set'", len(mozaikaList))

        # wyswietl komunikat pytanie
        if len(wizKartoList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                 "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     wizKartoList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie wizualizacji kartograficznej BDOT10k
                task = DownloadWizKartoTask(description='Pobieranie danych pdf o wizualizacji kartograficznej BDOT10k',
                                            wizKartoList=wizKartoList,
                                            folder=self.dockwidget.folder_fileWidget.filePath(),
                                            iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasWizualizacja_karto_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Wizualizacji Kartograficznej BDOT10k z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.wizualizacja_kartoClickTool)
        self.downloadWizualizacjaKartoForSinglePoint(point)

    # endregion

    # region archiwalne kartoteki osnów geodezyjnych
    def osnowa_arch_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Archiwalnych kartotek osnów geodezyjnych przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.osnowa_arch_mapLayerComboBox.currentLayer()
        katalog_niwelacyjne = True if self.dockwidget.niwelacyjne_rdbtn.isChecked() else False

        if layer:
            points = self.pointsFromVectorLayer(layer, density=500)

            # zablokowanie klawisza pobierania
            self.dockwidget.osnowa_arch_fromLayer_btn.setEnabled(False)

            kartotekiOsnowList = []
            for point in points:
                subList = kartoteki_osnow_api.getKartotekiOsnowListbyPoint1992(point=point,
                                                                               katalog_niwelacyjne=katalog_niwelacyjne)
                if subList:
                    kartotekiOsnowList.extend(subList)
                else:
                    bledy += 1
            # print("list: ", wizKartoList)
            self.filterKartotekiOsnowListAndRunTask(kartotekiOsnowList)
            # print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.osnowa_arch_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadKartotekiOsnowForSinglePoint(self, point):
        """Pobiera Archiwalne kartoteki osnów geodezyjnych dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        katalog_niwelacyjne = True if self.dockwidget.niwelacyjne_rdbtn.isChecked() else False
        kartotekiOsnowList = kartoteki_osnow_api.getKartotekiOsnowListbyPoint1992(point=point1992,
                                                                                  katalog_niwelacyjne=katalog_niwelacyjne)
        self.filterKartotekiOsnowListAndRunTask(kartotekiOsnowList)

    def filterKartotekiOsnowListAndRunTask(self, kartotekiOsnowList):
        """Filtruje listę dostępnych plików Archiwalnych kartotek osnów i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        kartotekiOsnowList = list(set(kartotekiOsnowList))
        # print("po 'set'", len(mozaikaList))

        # wyswietl komunikat pytanie
        if len(kartotekiOsnowList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat",
                                 "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     kartotekiOsnowList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie wizualizacji kartograficznej BDOT10k
                task = DownloadKartotekiOsnowTask(
                    description='Pobieranie danych o archiwalnych kartotekach osnów geodezyjnych',
                    kartotekiOsnowList=kartotekiOsnowList,
                    folder=self.dockwidget.folder_fileWidget.filePath(),
                    iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def canvasKartoteki_osnow_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Archiwalnych kartotek osnów geodezyjnych z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.kartoteki_osnowClickTool)
        self.downloadKartotekiOsnowForSinglePoint(point)

    # endregion

    # region dane archiwalne BDOT10k
    def archiwalne_bdot_selected_powiat_btn_clicked(self):
        """Pobiera paczkę archiwalnych danych BDOT10k dla powiatów"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        format_danych = None

        if self.dockwidget.archiwalne_bdot_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.archiwalne_bdot_shp_rdbtn.isChecked():
            format_danych = "SHP"

        powiatName = self.dockwidget.archiwalne_powiat_cmbbx.currentText()
        teryt = self.dockwidget.regionFetch.getTerytByPowiatName(powiatName)
        rok = self.dockwidget.archiwalne_bdot_dateEdit_comboBox.currentText()

        self.iface.messageBar().pushMessage("Informacja",
                                            f'Pobieranie powiatowej paczki danych archiwalnych BDOT10k dla {powiatName}({teryt}) z roku {rok}',
                                            level=Qgis.Info, duration=10)

        task = DownloadArchiwalnyBdotTask(
            description=f'Pobieranie powiatowej paczki danych archiwalnych BDOT10k dla {powiatName}({teryt}) z roku {rok}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            format_danych=format_danych,
            teryt=teryt,
            rok=rok,
            iface=self.iface
        )
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage('runtask')

    # endregion

    # region zdjęcia lotnicze
    def zdjecia_lotnicze_fromLayer_btn_clicked(self):
        """Kliknięcie plawisza pobierania Zdjęć Lotniczych przez wybór warstwą wektorową"""

        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.zdjecia_lotnicze_mapLayerComboBox.currentLayer()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=1000)

            # zablokowanie klawisza pobierania
            self.dockwidget.zdjecia_lotnicze_fromLayer_btn.setEnabled(False)

            zdjeciaLotniczeList = []
            for point in points:
                subList = zdjecia_lotnicze_api.getZdjeciaLotniczeListbyPoint1992(point=point)
                if subList:
                    zdjeciaLotniczeList.extend(subList)
                else:
                    bledy += 1
            # print("list: ", zdjeciaLotniczeList)
            self.filterZdjeciaLotniczeListAndRunTask(zdjeciaLotniczeList)
            # print("%d zapytań się nie powiodło" % bledy)

            # odblokowanie klawisza pobierania
            self.dockwidget.zdjecia_lotnicze_fromLayer_btn.setEnabled(True)

        else:
            self.iface.messageBar().pushWarning("Ostrzeżenie:",
                                                'Nie wskazano warstwy wektorowej')

    def downloadZdjeciaLotniczeForSinglePoint(self, point):
        """Pobiera Zdjecia Lotnicze dla pojedynczego punktu"""
        point1992 = utils.pointTo2180(point=point,
                                      sourceCrs=QgsProject.instance().crs(),
                                      project=QgsProject.instance())
        zdjeciaLotniczeList = zdjecia_lotnicze_api.getZdjeciaLotniczeListbyPoint1992(point=point1992)

        self.filterZdjeciaLotniczeListAndRunTask(zdjeciaLotniczeList)

    def filterZdjeciaLotniczeListAndRunTask(self, zdjeciaLotniczeList):
        """Filtruje listę dostępnych plików Zdjęć Lotniczych i uruchamia wątek QgsTask"""

        # usuwanie duplikatów
        zdjeciaLotniczeList = list(set(zdjeciaLotniczeList))
        # print("po 'set'", len(zdjeciaLotniczeList))
        zdjeciaLotniczeList = self.filterzdjeciaLotniczeList(zdjeciaLotniczeList)

        zdjeciaLotniczeList_brak_url = []
        for zdj in zdjeciaLotniczeList:
            if zdj.url == "brak zdjęcia":
                zdjeciaLotniczeList_brak_url.append(zdj)
                zdjeciaLotniczeList.remove(zdj)

        # wyswietl komunikat pytanie
        if len(zdjeciaLotniczeList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     zdjeciaLotniczeList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie zdjęć lotniczych
                task = DownloadZdjeciaLotniczeTask(description='Pobieranie plików zdjęć lotniczych',
                                                   zdjeciaLotniczeList=zdjeciaLotniczeList,
                                                   zdjeciaLotniczeList_brak_url=zdjeciaLotniczeList_brak_url,
                                                   folder=self.dockwidget.folder_fileWidget.filePath(),
                                                   iface=self.iface)
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def filterzdjeciaLotniczeList(self, zdjeciaLotniczeList):
        """Filtruje listę zdjęć lotniczych"""

        if self.dockwidget.zdjecia_lotnicze_filter_groupBox.isChecked():
            if not (self.dockwidget.zdjecia_lotnicze_kolor_cmbbx.currentText() == 'wszystkie'):
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.kolor == self.dockwidget.zdjecia_lotnicze_kolor_cmbbx.currentText()]
            if self.dockwidget.zdjecia_lotnicze_from_dateTimeEdit.date():
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.dataNalotu >= self.dockwidget.zdjecia_lotnicze_from_dateTimeEdit.dateTime().toPyDateTime().date()]
            if self.dockwidget.zdjecia_lotnicze_to_dateTimeEdit.date():
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.dataNalotu <= self.dockwidget.zdjecia_lotnicze_to_dateTimeEdit.dateTime().toPyDateTime().date()]
            if not (self.dockwidget.zdjecia_lotnicze_source_cmbbx.currentText() == 'wszystkie'):
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.zrodloDanych == self.dockwidget.zdjecia_lotnicze_source_cmbbx.currentText()]

        return zdjeciaLotniczeList

    def canvasZdjecia_lotnicze_clicked(self, point):
        """Zdarzenie kliknięcia przez wybór Aerotriangulacji z mapy"""
        """point - QgsPointXY"""
        self.canvas.unsetMapTool(self.zdjecia_lotniczeClickTool)
        self.downloadZdjeciaLotniczeForSinglePoint(point)

    # endregion

    def pointsFromVectorLayer(self, layer, density=1000):
        """tworzy punkty do zapytań na podstawie warstwy wektorowej"""
        # zamiana na 1992
        if layer.crs() != QgsCoordinateReferenceSystem('EPSG:2180'):
            params = {
                'INPUT': layer,
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
                'OPERATION': None,
                'OUTPUT': 'memory:TEMPORARY_OUTPUT'}
            proc = processing.run("qgis:reprojectlayer", params)
            layer = proc['OUTPUT']
            print('d ', proc)
            print('e ', type(layer), layer)
        if layer.geometryType() == QgsWkbTypes.LineGeometry:
            points = utils.createPointsFromLineLayer(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            points = utils.createPointsFromPolygon(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PointGeometry:
            points = utils.createPointsFromPointLayer(layer)

        return points

    def filterDataListAndRunTask(self, dataList, dataType):
        """Filtruje listę dostępnych plików

        dataType = 'LAS' - dane LAS/LAZ
        dataType = 'ORTOFOTO' - dane OROTOFOTO/CIR
        dataType = 'NMT' - dane NMT/NMPT
        dataType = 'REFLECTANCE' - dane REFLECTANCE

        i uruchamia wątek QgsTask"""

        if dataType == 'LAS':
            filterFunction = self.filterLasList
            downloadTask = DownloadLasTask
            isNmpt = None
        if dataType == 'ORTOFOTO':
            filterFunction = self.filterOrtoList
            downloadTask = DownloadOrtofotoTask
            isNmpt = None
        if dataType == 'NMT':
            filterFunction = self.filterNmtList
            downloadTask = DownloadNmtTask
            isNmpt = True if self.dockwidget.nmpt_rdbtn.isChecked() else False
        if dataType == 'REFLECTANCE':
            pass

        # usuwanie duplikatów
        dataList = list(set(dataList))

        # filtrowanie
        dataList = filterFunction(dataList)

        # wyswietl komunikat pytanie
        if len(dataList) == 0:
            msgbox = QMessageBox(QMessageBox.Information, "Komunikat", "Nie znaleniono danych spełniających kryteria")
            msgbox.exec_()
            return
        else:
            msgbox = QMessageBox(QMessageBox.Question,
                                 "Potwierdź pobieranie",
                                 "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     dataList))
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                # pobieranie plików
                task = downloadTask(f'Pobieranie plików {dataType}',
                                    dataList,
                                    self.dockwidget.folder_fileWidget.filePath())
                QgsApplication.taskManager().addTask(task)
                QgsMessageLog.logMessage('runtask')

    def capture_btn_clicked(self, clickTool):
        """Kliknięcie plawisza pobierania danych przez wybór z mapy"""
        path = self.dockwidget.folder_fileWidget.filePath()
        if self.checkSavePath(path):
            # pobrano ściezkę
            self.canvas.setMapTool(clickTool)

    def checkSavePath(self, path):
        """Sprawdza czy ścieżka jest poprawna i zwraca Boolean"""
        if not path:
            self.iface.messageBar().pushCritical("Ostrzeżenie:",
                                                 'Nie wskazano wskazano miejsca zapisu plików')
            return False
        elif not os.path.exists(path):
            self.iface.messageBar().pushCritical("Ostrzeżenie:",
                                                 'Wskazano nieistniejącą ścieżkę do zapisu plików')
            return False
        else:
            return True

    def no_area_specified_warning(self):
        self.iface.messageBar().pushWarning(
            "Ostrzeżenie:", 'Nie wskazano obszaru.')
