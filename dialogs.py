# -*- coding: utf-8 -*-


import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from qgis.gui import QgsFileWidget
from qgis.core import QgsMapLayerProxyModel
from .uldk import RegionFetch
from .wfs import WfsFetch

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pobieracz_danych_gugik_base.ui'))


class PobieraczDanychDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(PobieraczDanychDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.folder_fileWidget.setStorageMode(QgsFileWidget.GetDirectory)
        # orto
        self.orto_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.orto_pixelFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.orto_pixelTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.orto_from_dateTimeEdit.setAllowNull(False)
        self.orto_to_dateTimeEdit.setAllowNull(False)
        # nmt/nmpt
        self.nmt_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.nmt_pixelFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.nmt_pixelTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.nmt_mhFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.nmt_mhTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.nmt_from_dateTimeEdit.setAllowNull(False)
        self.nmt_to_dateTimeEdit.setAllowNull(False)
        # las
        self.las_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.las_pixelFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.las_pixelTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.las_mhFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.las_mhTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.las_from_dateTimeEdit.setAllowNull(False)
        self.las_to_dateTimeEdit.setAllowNull(False)
        # intensywnosc
        self.reflectance_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.reflectance_pixelFrom_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.reflectance_pixelTo_lineEdit.setValidator(QRegExpValidator(QRegExp("[0-9.]*")))
        self.reflectance_from_dateTimeEdit.setAllowNull(False)
        self.reflectance_to_dateTimeEdit.setAllowNull(False)
        # bdot10k/BDOO
        self.powiatDict = {}
        self.regionFetch = RegionFetch()
        self.wojewodztwo_cmbbx.currentTextChanged.connect(self.wojewodztwo_cmbbx_currentTextChanged)
        wojewodztwa = list(self.regionFetch.wojewodztwoDict.keys())
        self.wojewodztwo_cmbbx.addItems(wojewodztwa)

        # bdoo
        self.bdoo_wojewodztwo_cmbbx.addItems(wojewodztwa)
        rokDict_bdoo = ['2022', '2021', '2015']
        self.bdoo_dateEdit_comboBox.addItems(rokDict_bdoo)

        # PRG
        self.powiatDict_prg = {}
        self.gminaDict_prg = {}
        self.prg_wojewodztwo_cmbbx.currentTextChanged.connect(self.prg_wojewodztwo_cmbbx_currentTextChanged)
        self.prg_powiat_cmbbx.currentTextChanged.connect(self.prg_powiat_cmbbx_currentTextChanged)
        prg_wojewodztwa = list(self.regionFetch.wojewodztwoDict.keys())
        self.prg_wojewodztwo_cmbbx.addItems(prg_wojewodztwa)

        # modele 3D
        self.powiatDict_model3d = {}

        self.model3d_wojewodztwo_cmbbx.currentTextChanged.connect(self.model3d_wojewodztwo_cmbbx_currentTextChanged)
        model3d_wojewodztwa = list(self.regionFetch.wojewodztwoDict.keys())
        self.model3d_wojewodztwo_cmbbx.addItems(model3d_wojewodztwa)

        #WFS
        self.wfs_mapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)

        self.wfsFetch = WfsFetch()
        self.wfs_service_cmbbx.clear()
        self.wfs_layer_cmbbx.clear()
        self.wfs_service_cmbbx.currentTextChanged.connect(self.wfs_service_cmbbx_currentTextChanged)
        uslugi = list(self.wfsFetch.wfsServiceDict.keys())
        self.wfs_service_cmbbx.addItems(uslugi)

        #WFS EGiB
        self.powiatDict_wfs_egib = {}
        # self.powiatDict_wfs_egib = self.regionFetch.getAllPowiatNameWithTeryt()
        # self.wfs_egib_powiat_cmbbx.addItems(list(self.powiatDict_wfs_egib.values()))

        self.wfs_egib_wojewodztwo_cmbbx.currentTextChanged.connect(self.wfs_wojewodztwo_cmbbx_currentTextChanged)
        wfs_egib_wojewodztwa = list(self.regionFetch.wojewodztwoDict.keys())
        self.wfs_egib_wojewodztwo_cmbbx.addItems(wfs_egib_wojewodztwa)

        # zestawienia zbiorcze EGiB
        self.powiatDict_egib_excel = {}
        self.egib_excel_wojewodztwo_cmbbx.currentTextChanged.connect(self.egib_excel_wojewodztwo_cmbbx_currentTextChanged)
        egib_excel_wojewodztwo = list(self.regionFetch.wojewodztwoDict.keys())
        self.egib_excel_wojewodztwo_cmbbx.addItems(egib_excel_wojewodztwo)

        rokDict_egib_excel = ['2022', '2021', '2020']
        self.egib_excel_dateEdit_comboBox.addItems(rokDict_egib_excel)

        # podstawowa osnowa geodezyjna
        self.powiatDict_osnowa = {}
        self.osnowa_wojewodztwo_cmbbx.currentTextChanged.connect(self.osnowa_wojewodztwo_cmbbx_currentTextChanged)
        osnowa_wojewodztwa = list(self.regionFetch.wojewodztwoDict.keys())
        self.osnowa_wojewodztwo_cmbbx.addItems(osnowa_wojewodztwa)


        # areotriangulacja
        self.aerotriangulacja_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)

        # linie mozaikowania
        self.linie_mozaikowania_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)

        # wizualizacja karograficzna BDOT10k
        self.wizualizacja_karto_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)

        # archiwalne kartoteki osnów
        self.osnowa_arch_mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)

        # bdot10k/BDOO
        self.powiatArchiwalneBDOTDict = {}
        self.archiwalne_wojewodztwo_cmbbx.currentTextChanged.connect(self.archiwalne_wojewodztwo_cmbbx_currentTextChanged)
        wojewodztwaArchiwalneBDOT = list(self.regionFetch.wojewodztwoDict.keys())
        self.archiwalne_wojewodztwo_cmbbx.addItems(wojewodztwaArchiwalneBDOT)

        rokDict_archiwalne_bdot10k = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
        self.archiwalne_bdot_dateEdit_comboBox.addItems(rokDict_archiwalne_bdot10k)

        # zdjęcia lotnicze
        self.zdjecia_lotnicze_mapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.zdjecia_lotnicze_from_dateTimeEdit.setAllowNull(False)
        self.zdjecia_lotnicze_to_dateTimeEdit.setAllowNull(False)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.powiat_cmbbx.clear()
        self.powiatDict = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.powiat_cmbbx.addItems(list(self.powiatDict.keys()))

    def wfs_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.wfs_egib_powiat_cmbbx.clear()
        self.powiatDict_wfs_egib = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.wfs_egib_powiat_cmbbx.addItems(list(self.powiatDict_wfs_egib.keys()))

    def wfs_service_cmbbx_currentTextChanged(self, text):
        self.wfs_layer_cmbbx.clear()
        typenamesDict = self.wfsFetch.getTypenamesByServiceName(text)
        self.wfs_layer_cmbbx.addItems(sorted(list(typenamesDict.keys()), reverse=True))

    def prg_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.prg_powiat_cmbbx.clear()
        self.powiatDict_prg = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.prg_powiat_cmbbx.addItems(list(self.powiatDict_prg.keys()))

    def prg_powiat_cmbbx_currentTextChanged(self, text):
        self.prg_gmina_cmbbx.clear()
        self.gminaDict_prg = self.regionFetch.getGminaDictByPowiatName(text)
        self.prg_gmina_cmbbx.addItems(list(self.gminaDict_prg.keys()))

    def model3d_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.model3d_powiat_cmbbx.clear()
        self.powiatDict_model3d = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.model3d_powiat_cmbbx.addItems(list(self.powiatDict_model3d.keys()))

    def egib_excel_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.egib_excel_powiat_cmbbx.clear()
        self.powiatDict_egib_excel = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.egib_excel_powiat_cmbbx.addItems(list(self.powiatDict_egib_excel.keys()))

    def osnowa_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.osnowa_powiat_cmbbx.clear()
        self.powiatDict_osnowa = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.osnowa_powiat_cmbbx.addItems(list(self.powiatDict_osnowa.keys()))

    def archiwalne_wojewodztwo_cmbbx_currentTextChanged(self, text):
        self.archiwalne_powiat_cmbbx.clear()
        self.powiatArchiwalneBDOTDict = self.regionFetch.getPowiatDictByWojewodztwoName(text)
        self.archiwalne_powiat_cmbbx.addItems(list(self.powiatArchiwalneBDOTDict.keys()))

