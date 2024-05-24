# -*- coding: utf-8 -*-


import os
import warnings

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QRegExp
from qgis._core import Qgis, QgsMapLayerProxyModel

from PyQt5.QtGui import QRegExpValidator
from qgis.gui import QgsFileWidget

from .constants import ADMINISTRATIVE_UNITS_OBJECTS, DOUBLE_VALIDATOR_OBJECTS, DATA_TIME_OBJECTS, MAP_LAYER_COMBOBOXES, \
    VOIVODESHIP_COMBOBOXES, YEARS_COMBOBOXES
from .wfs import WfsFetch

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pobieracz_danych_gugik_base.ui'))


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
        for base_combo, combo_items in ADMINISTRATIVE_UNITS_OBJECTS.items():
            fetch_func, dependent_combo = combo_items
            combo_obj = getattr(self, base_combo)
            combo_obj.currentTextChanged.connect(
                lambda _, func=fetch_func, combo=dependent_combo: self.setup_administrative_unit_obj(func, combo))
        self.wfs_service_cmbbx.currentTextChanged.connect(self.wfs_service_cmbbx_currentTextChanged)

    def fill_services(self):
        self.wfs_service_cmbbx.clear()
        self.wfs_service_cmbbx.addItems(self.wfsFetch.wfsServiceDict.keys())

    def setup_validators(self):
        double_validator = QRegExpValidator(QRegExp("[0-9.]*"))
        for obj in DOUBLE_VALIDATOR_OBJECTS:
            getattr(self, obj).setValidator(double_validator)

    def setup_dates(self):
        for obj in DATA_TIME_OBJECTS:
            getattr(self, obj).setAllowNull(False)

    def setup_vector_layers_filters(self):
        vector_layers_filter = self.vector_layers_filter()
        for obj in MAP_LAYER_COMBOBOXES:
            getattr(self, obj).setFilters(vector_layers_filter)

    def fill_voivodeships(self):
        voivodeships_ids = self.regionFetch.wojewodztwoDict.keys()
        voivodeships_names = self.regionFetch.wojewodztwoDict.values()
        for obj_name in VOIVODESHIP_COMBOBOXES:
            obj = getattr(self, obj_name)
            obj.clear()
            obj.addItems(voivodeships_names)
            for idx, val in enumerate(voivodeships_ids):
                obj.setItemData(idx, val)
            obj.setCurrentIndex(-1)

    def fill_years(self):
        for obj, years in YEARS_COMBOBOXES.items():
            getattr(self, obj).addItems(years)

    def setup_administrative_unit_obj(self, func, dependent_combo):
        combo_obj = getattr(self, dependent_combo)
        unit_data = self.sender().currentData()
        if not unit_data:
            return
        combo_obj.clear()
        unit_dict = getattr(self.regionFetch, func)(unit_data)
        combo_obj.addItems(unit_dict.values())
        for idx, val in enumerate(unit_dict.keys()):
            combo_obj.setItemData(idx, val)
        combo_obj.setCurrentIndex(-1)

    def wfs_service_cmbbx_currentTextChanged(self, text):
        self.wfs_layer_cmbbx.clear()
        typenamesDict = self.wfsFetch.getTypenamesByServiceName(text)
        self.wfs_layer_cmbbx.addItems(sorted(list(typenamesDict.keys()), reverse=True))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
