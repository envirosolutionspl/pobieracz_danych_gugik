# -*- coding: utf-8 -*-


import os
import warnings
from functools import partial

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QRegExp
from qgis._core import Qgis, QgsMapLayerProxyModel

from PyQt5.QtGui import QRegExpValidator
from qgis.gui import QgsFileWidget
from .wfs import WfsFetch

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pobieracz_danych_gugik_base.ui'))


double_validator_obj = [
    'orto_pixelFrom_lineEdit',
    'orto_pixelTo_lineEdit',
    'nmt_pixelFrom_lineEdit',
    'nmt_pixelTo_lineEdit',
    'nmt_mhFrom_lineEdit',
    'nmt_mhTo_lineEdit',
    'las_pixelFrom_lineEdit',
    'las_pixelTo_lineEdit',
    'las_mhFrom_lineEdit',
    'las_mhTo_lineEdit',
    'reflectance_pixelFrom_lineEdit',
    'reflectance_pixelTo_lineEdit'
]

date_time_obj = [
    'orto_from_dateTimeEdit',
    'orto_to_dateTimeEdit',
    'nmt_from_dateTimeEdit',
    'nmt_to_dateTimeEdit',
    'las_from_dateTimeEdit',
    'las_to_dateTimeEdit',
    'reflectance_from_dateTimeEdit',
    'reflectance_to_dateTimeEdit',
    'zdjecia_lotnicze_from_dateTimeEdit',
    'zdjecia_lotnicze_to_dateTimeEdit'
]

map_layer_comboboxes = [
    'orto_mapLayerComboBox',
    'nmt_mapLayerComboBox',
    'las_mapLayerComboBox',
    'reflectance_mapLayerComboBox',
    'wfs_mapLayerComboBox',
    'aerotriangulacja_mapLayerComboBox',
    'linie_mozaikowania_mapLayerComboBox',
    'wizualizacja_karto_mapLayerComboBox',
    'osnowa_arch_mapLayerComboBox',
    'zdjecia_lotnicze_mapLayerComboBox'
]

voivodeship_comboboxes = [
    'wojewodztwo_cmbbx',
    'bdoo_wojewodztwo_cmbbx',
    'prg_wojewodztwo_cmbbx',
    'model3d_wojewodztwo_cmbbx',
    'wfs_egib_wojewodztwo_cmbbx',
    'egib_excel_wojewodztwo_cmbbx',
    'osnowa_wojewodztwo_cmbbx',
    'archiwalne_wojewodztwo_cmbbx'
]

administrative_units_obj = {
    'wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'powiat_cmbbx'),
    'prg_powiat_cmbbx': ('get_gmina_by_teryt', 'prg_gmina_cmbbx'),
    'prg_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'prg_powiat_cmbbx'),
    'model3d_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'model3d_powiat_cmbbx'),
    'wfs_egib_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'wfs_egib_powiat_cmbbx'),
    'egib_excel_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'egib_excel_powiat_cmbbx'),
    'osnowa_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'osnowa_powiat_cmbbx'),
    'archiwalne_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'archiwalne_powiat_cmbbx'),
}

years_comboboxes = {
    'bdoo_dateEdit_comboBox': ['2022', '2021', '2015'],
    'egib_excel_dateEdit_comboBox': ['2022', '2021', '2020'],
    'archiwalne_bdot_dateEdit_comboBox': ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
}


class PobieraczDanychDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    @staticmethod
    def vector_layers_filter():
        if Qgis.versionInt() >= 33400:
            return Qgis.LayerFilters(
                Qgis.LayerFilter.PolygonLayer | Qgis.LayerFilter.LineLayer | Qgis.LayerFilter.PointLayer
            )
        else:
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            return QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer

    def __init__(self, regionFetch, parent=None):
        """Constructor."""
        super(PobieraczDanychDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.folder_fileWidget.setStorageMode(QgsFileWidget.GetDirectory)
        self.regionFetch = regionFetch
        self.wfsFetch = WfsFetch()
        self.setup_dialog()

    def setup_dialog(self):
        self.setup_validators()
        self.setup_dates()
        self.setup_vector_layers_filters()
        self.fill_voivodeships()
        self.fill_services()
        self.fill_years()
        self.setup_signals()

    def setup_signals(self):
        for base_combo, combo_items in administrative_units_obj.items():
            fetch_func, dependent_combo = combo_items
            getattr(self, base_combo).currentTextChanged.connect(
                partial(self.setup_administrative_unit_obj, fetch_func, dependent_combo))
        self.wfs_service_cmbbx.currentTextChanged.connect(self.wfs_service_cmbbx_currentTextChanged)

    def fill_services(self):
        self.wfs_service_cmbbx.clear()
        self.wfs_service_cmbbx.addItems(self.wfsFetch.wfsServiceDict.keys())

    def setup_validators(self):
        double_validator = QRegExpValidator(QRegExp("[0-9.]*"))
        for obj in double_validator_obj:
            getattr(self, obj).setValidator(double_validator)

    def setup_dates(self):
        for obj in date_time_obj:
            getattr(self, obj).setAllowNull(False)

    def setup_vector_layers_filters(self):
        vector_layers_filter = self.vector_layers_filter()
        for obj in map_layer_comboboxes:
            getattr(self, obj).setFilters(vector_layers_filter)

    def fill_voivodeships(self):
        voivodeships_ids = self.regionFetch.wojewodztwoDict.keys()
        voivodeships_names = self.regionFetch.wojewodztwoDict.values()
        for obj_name in voivodeship_comboboxes:
            obj = getattr(self, obj_name)
            obj.clear()
            obj.addItems(voivodeships_names)
            for idx, val in enumerate(voivodeships_ids):
                obj.setItemData(idx, val)
            obj.setCurrentIndex(-1)

    def fill_years(self):
        for obj, years in years_comboboxes.items():
            getattr(self, obj).addItems(years)

    def setup_administrative_unit_obj(self, func, dependent_combo):
        combo_obj = getattr(self, dependent_combo)
        unit_data = self.sender().currentData()
        if not unit_data:
            return
        combo_obj.clear()
        unit_dict = getattr(self.regionFetch, func)(unit_data)
        for idx, val in enumerate(unit_dict.keys()):
            combo_obj.setItemData(idx, val)
        combo_obj.addItems(unit_dict.values())
        combo_obj.setCurrentIndex(-1)

    def wfs_service_cmbbx_currentTextChanged(self, text):
        self.wfs_layer_cmbbx.clear()
        typenamesDict = self.wfsFetch.getTypenamesByServiceName(text)
        self.wfs_layer_cmbbx.addItems(sorted(list(typenamesDict.keys()), reverse=True))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
