# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QT_VERSION_STR
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QMessageBox, QDialog
from qgis.gui import *
from qgis.core import *

from .qgis_feed import QgisFeedDialog, QgisFeed
from .constants import (GROUPBOXES_VISIBILITY_MAP, PRG_URL, 
                        OPRACOWANIA_TYFLOGICZNE_MAPPING, CURRENT_YEAR,
                        MIN_YEAR_BUILDINGS_3D, OKRES_DOSTEPNYCH_DANYCH_LOD, 
                        CRS, WFS_FILTER_KEYS, WIZUALIZACJA_KARTO_CONFIG)

from . import PLUGIN_VERSION as plugin_version
from . import PLUGIN_NAME as plugin_name

from .uldk import RegionFetch
from .tasks import (
    DownloadOrtofotoTask, DownloadNmtTask, DownloadNmptTask, DownloadLasTask, DownloadReflectanceTask,
    DownloadBdotTask, DownloadBdooTask, DownloadWfsTask, DownloadWfsEgibTask, DownloadPrngTask,
    DownloadPrgTask, DownloadModel3dTask, DownloadEgibExcelTask, DownloadOpracowaniaTyflologiczneTask,
    DownloadOsnowaTask, DownloadAerotriangulacjaTask, DownloadMozaikaTask, DownloadWizKartoTask,
    DownloadKartotekiOsnowTask, DownloadArchiwalnyBdotTask, DownloadZdjeciaLotniczeTask, DownloadMesh3dTask,
    DownloadTrees3dTask
)
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .dialogs import PobieraczDanychDockWidget
from .qgis_feed import QgisFeedDialog
import os.path

from . import ortofoto_api, nmt_api, nmpt_api, las_api, reflectance_api, aerotriangulacja_api, \
    mozaika_api, wizualizacja_karto_api, kartoteki_osnow_api, zdjecia_lotnicze_api, mesh3d_api

from .egib_api import EgibAPI
from .utils import LayersUtils, FilterUtils, MessageUtils, ServiceAPI, ParsingUtils, VersionUtils
from .wfs.utils import filterWfsFeaturesByUsersInput


class PobieraczDanychGugik:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.settings = QgsSettings()
        if Qgis.QGIS_VERSION_INT >= 31000:
            from .qgis_feed import QgisFeed
            self.selected_industry = self.settings.value("selected_industry", None)
            show_dialog = self.settings.value("showDialog", True, type=bool)

            if self.selected_industry is None and show_dialog:
                self.showBranchSelectionDialog()

            select_indust_session = self.settings.value('selected_industry')

            self.feed = QgisFeed(selected_industry=select_indust_session, plugin_name=plugin_name)
            self.feed.initFeed()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.task_mngr = QgsApplication.taskManager()

        # Declare instance attributes
        self.actions = []
        self.menu = u'&EnviroSolutions'
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, 'EnviroSolutions')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'EnviroSolutions')
            self.toolbar.setObjectName(u'EnviroSolutions')

        self.pluginIsActive = False
        self.dockwidget = None

        self.project = QgsProject.instance()

        # klasy wykorzystywanych modułów
        self.egib_api = EgibAPI()
        self.service_api = ServiceAPI(self)

        self.canvas = self.iface.mapCanvas()
        # out click tool will emit a QgsPoint on every click
        self.ortoClickTool = QgsMapToolEmitPoint(self.canvas)
        self.ortoClickTool.canvasClicked.connect(self.canvasOrtoClicked)
        self.nmtClickTool = QgsMapToolEmitPoint(self.canvas)
        self.nmtClickTool.canvasClicked.connect(self.canvasNmtClicked)
        self.lasClickTool = QgsMapToolEmitPoint(self.canvas)
        self.lasClickTool.canvasClicked.connect(self.canvasLasClicked)
        self.reflectanceClickTool = QgsMapToolEmitPoint(self.canvas)
        self.reflectanceClickTool.canvasClicked.connect(self.canvasReflectanceClicked)
        self.wfsClickTool = QgsMapToolEmitPoint(self.canvas)
        self.wfsClickTool.canvasClicked.connect(self.canvasWfsClicked)
        self.aerotriangulacjaClickTool = QgsMapToolEmitPoint(self.canvas)
        self.aerotriangulacjaClickTool.canvasClicked.connect(self.canvasAerotriangulacjaClicked)
        self.mesh3dClickTool = QgsMapToolEmitPoint(self.canvas)
        self.mesh3dClickTool.canvasClicked.connect(self.canvasMeshClicked)
        self.mozaikaClickTool = QgsMapToolEmitPoint(self.canvas)
        self.mozaikaClickTool.canvasClicked.connect(self.canvasMozaikaClicked)
        self.wizualizacja_kartoClickTool = QgsMapToolEmitPoint(self.canvas)
        self.wizualizacja_kartoClickTool.canvasClicked.connect(self.canvasWizualizacjaKartoClicked)
        self.kartoteki_osnowClickTool = QgsMapToolEmitPoint(self.canvas)
        self.kartoteki_osnowClickTool.canvasClicked.connect(self.canvasKartotekiOsnowClicked)
        self.zdjecia_lotniczeClickTool = QgsMapToolEmitPoint(self.canvas)
        self.zdjecia_lotniczeClickTool.canvasClicked.connect(self.canvasZdjeciaLotniczeClicked)
        success = self.service_api.checkInternetConnection()
        if success:
            self.regionFetch = RegionFetch()

        # --------------------------------------------------------------------------

    def addAction(
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

        icon_path = os.path.join(
            self.plugin_dir,
            'img',
            'pobieracz_logo.svg'
        )
        self.addAction(
            icon_path,
            text=u'Pobieracz Danych GUGiK',
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        if self.dockwidget is None:
            return
        # zwijanie groupboxow przy wylaczeniu
        self.changeGroupboxesVisibility()

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        self.dockwidget = None

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


    def showBranchSelectionDialog(self):
        self.qgisfeed_dialog = QgisFeedDialog()

        if self.qgisfeed_dialog.exec() == QDialog.Accepted:
            self.selected_branch = self.qgisfeed_dialog.comboBox.currentText()

            #Zapis w QGIS3.ini
            self.settings.setValue("selected_industry", self.selected_branch)
            self.settings.setValue("showDialog", False)

    # --------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""
        if self.pluginIsActive:
            return
        connection = self.service_api.checkInternetConnection()
        if not connection:
            self.pluginIsActive = False
            return

        if self.dockwidget is None:
            if not hasattr(self, 'regionFetch'):
                self.regionFetch = RegionFetch()
            self.dockwidget = PobieraczDanychDockWidget(self.regionFetch)
            self.pluginIsActive = True

        # Eventy
        for rdbtn in GROUPBOXES_VISIBILITY_MAP.keys():
            obj = getattr(self.dockwidget, rdbtn)
            obj.toggled.connect(self.changeGroupboxesVisibility)
            obj.toggled.emit(True)

        self.dockwidget.wfs_capture_btn.clicked.connect(lambda: self.captureBtnClicked(self.wfsClickTool))
        self.dockwidget.wfs_fromLayer_btn.clicked.connect(self.wfsFromLayerBtnClicked)

        self.dockwidget.wfs_service_cmbbx.currentTextChanged.connect(self.toggle_ortho_filters_visibility)
        self.toggle_ortho_filters_visibility()

        self.dockwidget.orto_capture_btn.clicked.connect(lambda: self.captureBtnClicked(self.ortoClickTool))
        self.dockwidget.orto_fromLayer_btn.clicked.connect(self.ortoFromLayerBtnClicked)

        self.dockwidget.nmt_capture_btn.clicked.connect(lambda: self.captureBtnClicked(self.nmtClickTool))
        self.dockwidget.nmt_fromLayer_btn.clicked.connect(self.nmtFromLayerBtnClicked)

        self.dockwidget.las_capture_btn.clicked.connect(lambda: self.captureBtnClicked(self.lasClickTool))
        self.dockwidget.las_fromLayer_btn.clicked.connect(self.lasFromLayerBtnClicked)

        self.dockwidget.reflectance_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.reflectanceClickTool))
        self.dockwidget.reflectance_fromLayer_btn.clicked.connect(self.reflectanceFromLayerBtnClicked)

        self.dockwidget.bdot_selected_powiat_btn.clicked.connect(self.bdotSelectedPowiatBtnClicked)
        self.dockwidget.bdot_selected_woj_btn.clicked.connect(self.bdotSelectedWojBtnClicked)
        self.dockwidget.bdot_polska_btn.clicked.connect(self.bdotPolskaBtnClicked)

        self.dockwidget.bdoo_selected_woj_btn.clicked.connect(self.bdooSelectedWojBtnClicked)
        self.dockwidget.bdoo_selected_polska_btn.clicked.connect(self.bdooSelectedPolskaBtnClicked)

        self.dockwidget.prng_selected_btn.clicked.connect(self.prngSelectedBtnClicked)

        self.dockwidget.prg_gml_rdbtn.toggled.connect(self.radioButtonStatePRG)
        self.dockwidget.radioButton_adres_powiat.toggled.connect(self.radioButtonPowiatyPRG)
        self.dockwidget.radioButton_adres_wojew.toggled.connect(self.radioButtonWojewodztwaPRG)
        self.dockwidget.radioButton_jend_admin_wojew.toggled.connect(self.radioButtonWojewodztwaPRG)
        self.dockwidget.radioButton_adres_kraj.toggled.connect(self.radioButtonKrajPRG)
        self.dockwidget.radioButton_granice_spec.toggled.connect(self.radioButtonKrajPRG)
        self.dockwidget.radioButton_jedn_admin_kraj.toggled.connect(self.radioButtonKrajPRG)
        self.dockwidget.radioButton_adres_gmin.toggled.connect(self.radioButtonGminaPRG)
        self.dockwidget.prg_selected_btn.clicked.connect(self.prgSelectedBtnClicked)

        self.dockwidget.model3d_selected_powiat_btn.clicked.connect(self.model3dSelectedPowiatBtnClicked)
        self.dockwidget.drzewa3d_selected_powiat_btn.clicked.connect(self.invokeTask3dTrees)

        self.dockwidget.wfs_egib_selected_pow_btn.clicked.connect(self.wfsEgibSelectedPowBtnClicked)

        self.dockwidget.powiat_egib_excel_rdbtn.toggled.connect(self.radioButtonPowiatyEgibExcel)
        self.dockwidget.wojew_egib_excel_rdbtn.toggled.connect(self.radioButtonWojewodztwaEgibExcel)
        self.dockwidget.kraj_egib_excel_rdbtn.toggled.connect(self.radioButtonKrajEgibExcel)
        self.dockwidget.egib_excel_selected_btn.clicked.connect(self.egibExcelSelectedBtnClicked)

        self.dockwidget.tyflologiczne_selected_btn.clicked.connect(self.tyflologiczneSelectedBtnClicked)

        self.dockwidget.osnowa_selected_btn.clicked.connect(self.osnowaSelectedBtnClicked)

        self.dockwidget.aerotriangulacja_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.aerotriangulacjaClickTool))
        self.dockwidget.aerotriangulacja_fromLayer_btn.clicked.connect(self.aerotriangulacjaFromLayerBtnClicked)

        self.dockwidget.mesh3d_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.mesh3dClickTool))
        self.dockwidget.mesh3d_fromLayer_btn.clicked.connect(self.mesh3dFromLayerBtnClicked)

        self.dockwidget.linie_mozaikowania_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.mozaikaClickTool))
        self.dockwidget.linie_mozaikowania_arch_fromLayer_btn.clicked.connect(
            self.linieMozaikowaniaArchFromLayerBtnClicked)

        self.dockwidget.wizualizacja_karto_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.wizualizacja_kartoClickTool))
        self.dockwidget.wizualizacja_karto_fromLayer_btn.clicked.connect(
            self.wizualizacjaKartoFromLayerBtnClicked)

        self.dockwidget.osnowa_arch_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.kartoteki_osnowClickTool))
        self.dockwidget.osnowa_arch_fromLayer_btn.clicked.connect(self.osnowaArchFromLayerBtnClicked)

        self.dockwidget.archiwalne_bdot_selected_powiat_btn.clicked.connect(
            self.archiwalneBdotSelectedPowiatBtnClicked)

        self.dockwidget.zdjecia_lotnicze_capture_btn.clicked.connect(
            lambda: self.captureBtnClicked(self.zdjecia_lotniczeClickTool))
        self.dockwidget.zdjecia_lotnicze_fromLayer_btn.clicked.connect(self.zdjeciaLotniczeFromLayerBtnClicked)

        # connect to provide cleanup on closing of dockwidget
        self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        self.dockwidget.folder_fileWidget.setFilePath(
            self.settings.value("pobieracz_danych_gugik/settings/defaultPath", ""))
        self.dockwidget.folder_fileWidget.fileChanged.connect(
            lambda: self.settings.setValue(
                "pobieracz_danych_gugik/settings/defaultPath",
                self.dockwidget.folder_fileWidget.filePath())
        )
        # informacje o wersji
        self.dockwidget.setWindowTitle('%s %s' % (plugin_name, plugin_version))
        self.dockwidget.lbl_pluginVersion.setText('%s %s' % (plugin_name, plugin_version))

        # show the dockwidget
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockwidget)
        else:
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

        self.dockwidget.label_55.setMargin(5)
        self.dockwidget.show()

    def changeGroupboxesVisibility(self):
        if self.dockwidget is None:
            return

        for rdbtn, groupboxes in GROUPBOXES_VISIBILITY_MAP.items():
            visible = getattr(self.dockwidget, rdbtn).isChecked()
            for groupbox in groupboxes:
                getattr(self.dockwidget, groupbox).setVisible(visible)
                getattr(self.dockwidget, groupbox).setCollapsed(visible)

    def wfsFromLayerBtnClicked(self):
        """Kliknięcie klawisza pobierania danych WFS przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            MessageUtils.pushWarning(self.iface, 'Nie wskazano warstwy wektorowej')
    def test(self):
        print('test')

    def downloadWfsForLayer(self, layer):
        """Pobiera dane WFS """
        if isinstance(layer, QgsPointXY):
            vp = QgsVectorLayer(f'Point?crs={self.project.crs().authid()}', "vectpoi", "memory")
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(layer))
            dp = vp.dataProvider()
            dp.addFeature(feature)
            layer = vp

        layer1992 = LayersUtils.layerToCrs(layer=layer, dest_crs=CRS)

        skorowidzeLayer = self.dockwidget.wfsFetch.getWfsListbyLayer1992(
            layer=layer1992,
            wfsService=self.dockwidget.wfs_service_cmbbx.currentText(),
            typename=self.dockwidget.wfs_layer_cmbbx.currentText())
        skorowidzeLayer.updatedFields.connect(self.test)
        if skorowidzeLayer.isValid():
            self.project.addMapLayer(skorowidzeLayer)
            features = list(skorowidzeLayer.getFeatures())
            
            service_name = self.dockwidget.wfs_service_cmbbx.currentText().lower()

            if service_name == 'ortofotomapa':

                filters = {}
                # Pobranie parametrów z UI
                fk = WFS_FILTER_KEYS
                filters[fk['COLOR']] = self.dockwidget.wfs_kolor_choice.currentText()
                filters[fk['SOURCE']] = self.dockwidget.wfs_source_choice.currentText()
                filters[fk['CRS']] = self.dockwidget.wfs_crs_choice.currentText()
                filters[fk['PIXEL_FROM']] = self.dockwidget.wfs_pixelFrom_choice.value()
                filters[fk['PIXEL_TO']] = self.dockwidget.wfs_pixelTo_choice.value()

                # Filtracja
                filtered_features = filterWfsFeaturesByUsersInput(features, filters)
            else:
                filtered_features = features

            # Usunięcie duplikatów URL
            urls = []
            seen_urls = set()
            for feat in filtered_features:
                url = feat['url_do_pobrania']
                if url and url not in seen_urls:
                    urls.append(url)
                    seen_urls.add(url)

            # Komunikat
            if len(urls) == 0:
                title = "Komunikat"
                message = "Brak danych spełniających Twoje filtry."
                MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
                LayersUtils.removeLayer(self.project, self.canvas, skorowidzeLayer.id())
                return

            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), "Potwierdź", f"Znaleziono {len(urls)} plików. Pobrać?")
            
            if reply:
                # pobieranie
                self.runWfsTask(urls)
                LayersUtils.removeLayer(self.project, self.canvas, skorowidzeLayer.id())
            else:
                LayersUtils.removeLayer(self.project, self.canvas, skorowidzeLayer.id())

    def toggle_ortho_filters_visibility(self):
        """Pokazuje/ukrywa filtry ortofotomapy w zależności od wybranej usługi"""
        group_box = (
            getattr(self.dockwidget, 'groupWfsOrthoFilters', None)
            or getattr(self.dockwidget, 'groupOrthoFilters', None)
        )

        if not group_box:
            return

        service_name = self.dockwidget.wfs_service_cmbbx.currentText().lower()
        is_ortho = service_name == 'ortofotomapa'

        # enable / disable
        group_box.setEnabled(is_ortho)

        # checkbox w nagłówku
        if hasattr(group_box, 'setChecked'):
            group_box.setChecked(is_ortho)

        # zwijanie / rozwijanie
        if hasattr(group_box, 'setCollapsed'):
            group_box.setCollapsed(not is_ortho)

    def runWfsTask(self, urlList):
        """Filtruje listę dostępnych plików ortofotomap i uruchamia wątek QgsTask"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        task = DownloadWfsTask(description='Pobieranie plików z WFS',
                               urlList=urlList,
                               folder=self.dockwidget.folder_fileWidget.filePath(),
                               iface=self.iface)
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasWfsClicked(self, point):
        """Zdarzenie kliknięcia przez wybór ortofotomapy z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.wfsClickTool)
        self.downloadWfsForLayer(point)

    def downloadWfsFile(self, orto, folder):
        """Pobiera plik z wfs"""
        MessageUtils.pushLogInfo('Rozpoczęto ' + orto.url)
        self.service_api.retreiveFile(url=orto.url, destFolder=folder)

    # endregion

    # region ORTOFOTOMAPA

    def ortoFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania ortofotomapy przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            MessageUtils.pushWarning(self.iface, 'Nie wskazano warstwy wektorowej')

    def downloadOrtoForSinglePoint(self, point):
        """Pobiera ortofotomapę dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        ortoList = ortofoto_api.getOrtoListbyPoint1992(point=point_reprojected)
        self.filterOrtoListAndRunTask(ortoList)

    def filterOrtoListAndRunTask(self, ortoList):
        """Filtruje listę dostępnych plików ortofotomap i uruchamia wątek QgsTask"""
        ortoList = self.filterOrtoList(ortoList)
        if len(ortoList) == 0:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            MessageUtils.pushLogInfo(message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                ortoList)
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)

            if reply:
                # pobieranie
                task = DownloadOrtofotoTask(description='Pobieranie plików ortofotomapy',
                                            ortoList=ortoList,
                                            folder=self.dockwidget.folder_fileWidget.filePath(),
                                            iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasOrtoClicked(self, point):
        """Zdarzenie kliknięcia przez wybór ortofotomapy z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.ortoClickTool)
        self.downloadOrtoForSinglePoint(point)

    def filterOrtoList(self, ortoList):
        """Filtruje listę ortofotomap"""

        if self.dockwidget.orto_filter_groupBox.isChecked():
            if not (self.dockwidget.orto_kolor_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.get('kolor') == self.dockwidget.orto_kolor_cmbbx.currentText()]
            if not (self.dockwidget.orto_crs_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.get('ukladWspolrzednychPoziomych') and orto.get('ukladWspolrzednychPoziomych').split(":")[
                                0] == self.dockwidget.orto_crs_cmbbx.currentText()]
            if self.dockwidget.orto_from_dateTimeEdit.date():
                ortoList = [orto for orto in ortoList if
                            str(orto.get('aktualnosc')) >= str(
                                self.dockwidget.orto_from_dateTimeEdit.dateTime().toPyDateTime().date())]
            if self.dockwidget.orto_to_dateTimeEdit.date():
                ortoList = [orto for orto in ortoList if
                            str(orto.get('aktualnosc')) <= str(
                                self.dockwidget.orto_to_dateTimeEdit.dateTime().toPyDateTime().date())]
            if not (self.dockwidget.orto_source_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.get('zrodloDanych') == self.dockwidget.orto_source_cmbbx.currentText()]
            if not (self.dockwidget.orto_full_cmbbx.currentText() == 'wszystkie'):
                ortoList = [orto for orto in ortoList if
                            orto.get('calyArkuszWyeplnionyTrescia') == self.dockwidget.orto_full_cmbbx.currentText()]
            min_val_pixels = self.dockwidget.orto_pixelFrom_lineEdit.value()
            if min_val_pixels > 0:
                ortoList = [orto for orto in ortoList if
                            ParsingUtils.getSafelyFloat(orto.get('wielkoscPiksela', 0)) >= ParsingUtils.getSafelyFloat(self.dockwidget.orto_pixelFrom_lineEdit.text())]
            if self.dockwidget.orto_pixelTo_lineEdit.text():
                ortoList = [orto for orto in ortoList if
                            ParsingUtils.getSafelyFloat(orto.get('wielkoscPiksela', 0)) <= ParsingUtils.getSafelyFloat(self.dockwidget.orto_pixelTo_lineEdit.text())]

        # ograniczenie tylko do najnowszego
        if self.dockwidget.orto_newest_chkbx.isChecked():
            ortoList = FilterUtils.onlyNewest(ortoList)
            # print(ortoList)
        return ortoList

    def downloadOrtoFile(self, orto, folder):
        """Pobiera plik ortofotomapy"""
        MessageUtils.pushLogInfo('Rozpoczęto ' + orto.url)
        self.service_api.retreiveFile(url=orto.url, destFolder=folder)

    # endregion

    # region NMT/NMPT

    def nmtFromLayerBtnClicked(self):
        """Kliknięcie klawisza pobierania NMT/NMPT przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.nmt_mapLayerComboBox.currentLayer()

        isNmpt = self.dockwidget.nmpt_rdbtn.isChecked()
        isEvrf2007 = self.dockwidget.evrf2007_rdbtn.isChecked()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=200 if isNmpt else 400)

            # zablokowanie klawisza pobierania
            self.dockwidget.nmt_fromLayer_btn.setEnabled(False)

            nmtList = []
            for point in points:

                resp = nmpt_api.getNmptListbyPoint1992(
                    point=point,
                    isEvrf2007=isEvrf2007
                ) if isNmpt else nmt_api.getNmtListbyPoint1992(
                    point=point,
                    isEvrf2007=isEvrf2007
                )
                if resp:
                    nmtList.extend(resp if isNmpt else resp[1])
                else:
                    bledy += 1

            self.filterNmtListAndRunTask(nmtList, isNmpt)
            self.dockwidget.nmt_fromLayer_btn.setEnabled(True)
        else:
            MessageUtils.pushWarning(self.iface, 'Nie wskazano warstwy wektorowej')

    def downloadNmtForSinglePoint(self, point):
        """Pobiera NMT/NMPT dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        isNmpt = self.dockwidget.nmpt_rdbtn.isChecked()
        isEvrf2007 = self.dockwidget.evrf2007_rdbtn.isChecked()
        resp = nmpt_api.getNmptListbyPoint1992(
            point=point_reprojected,
            isEvrf2007=isEvrf2007
        ) if isNmpt else nmt_api.getNmtListbyPoint1992(
            point=point_reprojected,
            isEvrf2007=isEvrf2007
        )

        if resp:
            nmtList = resp if isNmpt else resp[1]
            self.filterNmtListAndRunTask(nmtList, isNmpt)
        else:
            self.iface.messageBar().pushCritical(
                'Błąd pobierania',
                'Nie udało się pobrać danych z serwera.'
            )

    def filterNmtListAndRunTask(self, nmtList, isNmpt):
        """Filtruje listę dostępnych plików NMT/NMPT i uruchamia wątek QgsTask"""
        nmtList = self.filterNmtList(nmtList)
        if not nmtList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            MessageUtils.pushLogInfo(message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                nmtList)
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)

            if reply and isNmpt is False and self.dockwidget.nmt_rdbtn.isChecked():
                # pobieranie NMT
                task = DownloadNmtTask(description='Pobieranie plików NMT',
                                       nmtList=nmtList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       isNmpt=False,
                                       iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

            elif reply and isNmpt is True and self.dockwidget.nmpt_rdbtn.isChecked():
                # pobieranie NMTP
                task = DownloadNmptTask(description='Pobieranie plików NMPT',
                                        nmptList=nmtList,
                                        folder=self.dockwidget.folder_fileWidget.filePath(),
                                        isNmpt=True,
                                        iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasNmtClicked(self, point):
        """Zdarzenie kliknięcia przez wybór NMT/NMPT z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.nmtClickTool)
        self.downloadNmtForSinglePoint(point)

    def filterNmtList(self, nmtList):
        """Filtruje listę NMT/NMPT"""
        # wybór formatu
        if self.dockwidget.arcinfo_rdbtn.isChecked():
            nmtList = [nmt for nmt in nmtList if nmt.get('format') == "ARC/INFO ASCII GRID"]
        elif self.dockwidget.xyz_rdbtn.isChecked():
            nmtList = [nmt for nmt in nmtList if nmt.get('format') == "ASCII XYZ GRID"]

        if self.dockwidget.nmt_filter_groupBox.isChecked():
            if self.dockwidget.nmt_crs_cmbbx.currentText() != 'wszystkie':
                nmtList = [nmt for nmt in nmtList if
                           nmt.get('ukladWspolrzednychPoziomych').split(":")[0] == self.dockwidget.nmt_crs_cmbbx.currentText()]

            if self.dockwidget.nmt_from_dateTimeEdit.date():
                nmtList = [nmt for nmt in nmtList if str(nmt.get('aktualnosc')) >= str(
                    self.dockwidget.nmt_from_dateTimeEdit.dateTime().toPyDateTime().date())]

            if self.dockwidget.nmt_to_dateTimeEdit.date():
                nmtList = [nmt for nmt in nmtList if str(nmt.get('aktualnosc')) <= str(
                    self.dockwidget.nmt_to_dateTimeEdit.dateTime().toPyDateTime().date())]

            if self.dockwidget.nmt_full_cmbbx.currentText() != 'wszystkie':
                nmtList = [nmt for nmt in nmtList if
                           nmt.get('calyArkuszWyeplnionyTrescia') == self.dockwidget.nmt_full_cmbbx.currentText()]

            if self.dockwidget.nmt_pixelFrom_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if ParsingUtils.getSafelyFloat(nmt.get('charakterystykaPrzestrzenna', 0)) >= ParsingUtils.getSafelyFloat(
                    self.dockwidget.nmt_pixelFrom_lineEdit.text())]

            if self.dockwidget.nmt_pixelTo_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if ParsingUtils.getSafelyFloat(nmt.get('charakterystykaPrzestrzenna', 0)) <= ParsingUtils.getSafelyFloat(
                    self.dockwidget.nmt_pixelTo_lineEdit.text())]

            if self.dockwidget.nmt_mhFrom_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           ParsingUtils.getSafelyFloat(nmt.get('bladSredniWysokosci', 0)) >= ParsingUtils.getSafelyFloat(self.dockwidget.nmt_mhFrom_lineEdit.text())]

            if self.dockwidget.nmt_mhTo_lineEdit.text():
                nmtList = [nmt for nmt in nmtList if
                           ParsingUtils.getSafelyFloat(nmt.get('bladSredniWysokosci', 0)) <= ParsingUtils.getSafelyFloat(self.dockwidget.nmt_mhTo_lineEdit.text())]

        # ograniczenie tylko do najnowszego
        if self.dockwidget.nmt_newest_chkbx.isChecked():
            nmtList = FilterUtils.onlyNewest(nmtList)
        return nmtList

    def downloadNmtFile(self, nmt, folder):
        """Pobiera plik NMT/NMPT"""
        MessageUtils.pushLogInfo('Rozpoczęto ' + nmt.url)
        self.service_api.retreiveFile(url=nmt.url, destFolder=folder)

    # endregion

    # region LAS

    def lasFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania LAS przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
                las_list.extend(sub_list)
            self.filterLasListAndRunTask(las_list)
        else:
            MessageUtils.pushWarning(self.iface, 'Nie wskazano warstwy wektorowej')

        # odblokowanie klawisza pobierania
        self.dockwidget.las_fromLayer_btn.setEnabled(True)

    def downloadLasForSinglePoint(self, point):
        """Pobiera LAS dla pojedynczego punktu"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        isEvrf2007 = self.dockwidget.las_evrf2007_rdbtn.isChecked()
        lasList = las_api.getLasListbyPoint1992(
            point=point_reprojected,
            isEvrf2007=isEvrf2007
        )
        self.filterLasListAndRunTask(lasList)

    def filterLasListAndRunTask(self, lasList):
        """Filtruje listę dostępnych plików LAS i uruchamia wątek QgsTask"""
        lasList = self.filterLasList(lasList)
        if not lasList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            MessageUtils.pushLogInfo(message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                lasList)
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)

            if reply:
                # pobieranie LAS
                task = DownloadLasTask(description='Pobieranie plików LAZ',
                                       lasList=lasList,
                                       folder=self.dockwidget.folder_fileWidget.filePath(),
                                       iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasLasClicked(self, point):
        """Zdarzenie kliknięcia przez wybór LAS z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.lasClickTool)
        self.downloadLasForSinglePoint(point)

    def filterLasList(self, lasList):
        """Filtruje listę LAS"""
        if self.dockwidget.las_filter_groupBox.isChecked():
            if not (self.dockwidget.las_crs_cmbbx.currentText() == 'wszystkie'):
                lasList = [las for las in lasList if
                           las.get('ukladWspolrzednychPoziomych').split(":")[0] == self.dockwidget.las_crs_cmbbx.currentText()]
            if self.dockwidget.las_from_dateTimeEdit.date():
                lasList = [las for las in lasList if
                           str(las.get('aktualnosc')) >= str(
                               self.dockwidget.las_from_dateTimeEdit.dateTime().toPyDateTime().date())]
            if self.dockwidget.las_to_dateTimeEdit.date():
                lasList = [las for las in lasList if
                           str(las.get('aktualnosc')) <= str(
                               self.dockwidget.las_to_dateTimeEdit.dateTime().toPyDateTime().date())]
            if not (self.dockwidget.las_full_cmbbx.currentText() == 'wszystkie'):
                lasList = [las for las in lasList if
                           las.get('calyArkuszWyeplnionyTrescia') == self.dockwidget.las_full_cmbbx.currentText()]
            if self.dockwidget.las_pixelFrom_lineEdit.text():
                lasList = [las for las in lasList if
                           ParsingUtils.getSafelyFloat(las.get('charakterystykaPrzestrzenna', 0)) >= ParsingUtils.getSafelyFloat(
                               self.dockwidget.las_pixelFrom_lineEdit.text())]
            if self.dockwidget.las_pixelTo_lineEdit.text():
                lasList = [las for las in lasList if
                           ParsingUtils.getSafelyFloat(las.get('charakterystykaPrzestrzenna', 0)) <= ParsingUtils.getSafelyFloat(
                               self.dockwidget.las_pixelTo_lineEdit.text())]
            if self.dockwidget.las_mhFrom_lineEdit.text():
                lasList = [las for las in lasList if
                           ParsingUtils.getSafelyFloat(las.get('bladSredniWysokosci', 0)) >= ParsingUtils.getSafelyFloat(self.dockwidget.las_mhFrom_lineEdit.text())]
            if self.dockwidget.las_mhTo_lineEdit.text():
                lasList = [las for las in lasList if
                           ParsingUtils.getSafelyFloat(las.get('bladSredniWysokosci', 0)) <= ParsingUtils.getSafelyFloat(self.dockwidget.las_mhTo_lineEdit.text())]

        # ograniczenie tylko do najnowszego
        if self.dockwidget.laz_newest_chkbx.isChecked():
            lasList = FilterUtils.onlyNewest(lasList)

        return lasList


    def downloadLaFile(self, las, folder):
        """Pobiera plik LAS"""
        MessageUtils.pushLogInfo('Rozpoczęto ' + las.url)
        self.service_api.retreiveFile(url=las.url, destFolder=folder)

    # endregion

    # region Reflectance

    def reflectanceFromLayerBtnClicked(self):
        """Kliknięcie klawisza pobierania Intensywności przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            MessageUtils.pushWarning(self.iface, 'Nie wskazano warstwy wektorowej')

    def downloadReflectanceForSinglePoint(self, point):
        """Pobiera Intensywność dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        # zablokowanie klawisza pobierania
        # self.dockwidget.reflectance_capture_btn.setEnabled(False)

        reflectanceList = reflectance_api.getReflectanceListbyPoint1992(point=point_reprojected)
        # print("reflectanceList: ", list(reflectanceList))
        self.filterReflectanceListAndRunTask(reflectanceList)

        # odblokowanie klawisza pobierania
        # self.dockwidget.reflectance_capture_btn.setEnabled(True)

    def filterReflectanceListAndRunTask(self, reflectanceList):
        """Filtruje listę dostępnych plików Intensywności i uruchamia wątek QgsTask"""
        reflectanceList = self.filterReflectanceList(reflectanceList)
        if not reflectanceList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            MessageUtils.pushLogInfo(message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                reflectanceList)
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)

            if reply:
                # pobieranie reflectance
                task = DownloadReflectanceTask(description='Pobieranie plików Obrazów Intensywności',
                                               reflectanceList=reflectanceList,
                                               folder=self.dockwidget.folder_fileWidget.filePath(),
                                               iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasReflectanceClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Intensywności z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.reflectanceClickTool)
        self.downloadReflectanceForSinglePoint(point)

    def filterReflectanceList(self, reflectanceList):
        """Filtruje listę Intensywności"""

        if self.dockwidget.reflectance_filter_groupBox.isChecked():
            if not (self.dockwidget.reflectance_crs_cmbbx.currentText() == 'wszystkie'):
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.get('ukladWspolrzednychPoziomych').split(":")[
                                       0] == self.dockwidget.reflectance_crs_cmbbx.currentText()]
            if self.dockwidget.reflectance_from_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   str(reflectance.get('aktualnosc')) >= str(
                                       self.dockwidget.reflectance_from_dateTimeEdit.dateTime().toPyDateTime().date())]
            if self.dockwidget.reflectance_to_dateTimeEdit.date():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   str(reflectance.get('aktualnosc')) <= str(
                                       self.dockwidget.reflectance_to_dateTimeEdit.dateTime().toPyDateTime().date())]
            if self.dockwidget.reflectance_pixelFrom_lineEdit.text():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   ParsingUtils.getSafelyFloat(reflectance.get('wielkoscPiksela', 0)) >= ParsingUtils.getSafelyFloat(
                                       self.dockwidget.reflectance_pixelFrom_lineEdit.text())]
            if self.dockwidget.reflectance_pixelTo_lineEdit.text():
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   ParsingUtils.getSafelyFloat(reflectance.get('wielkoscPiksela', 0)) <= ParsingUtils.getSafelyFloat(
                                       self.dockwidget.reflectance_pixelTo_lineEdit.text())]
            if not (self.dockwidget.reflectance_source_cmbbx.currentText() == 'wszystkie'):
                reflectanceList = [reflectance for reflectance in reflectanceList if
                                   reflectance.get(
                                       'zrodloDanych') == self.dockwidget.reflectance_source_cmbbx.currentText()]
        return reflectanceList

    def downloadReflectanceFile(self, reflectance, folder):
        """Pobiera plik LAS"""
        MessageUtils.pushLogInfo('Rozpoczęto ' + reflectance.url)
        self.service_api.retreiveFile(url=reflectance.url, destFolder=folder)

    # endregion

    # region BDOT10k
    def bdotSelectedPowiatBtnClicked(self):
        """Pobiera paczkę danych BDOT10k dla powiatu"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
        elif self.dockwidget.bdot_parquet_rdbtn.isChecked():
            self.showUnavailableFormat()
            return

        powiatName = self.dockwidget.powiat_cmbbx.currentText()
        if not powiatName:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.powiat_cmbbx.currentData()

        MessageUtils.pushMessage(self.iface, f'Pobieranie powiatowej paczki BDOT10k dla {powiatName}({teryt})')
        task = DownloadBdotTask(
            description=f'Pobieranie powiatowej paczki BDOT10k dla {powiatName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=2,
            format_danych=format_danych,
            teryt=teryt,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def bdotSelectedWojBtnClicked(self):
        """Pobiera paczkę danych BDOT10k dla województwa"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
        elif self.dockwidget.bdot_parquet_rdbtn.isChecked():
            self.showUnavailableFormat()
            return

        wojewodztwoName = self.dockwidget.wojewodztwo_cmbbx.currentText()
        if not wojewodztwoName:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.wojewodztwo_cmbbx.currentData()
        MessageUtils.pushMessage(self.iface, f'Pobieranie wojewódzkiej paczki BDOT10k dla {wojewodztwoName}({teryt})')
        task = DownloadBdotTask(
            description=f'Pobieranie wojewódzkiej paczki BDOT10k dla {wojewodztwoName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=1,
            format_danych=format_danych,
            teryt=teryt,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def bdotPolskaBtnClicked(self):
        """Pobiera paczkę danych BDOT10k dla całej Polski"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
        elif self.dockwidget.bdot_parquet_rdbtn.isChecked():
            format_danych = 'BDOT10k_GeoParquet'
        MessageUtils.pushMessage(self.iface, 'Pobieranie paczki BDOT10k dla całego kraju')
        task = DownloadBdotTask(
            description='Pobieranie paczki BDOT10k dla całego kraju',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=0,
            format_danych=format_danych,
            teryt=None,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # region BDOO
    def bdooSelectedWojBtnClicked(self):
        """Pobiera paczkę danych BDOO dla województwa"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        rok = self.dockwidget.bdoo_dateEdit_comboBox.currentText()
        wojewodztwoName = self.dockwidget.bdoo_wojewodztwo_cmbbx.currentText()
        if not wojewodztwoName:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.bdoo_wojewodztwo_cmbbx.currentData()

        MessageUtils.pushMessage(self.iface, f'Pobieranie wojewódzkiej paczki BDOO dla {wojewodztwoName}({teryt})')
        task = DownloadBdooTask(
            description=f'Pobieranie wojewódzkiej paczki BDOO dla {wojewodztwoName}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=1,
            rok=rok,
            teryt=teryt,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def bdooSelectedPolskaBtnClicked(self):
        """Pobiera paczkę danych BDOO dla całej Polski"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        rok = self.dockwidget.bdoo_dateEdit_comboBox.currentText()
        MessageUtils.pushMessage(self.iface, 'Pobieranie paczki BDOO dla całego kraju')
        task = DownloadBdooTask(
            description='Pobieranie paczki BDOO dla całego kraju',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            level=0,
            rok=rok,
            teryt=None,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # endregion PRNG
    def prngSelectedBtnClicked(self):
        """Pobiera paczkę danych PRNG"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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

        MessageUtils.pushMessage(self.iface, f'{description} w formacie {format_danych}')
        task = DownloadPrngTask(
            description=f'{description} w formacie {format_danych}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            rodzaj=rodzaj,
            format_danych=format_danych,
            iface=self.iface
        )

        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # endregion

    # endregion PRG
    def radioButtonStatePRG(self):
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

    def radioButtonGminaPRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych gminy"""
        if self.dockwidget.radioButton_adres_gmin.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(True)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(True)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButtonPowiatyPRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych powiatowych"""
        if self.dockwidget.radioButton_adres_powiat.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(True)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButtonWojewodztwaPRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych wojewódzkich"""
        if self.dockwidget.radioButton_adres_wojew.isChecked() or self.dockwidget.radioButton_jend_admin_wojew.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(False)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(True)

    def radioButtonKrajPRG(self):
        """Ustala dostępność rodzaju danych PRG dla danych krajowych"""
        if self.dockwidget.radioButton_adres_kraj.isChecked() or self.dockwidget.radioButton_granice_spec.isChecked() or self.dockwidget.radioButton_jedn_admin_kraj.isChecked():
            self.dockwidget.prg_gmina_cmbbx.setEnabled(False)
            self.dockwidget.prg_powiat_cmbbx.setEnabled(False)
            self.dockwidget.prg_wojewodztwo_cmbbx.setEnabled(False)

    def prgSelectedBtnClicked(self):
        """Pobiera paczkę danych PRG"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            teryt = self.dockwidget.prg_gmina_cmbbx.currentData()
            self.url = f"{PRG_URL}teryt={teryt}&adresy"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z gminy {gmina_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_powiat.isChecked():
            powiat_name = self.dockwidget.prg_powiat_cmbbx.currentText()
            teryt = self.dockwidget.prg_powiat_cmbbx.currentData()
            self.url = f"{PRG_URL}teryt={teryt}&adresy_pow"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z powiatu {powiat_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_wojew.isChecked():
            wojewodztwo_name = self.dockwidget.prg_wojewodztwo_cmbbx.currentText()
            teryt = self.dockwidget.prg_wojewodztwo_cmbbx.currentData()
            self.url = f"{PRG_URL}teryt={teryt}&adresy_woj"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z województwa {wojewodztwo_name} ({teryt})'
        elif self.dockwidget.radioButton_adres_kraj.isChecked():
            self.url = f"{PRG_URL}adresy_zbiorcze_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - adresy z całego kraju - format {prg_format_danych}'
        elif self.dockwidget.radioButton_granice_spec.isChecked():
            self.url = f"{PRG_URL}granice_specjalne_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - granice specjalne z całego kraju - format {prg_format_danych}'
        elif self.dockwidget.radioButton_jend_admin_wojew.isChecked():
            wojewodztwo_name = self.dockwidget.prg_wojewodztwo_cmbbx.currentText()
            teryt = self.dockwidget.prg_wojewodztwo_cmbbx.currentData()
            self.url = f"{PRG_URL}teryt={teryt}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - jednostki administracyjne województwa {wojewodztwo_name} ({teryt})'
        elif self.dockwidget.radioButton_jedn_admin_kraj.isChecked():
            self.url = f"{PRG_URL}jednostki_administracyjne_{prg_format_danych}"
            description = f'Pobieranie danych z Państwowego Rejestru Granic - jednostki administracyjne całego kraju - format {prg_format_danych}'

        if 'None' in self.url:
            self.noAreaSpecifiedWarning()
            return
        MessageUtils.pushMessage(self.iface, description)

        task = DownloadPrgTask(
            description=f'Pobieranie danych z Państwowego Rejestru Granic',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            url=self.url,
            iface=self.iface
        )

        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def invokeTask3dTrees(self):
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False
        powiat_name = self.dockwidget.drzewa3d_powiat_cmbbx.currentText()
        if not powiat_name:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.drzewa3d_powiat_cmbbx.currentData()
        task = DownloadTrees3dTask(
            description=f'Pobieranie powiatowej paczki modelu drzew 3D dla {powiat_name}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt_powiat=teryt,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def model3dPoprawnoscDat(self, dict_od_do_data):
        """
        Funkcja sprawdza warunki dla zakresu dat w których zostały opracowane modele LOD budynków
        """

        od_data = ""
        do_data = ""

        try:
            od_data = int(dict_od_do_data.get("początkowa"))
            do_data = int(dict_od_do_data.get("końcowa"))

            for year in [od_data, do_data]:
                if year not in OKRES_DOSTEPNYCH_DANYCH_LOD:
                    title = "Błąd"
                    message = f"Data {'początkowa' if year == od_data else 'końcowa'} musi być w przedziale od {MIN_YEAR_BUILDINGS_3D} do {CURRENT_YEAR}."
                    MessageUtils.pushMessageBoxCritical(self.iface.mainWindow(), title, message)
                    return False, None, None

        except ValueError as err:
            error_value = err.args[0].split(" ")[-1]
            title = "Błąd"
            message = f"Nieprawidłowy format - data {error_value}."
            MessageUtils.pushMessageBoxCritical(self.iface.mainWindow(), title, message)
            return False, None, None

        else:
            return True, od_data, do_data

    def model3dSelectedPowiatBtnClicked(self):
        """Pobiera paczkę danych modulu 3D budynków"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            title = "Ostrzeżenie"
            message = "Nie wybrano standardu"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return False

        od_data_text = self.dockwidget.model3d_dateEdit_comboBox_1.currentText()
        do_data_text = self.dockwidget.model3d_dateEdit_comboBox_2.currentText()

        dict_od_do_data = {
            "początkowa": od_data_text,
            "końcowa": do_data_text,
        }

        valid, od_data, do_data = self.model3dPoprawnoscDat(dict_od_do_data)

        if not valid:
            return False

        roznica = do_data - od_data

        if roznica < 0:
            title = "Ostrzeżenie"
            message = f"Data początkowa ({od_data}) jest większa od daty końcowej ({do_data})"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return False
        else:
            data_lista = [rok for rok in range(od_data, do_data + 1)]

        powiat_name = self.dockwidget.model3d_powiat_cmbbx.currentText()
        if not powiat_name:
            self.noAreaSpecifiedWarning()
            return
        teryt_powiat = self.dockwidget.model3d_powiat_cmbbx.currentData()
        MessageUtils.pushMessage(self.iface, f'Pobieranie powiatowej paczki modelu 3D dla {powiat_name}({teryt_powiat})')
        task = DownloadModel3dTask(
            description=f'Pobieranie powiatowej paczki modelu 3D dla {powiat_name}({teryt_powiat})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt_powiat=teryt_powiat,
            teryt_wojewodztwo=teryt_powiat[0:2],
            standard=standard,
            data_lista=data_lista,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def egibWfsDownloadTask(self, powiat_name, teryt, wfs_dict, wfs_type):
        """Pobiera paczkę danych WFS dla określonego typu (EGiB i RCiN)"""
        if not hasattr(self, wfs_dict):
            setattr(self, wfs_dict, self.egib_api.getWfsEgibDict())
        if not getattr(self, wfs_dict):
            return
        task = DownloadWfsEgibTask(
            description=f'Pobieranie powiatowej paczki WFS dla {wfs_type} {powiat_name}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(), 
            teryt=teryt,
            wfs_url=getattr(self, wfs_dict).get(teryt),
            iface=self.iface,
            plugin_dir=self.plugin_dir
        )
        QgsApplication.taskManager().addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def wfsEgibSelectedPowBtnClicked(self):
        """Pobiera paczkę danych WFS EGiB dla powiatów"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        powiat_name = self.dockwidget.wfs_egib_powiat_cmbbx.currentText()
        if not powiat_name:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.wfs_egib_powiat_cmbbx.currentData()
        
        MessageUtils.pushMessage(self.iface, f'Pobieranie powiatowej paczki WFS dla EGiB {powiat_name}({teryt})')

        if not hasattr(self, 'egib_wfs_dict'):
            setattr(self, 'egib_wfs_dict', self.egib_api.getWfsEgibDict())
        if not self.egib_wfs_dict:
            return

        task = DownloadWfsEgibTask(
            description=f'Pobieranie powiatowej paczki WFS dla EGiB {powiat_name}({teryt})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt=teryt,
            wfs_url=self.egib_wfs_dict.get(teryt),
            iface=self.iface,
            plugin_dir=self.plugin_dir
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def radioButtonPowiatyEgibExcel(self):
        if self.dockwidget.powiat_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(True)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(True)

    def radioButtonWojewodztwaEgibExcel(self):
        if self.dockwidget.wojew_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(False)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(True)

    def radioButtonKrajEgibExcel(self):
        if self.dockwidget.kraj_egib_excel_rdbtn.isChecked():
            self.dockwidget.egib_excel_powiat_cmbbx.setEnabled(False)
            self.dockwidget.egib_excel_wojewodztwo_cmbbx.setEnabled(False)

    def egibExcelSelectedBtnClicked(self):
        """Pobiera excela z Zestawieniami Zbiorczymi EGiB"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return
        egib_excel_zakres_danych = ''

        rok = self.dockwidget.egib_excel_dateEdit_comboBox.currentText()
        powiatName = self.dockwidget.egib_excel_powiat_cmbbx.currentText()
        wojName = self.dockwidget.egib_excel_wojewodztwo_cmbbx.currentText()
        teryt_powiat = self.dockwidget.egib_excel_powiat_cmbbx.currentData()
        terytWoj = self.dockwidget.egib_excel_wojewodztwo_cmbbx.currentData()

        if self.dockwidget.powiat_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'powiat'
            if not powiatName:
                self.noAreaSpecifiedWarning()
                return
            else:
                MessageUtils.pushMessage(self.iface, f'Pobieranie danych z Zestawień Zbiorczych EGiB dla {powiatName}({teryt_powiat}) z roku {rok}')
        elif self.dockwidget.wojew_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'wojew'
            if not wojName:
                self.noAreaSpecifiedWarning()
                return
            else:
                MessageUtils.pushMessage(self.iface, f'Pobieranie danych z Zestawień Zbiorczych EGiB dla {wojName}({terytWoj}) z roku {rok}')
        elif self.dockwidget.kraj_egib_excel_rdbtn.isChecked():
            egib_excel_zakres_danych = 'kraj'
            MessageUtils.pushMessage(self.iface, f'Pobieranie danych z Zestawień Zbiorczych EGiB dla całej Polski z roku {rok}')

        task = DownloadEgibExcelTask(
            description=f'Pobieranie danych z Zestawień Zbiorczych EGiB dla {powiatName}({teryt_powiat}) z roku {rok}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            egib_excel_zakres_danych=egib_excel_zakres_danych,
            rok=rok,
            teryt_powiat=teryt_powiat,
            teryt_wojewodztwo=terytWoj,
            iface=self.iface
        )

        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # endregion

    # region opracowania tyflologiczne
    def tyflologiczneSelectedBtnClicked(self):
        """Pobiera opracowania tyflologiczne"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return

        for radio_button_name, data in OPRACOWANIA_TYFLOGICZNE_MAPPING.items():
            if getattr(self.dockwidget, radio_button_name).isChecked():
                atlas_url = data["url"]
                atlas_rodzaj = data["rodzaj"]
                break

        MessageUtils.pushMessage(self.iface, f'Pobieranie danych z Opracowań Tyflologicznych - {atlas_rodzaj}')

        task = DownloadOpracowaniaTyflologiczneTask(
            description=f'Pobieranie danych z Opracowań Tyflologicznych - {atlas_rodzaj}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            url=atlas_url,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # endregion

    # region podstawowa osnowa geodezyjna
    def osnowaSelectedBtnClicked(self):
        """Pobiera podstawową osnowę geodezyjną"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            title = "Ostrzeżenie"
            message = "Nie wybrano typu osnowy"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return False

        powiat_name = self.dockwidget.osnowa_powiat_cmbbx.currentText()
        if not powiat_name:
            self.noAreaSpecifiedWarning()
            return
        teryt_powiat = self.dockwidget.osnowa_powiat_cmbbx.currentData()

        MessageUtils.pushMessage(self.iface, f'Pobieranie danych z Podstawowej Osnowy Geodezyjnej - dla powiatu {powiat_name} ({teryt_powiat}) - typ osnowy {typ}')

        task = DownloadOsnowaTask(
            description=f'Pobieranie danych z Podstawowej Osnowy Geodezyjnej - dla powiatu {powiat_name} ({teryt_powiat})',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            teryt_powiat=teryt_powiat,
            typ=typ,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def mesh3dFromLayerBtnClicked(self):
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False
        bledy = 0
        layer = self.dockwidget.mesh3d_mapLayerComboBox.currentLayer()
        if layer:
            points = self.pointsFromVectorLayer(layer, density=1000)
            self.dockwidget.mesh3d_fromLayer_btn.setEnabled(False)
            mesh_objs = []
            for point in points:
                subList = mesh3d_api.getMesh3dListbyPoint1992(point=point)
                if subList:
                    mesh_objs.extend(subList)
                else:
                    bledy += 1
            self.filterMeshListAndRunTask(mesh_objs)
            self.dockwidget.mesh3d_fromLayer_btn.setEnabled(True)
        else:
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def aerotriangulacjaFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania Aerotriangulacji przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def downloadAerotriangulacjiForSinglePoint(self, point):
        """Pobiera Aerotriangulacji dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        aerotriangulacjaList = aerotriangulacja_api.getAerotriangulacjaListbyPoint1992(point=point_reprojected)
        self.filterAerotriangulacjaListAndRunTask(aerotriangulacjaList)

    def downloadMesh3dForSinglePoint(self, point):
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        mesh_objs = mesh3d_api.getMesh3dListbyPoint1992(point=point_reprojected)
        self.filterMeshListAndRunTask(mesh_objs)

    def filterAerotriangulacjaListAndRunTask(self, aerotriangulacjaList):
        """Filtruje listę dostępnych plików Areotriangulacji i uruchamia wątek QgsTask"""
        if not aerotriangulacjaList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = "Znaleziono %d plików spełniających kryteria. Czy chcesz je wszystkie pobrać?" % len(
                                     aerotriangulacjaList)
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                # pobieranie areotriangulacji
                task = DownloadAerotriangulacjaTask(description='Pobieranie plików danych o aerotriangulacji',
                                                    aerotriangulacjaList=aerotriangulacjaList,
                                                    folder=self.dockwidget.folder_fileWidget.filePath(),
                                                    iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def filterMeshListAndRunTask(self, mesh_objs):
        if not mesh_objs:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f'Znaleziono {len(mesh_objs)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?'
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                task = DownloadMesh3dTask(
                    description='Pobieranie plików danych siatkowych modeli 3D',
                    mesh_objs=mesh_objs,
                    folder=self.dockwidget.folder_fileWidget.filePath(),
                    iface=self.iface
                )
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasAerotriangulacjaClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Aerotriangulacji z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.aerotriangulacjaClickTool)
        self.downloadAerotriangulacjiForSinglePoint(point)

    def canvasMeshClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Siatki modeli 3D z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.mesh3dClickTool)
        self.downloadMesh3dForSinglePoint(point)

    def linieMozaikowaniaArchFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania Linii Mozaikowania przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def downloadMozaikaForSinglePoint(self, point):
        """Pobiera Linie Mozaikowania dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        mozaikaList = mozaika_api.getMozaikaListbyPoint1992(point=point_reprojected)

        self.filterMozaikaListAndRunTask(mozaikaList)

    def filterMozaikaListAndRunTask(self, mozaikaList):
        """Filtruje listę dostępnych plików Linii Mozaikowania i uruchamia wątek QgsTask"""
        if not mozaikaList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f"Znaleziono {len(mozaikaList)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?"
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                # pobieranie linii mozaikowania
                task = DownloadMozaikaTask(description='Pobieranie plików danych o linii mozaikowania',
                                           mozaikaList=mozaikaList,
                                           folder=self.dockwidget.folder_fileWidget.filePath(),
                                           iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasMozaikaClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Linii Mozaikowania z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.mozaikaClickTool)
        self.downloadMozaikaForSinglePoint(point)

    # endregion

    # region wizualizacja kartograficzna BDOT10k
    def wizualizacjaKartoFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania Wizualizacji kartograficznej BDOT10k przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.wizualizacja_karto_mapLayerComboBox.currentLayer()
        skala_wartosc = self.getSelectedScaleForWizualizacjaKarto()

        if layer:
            points = self.pointsFromVectorLayer(layer, density=500)

            # zablokowanie klawisza pobierania
            self.dockwidget.wizualizacja_karto_fromLayer_btn.setEnabled(False)

            wizKartoList = []
            for point in points:
                subList = wizualizacja_karto_api.getWizualizacjaKartoListbyPoint1992(
                    point=point,
                    skala=skala_wartosc
                )
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
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def downloadWizualizacjaKartoForSinglePoint(self, point):
        """Pobiera Wizualizacji Kartograficznej BDOT10k dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        skala_wartosc = self.getSelectedScaleForWizualizacjaKarto()
        
        wizKartoList = wizualizacja_karto_api.getWizualizacjaKartoListbyPoint1992(
            point=point_reprojected,
            skala=skala_wartosc
        )
        self.filterWizualizacjaKartoListAndRunTask(wizKartoList)

    def filterWizualizacjaKartoListAndRunTask(self, wizKartoList):
        """Filtruje listę dostępnych plików Wizualizacji Kartograficznej BDOT10k i uruchamia wątek QgsTask"""
        if not wizKartoList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f"Znaleziono {len(wizKartoList)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?"
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                # pobieranie wizualizacji kartograficznej BDOT10k
                task = DownloadWizKartoTask(description='Pobieranie danych pdf o wizualizacji kartograficznej BDOT10k',
                                            wizKartoList=wizKartoList,
                                            folder=self.dockwidget.folder_fileWidget.filePath(),
                                            iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasWizualizacjaKartoClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Wizualizacji Kartograficznej BDOT10k z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.wizualizacja_kartoClickTool)
        self.downloadWizualizacjaKartoForSinglePoint(point)

    def getSelectedScaleForWizualizacjaKarto(self):
        """
        Zwraca klucz dla wybranej skali
        """
        for scale_key, scale_config in WIZUALIZACJA_KARTO_CONFIG.items():
            btn_name = scale_config.get('btn_name')
            if btn_name:
                if hasattr(self.dockwidget, btn_name):
                    button_widget = getattr(self.dockwidget, btn_name)
                    if button_widget.isChecked():
                        return scale_key
                else:
                    MessageUtils.pushLogWarning(
                        f"Nie znaleziono przycisku {btn_name}"
                    )
            else:
                MessageUtils.pushLogWarning(
                   f"Nie znaleziono klucza {scale_key}"
                )
        
        MessageUtils.pushLogWarning(
            "Nie znaleziono wybranej skali. Używam domyślnej wartości 10."
        )
        return list(WIZUALIZACJA_KARTO_CONFIG.keys())[0] # domyślna wartość 10


    # endregion

    # region archiwalne kartoteki osnów geodezyjnych
    def osnowaArchFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania Archiwalnych kartotek osnów geodezyjnych przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        # sprawdzanie ścieżki zapisu
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        bledy = 0
        layer = self.dockwidget.osnowa_arch_mapLayerComboBox.currentLayer()
        is_kronsztad = True if self.dockwidget.niwelacyjne_rdbtn.isChecked() else False

        if layer:
            points = self.pointsFromVectorLayer(layer, density=500)

            # zablokowanie klawisza pobierania
            self.dockwidget.osnowa_arch_fromLayer_btn.setEnabled(False)

            kartotekiOsnowList = []
            for point in points:
                subList = kartoteki_osnow_api.getKartotekiOsnowListbyPoint1992(point=point,
                                                                               is_kronsztad=is_kronsztad)
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
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def downloadKartotekiOsnowForSinglePoint(self, point):
        """Pobiera Archiwalne kartoteki osnów geodezyjnych dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        is_kronsztad = self.dockwidget.niwelacyjne_rdbtn.isChecked()
        kartotekiOsnowList = kartoteki_osnow_api.getKartotekiOsnowListbyPoint1992(
            point=point_reprojected,
            is_kronsztad=is_kronsztad
        )
        self.filterKartotekiOsnowListAndRunTask(kartotekiOsnowList)

    def filterKartotekiOsnowListAndRunTask(self, kartotekiOsnowList):
        """Filtruje listę dostępnych plików Archiwalnych kartotek osnów i uruchamia wątek QgsTask"""
        if not kartotekiOsnowList:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f"Znaleziono {len(kartotekiOsnowList)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?"
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                # pobieranie wizualizacji kartograficznej BDOT10k
                task = DownloadKartotekiOsnowTask(
                    description='Pobieranie danych o archiwalnych kartotekach osnów geodezyjnych',
                    kartotekiOsnowList=kartotekiOsnowList,
                    folder=self.dockwidget.folder_fileWidget.filePath(),
                    iface=self.iface)
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def canvasKartotekiOsnowClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Archiwalnych kartotek osnów geodezyjnych z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.kartoteki_osnowClickTool)
        self.downloadKartotekiOsnowForSinglePoint(point)

    # endregion

    # region dane archiwalne BDOT10k
    def archiwalneBdotSelectedPowiatBtnClicked(self):
        """Pobiera paczkę archiwalnych danych BDOT10k dla powiatów"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        path = self.dockwidget.folder_fileWidget.filePath()
        if not self.checkSavePath(path):
            return False

        format_danych = None

        if self.dockwidget.archiwalne_bdot_gml_rdbtn.isChecked():
            format_danych = "GML"
        elif self.dockwidget.archiwalne_bdot_shp_rdbtn.isChecked():
            format_danych = "SHP"

        powiatName = self.dockwidget.archiwalne_powiat_cmbbx.currentText()
        if not powiatName:
            self.noAreaSpecifiedWarning()
            return
        teryt = self.dockwidget.archiwalne_powiat_cmbbx.currentData()
        rok = self.dockwidget.archiwalne_bdot_dateEdit_comboBox.currentText()

        MessageUtils.pushMessage(self.iface, f'Pobieranie powiatowej paczki danych archiwalnych BDOT10k dla {powiatName}({teryt}) z roku {rok}')

        task = DownloadArchiwalnyBdotTask(
            description=f'Pobieranie powiatowej paczki danych archiwalnych BDOT10k dla {powiatName}({teryt}) z roku {rok}',
            folder=self.dockwidget.folder_fileWidget.filePath(),
            format_danych=format_danych,
            teryt=teryt,
            rok=rok,
            iface=self.iface
        )
        self.task_mngr.addTask(task)
        MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    # endregion

    # region zdjęcia lotnicze
    def zdjeciaLotniczeFromLayerBtnClicked(self):
        """Kliknięcie plawisza pobierania Zdjęć Lotniczych przez wybór warstwą wektorową"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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

            self.filterZdjeciaLotniczeListAndRunTask(zdjeciaLotniczeList)

            # odblokowanie klawisza pobierania
            self.dockwidget.zdjecia_lotnicze_fromLayer_btn.setEnabled(True)

        else:
            MessageUtils.pushWarning(self.iface, "Nie wskazano warstwy wektorowej")

    def downloadZdjeciaLotniczeForSinglePoint(self, point):
        """Pobiera Zdjecia Lotnicze dla pojedynczego punktu"""
        point_reprojected = LayersUtils.pointToCrs(
            point=point,
            project=self.project,
            dest_crs=CRS
        )
        zdjeciaLotniczeList = zdjecia_lotnicze_api.getZdjeciaLotniczeListbyPoint1992(point=point_reprojected)
        self.filterZdjeciaLotniczeListAndRunTask(zdjeciaLotniczeList)

    def filterZdjeciaLotniczeListAndRunTask(self, zdjeciaLotniczeList):
        """Filtruje listę dostępnych plików Zdjęć Lotniczych i uruchamia wątek QgsTask"""
        zdjeciaLotniczeList = self.filterzdjeciaLotniczeList(zdjeciaLotniczeList)
        zdjeciaLotniczeList_brak_url = []
        filtered_list = []
        for zdj in zdjeciaLotniczeList:
            if zdj.get('url') == "brak zdjęcia":
                zdjeciaLotniczeList_brak_url.append(zdj)
            else:
                filtered_list.append(zdj)

        # wyswietl komunikat pytanie
        if not filtered_list:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f"Znaleziono {len(filtered_list)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?"
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                task = DownloadZdjeciaLotniczeTask(
                    description='Pobieranie plików zdjęć lotniczych',
                    zdjeciaLotniczeList=filtered_list,
                    zdjeciaLotniczeList_brak_url=zdjeciaLotniczeList_brak_url,
                    folder=self.dockwidget.folder_fileWidget.filePath(),
                    iface=self.iface
                )
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def filterzdjeciaLotniczeList(self, zdjeciaLotniczeList):
        """Filtruje listę zdjęć lotniczych"""

        if self.dockwidget.zdjecia_lotnicze_filter_groupBox.isChecked():
            if not (self.dockwidget.zdjecia_lotnicze_kolor_cmbbx.currentText() == 'wszystkie'):
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.get(
                                           'przestrzenBarwna') == self.dockwidget.zdjecia_lotnicze_kolor_cmbbx.currentText()]
            if self.dockwidget.zdjecia_lotnicze_from_dateTimeEdit.date():
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       str(zdjecie.get('dataNalotu')) >= str(
                                           self.dockwidget.zdjecia_lotnicze_from_dateTimeEdit.dateTime().toPyDateTime().date())]
            if self.dockwidget.zdjecia_lotnicze_to_dateTimeEdit.date():
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       str(zdjecie.get('dataNalotu')) <= str(
                                           self.dockwidget.zdjecia_lotnicze_to_dateTimeEdit.dateTime().toPyDateTime().date())]
            if not (self.dockwidget.zdjecia_lotnicze_source_cmbbx.currentText() == 'wszystkie'):
                zdjeciaLotniczeList = [zdjecie for zdjecie in zdjeciaLotniczeList if
                                       zdjecie.get(
                                           'zrodloDanych') == self.dockwidget.zdjecia_lotnicze_source_cmbbx.currentText()]

        return zdjeciaLotniczeList

    def canvasZdjeciaLotniczeClicked(self, point):
        """Zdarzenie kliknięcia przez wybór Aerotriangulacji z mapy"""
        """point - QgsPointXY"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
        self.canvas.unsetMapTool(self.zdjecia_lotniczeClickTool)
        self.downloadZdjeciaLotniczeForSinglePoint(point)

    # endregion

    def pointsFromVectorLayer(self, layer, density=1000):
        """tworzy punkty do zapytań na podstawie warstwy wektorowej"""
        # zamiana na 1992
        if layer.crs() != QgsCoordinateReferenceSystem('EPSG:' + CRS):
            layer = LayersUtils.layerToCrs(layer, CRS)

        if layer.geometryType() == QgsWkbTypes.LineGeometry:
            points = LayersUtils.createPointsFromLineLayer(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            points = LayersUtils.createPointsFromPolygon(layer, density)
        elif layer.geometryType() == QgsWkbTypes.PointGeometry:
            points = LayersUtils.createPointsFromPointLayer(layer)

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
            isNmpt = self.dockwidget.nmpt_rdbtn.isChecked()
        if dataType == 'REFLECTANCE':
            pass

        # usuwanie duplikatów
        dataList = list(set(dataList))

        # filtrowanie
        dataList = filterFunction(dataList)

        # wyswietl komunikat pytanie
        if len(dataList) == 0:
            title = "Komunikat"
            message = "Nie znaleniono danych spełniających kryteria"
            MessageUtils.pushMessageBoxInfo(self.iface.mainWindow(), title, message)
            return
        else:
            title = "Potwierdź pobieranie"
            message = f"Znaleziono {len(dataList)} plików spełniających kryteria. Czy chcesz je wszystkie pobrać?"
            reply = MessageUtils.pushMessageBoxYesNo(self.iface.mainWindow(), title, message)
            if reply:
                # pobieranie plików
                task = downloadTask(f'Pobieranie plików {dataType}',
                                    dataList,
                                    self.dockwidget.folder_fileWidget.filePath())
                self.task_mngr.addTask(task)
                MessageUtils.pushLogInfo('Dodano nowe zadanie.')

    def captureBtnClicked(self, clickTool):
        """Kliknięcie klawisza pobierania danych przez wybór z mapy"""
        connection = self.service_api.checkInternetConnection()
        if not connection:
            return
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

    def noAreaSpecifiedWarning(self):
        MessageUtils.pushWarning(self.iface, 'Nie wskazano obszaru')

    def showUnavailableFormat(self):
        MessageUtils.pushWarning(self.iface, "Dla podanego obszaru nie ma dostępnego pliku w formacie GeoParquet")
