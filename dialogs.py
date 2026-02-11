# -*- coding: utf-8 -*-


import os
import warnings
from .utils import VersionUtils
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QT_VERSION_STR, pyqtSignal

# różne importy w zależności od wersji Qt
if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
    from qgis.PyQt.QtCore import QRegularExpression
    from qgis.PyQt.QtGui import QRegularExpressionValidator
else: 
    from qgis.PyQt.QtCore import QRegExp
    from qgis.PyQt.QtGui import QRegExpValidator

from qgis._core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsFileWidget

from .constants import ADMINISTRATIVE_UNITS_OBJECTS, DOUBLE_VALIDATOR_OBJECTS, DATA_TIME_OBJECTS, MAP_LAYER_COMBOBOXES, \
    VOIVODESHIP_COMBOBOXES, YEARS_COMBOBOXES, WFS_URL_MAPPING
from .wfs import WfsFetch

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pobieracz_danych_gugik_base.ui'))


class PobieraczDanychDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    @staticmethod
    def vectorLayersFilter():
        if Qgis.versionInt() >= 33400:
            return Qgis.LayerFilters(
                Qgis.LayerFilter.PolygonLayer | Qgis.LayerFilter.LineLayer | Qgis.LayerFilter.PointLayer
            )
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
        self.setupValidators()
        self.setupDates()
        self.setupVectorLayersFilters()
        self.fillVoivodeships()
        self.fillServices()
        self.fillWfsServicesData()
        self.fillYears()
        self.setupSignals()

    def setupSignals(self):
        for base_combo, combo_items in ADMINISTRATIVE_UNITS_OBJECTS.items():
            fetch_func, dependent_combo = combo_items
            combo_obj = getattr(self, base_combo)
            combo_obj.currentTextChanged.connect(
                lambda _, func=fetch_func, combo=dependent_combo: self.setupAdministrativeUnitObj(func, combo))
        self.wfs_service_cmbbx.currentTextChanged.connect(self.wfsServiceCmbbxCurrentTextChanged)

    def fillServices(self):
        self.wfs_service_cmbbx.clear()
        self.wfs_service_cmbbx.addItems(WFS_URL_MAPPING.keys())

    def fillWfsServicesData(self):
        aktualna_warstwa = self.wfs_service_cmbbx.currentText()
        self.wfsServiceCmbbxCurrentTextChanged(aktualna_warstwa)

    def setupValidators(self):
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            double_validator = QRegularExpressionValidator(QRegularExpression("[0-9.]*"))
        else:
            double_validator = QRegExpValidator(QRegExp("[0-9.]*"))
        for obj in DOUBLE_VALIDATOR_OBJECTS:
            getattr(self, obj).setValidator(double_validator)

    def setupDates(self):
        for obj in DATA_TIME_OBJECTS:
            getattr(self, obj).setAllowNull(False)

    def setupVectorLayersFilters(self):
        vector_layers_filter = self.vectorLayersFilter()
        for obj in MAP_LAYER_COMBOBOXES:
            getattr(self, obj).setFilters(vector_layers_filter)

    def fillVoivodeships(self):
        voivodeships_ids = self.regionFetch.wojewodztwoDict.keys()
        voivodeships_names = self.regionFetch.wojewodztwoDict.values()
        for obj_name in VOIVODESHIP_COMBOBOXES:
            obj = getattr(self, obj_name)
            obj.clear()
            obj.addItems(voivodeships_names)
            for idx, val in enumerate(voivodeships_ids):
                obj.setItemData(idx, val)
            obj.setCurrentIndex(-1)

    def fillYears(self):
        for obj, years in YEARS_COMBOBOXES.items():
            getattr(self, obj).addItems(years)

    def setupAdministrativeUnitObj(self, func, dependent_combo):
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

    def wfsServiceCmbbxCurrentTextChanged(self, text):
        self.wfs_layer_cmbbx.clear()
        typenamesDict = self.wfsFetch.getTypenamesByServiceName(text)
        self.wfs_layer_cmbbx.addItems(sorted(list(typenamesDict.keys()), reverse=True))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
