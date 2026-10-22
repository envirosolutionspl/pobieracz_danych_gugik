# -*- coding: utf-8 -*-


import os
import re
import configparser
import warnings
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QDir, QEvent, QUrl

from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QRegularExpressionValidator, QDesktopServices

from qgis._core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsFileWidget, QgsCollapsibleGroupBox

from . import PLUGIN_VERSION
from .constants import ADMINISTRATIVE_UNITS_OBJECTS, DOUBLE_VALIDATOR_OBJECTS, DATA_TIME_OBJECTS, MAP_LAYER_COMBOBOXES, \
    VOIVODESHIP_COMBOBOXES, YEARS_COMBOBOXES, WFS_URL_MAPPING, AVAILABLE_DATA_LABELS, \
    FOOTER_LINK_COLORS, FOOTER_LOGOS, HOME_LINK
from .utils import ThemeUtils
from .wfs import WfsFetch

PLUGIN_DIR = os.path.dirname(__file__)

# Prefiks „pdgimg:” używany w url(...) arkusza stylów w pliku .ui.
# Musi być zarejestrowany PRZED setupUi, inaczej QSS nie znajdzie ikon.
QDir.addSearchPath('pdgimg', os.path.join(PLUGIN_DIR, 'images'))

FORM_CLASS, _ = uic.loadUiType(os.path.join(PLUGIN_DIR, 'ui', 'pobieracz_danych_gugik_base.ui'))


class PobieraczDanychDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    @staticmethod
    def vectorLayersFilter():
        if Qgis.versionInt() >= 33400:
            return Qgis.LayerFilters(
                Qgis.LayerFilter.PolygonLayer | Qgis.LayerFilter.LineLayer | Qgis.LayerFilter.PointLayer
            )

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return QgsMapLayerProxyModel.Filter.PolygonLayer | QgsMapLayerProxyModel.Filter.LineLayer | QgsMapLayerProxyModel.Filter.PointLayer

    def __init__(self, regionFetch, parent=None):
        """Constructor."""
        super(PobieraczDanychDockWidget, self).__init__(parent)
        self.setupUi(self)
        self._theme = None
        self._applyTheme()
        self.folder_fileWidget.setStorageMode(QgsFileWidget.StorageMode.GetDirectory)
        self.regionFetch = regionFetch
        self.wfsFetch = WfsFetch()
        self.setup_dialog()
        self._setupLook()

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
        double_validator = QRegularExpressionValidator(QRegularExpression("[0-9.]*"))
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

    # ------------------------------- Wygląd -----------------------------------

    def _setupLook(self):
        """Elementy wyglądu, których nie da się opisać w pliku .ui."""
        self.lbl_pluginVersion.setText('v%s' % PLUGIN_VERSION)
        self.btn_help.clicked.connect(self._openHelp)
        self.btn_close.clicked.connect(self.close)
        self.btn_collapse_all.clicked.connect(self._collapseAllSections)
        for rdbtn in AVAILABLE_DATA_LABELS:
            getattr(self, rdbtn).toggled.connect(self._showAvailableData)
        self._setupTitleBar()

    def _setupTitleBar(self):
        """Nagłówek wtyczki jako pasek tytułu panelu – zamiast systemowego paska z nazwą."""
        self.verticalLayout_main.removeWidget(self.header_frame)
        self.setTitleBarWidget(self.header_frame)

    def _collapseAllSections(self):
        for group_box in self.findChildren(QgsCollapsibleGroupBox):
            group_box.setCollapsed(True)

    def _showAvailableData(self):
        """Pokazuje etykietę „Dostępne dane: …” (tekst w .ui) zaznaczonego sposobu wyszukiwania."""
        for rdbtn, label in AVAILABLE_DATA_LABELS.items():
            getattr(self, label).setVisible(getattr(self, rdbtn).isChecked())

    def _applyTheme(self, force=False):
        """Ustawia właściwość „theme” – kolory zdefiniowane w arkuszu stylów w pliku .ui."""
        theme = 'dark' if ThemeUtils.isDarkTheme() else 'light'
        if theme == self._theme and not force:
            return
        self._theme = theme
        self.setProperty('theme', theme)
        ThemeUtils.repolishAll(self)
        # Linki w stopce: tekst i adres są w .ui, tu zmienia się tylko kolor
        color = FOOTER_LINK_COLORS[theme]
        for lbl in (self.lbl_email, self.lbl_szkolenia):
            lbl.setText(re.sub(r'style="[^"]*"', 'style="text-decoration:underline; color:%s;"' % color, lbl.text()))
        # Logo w stopce: zielone na jasnym tle, białe na ciemnym.
        self._setFooterLogo(FOOTER_LOGOS[theme])

    def _setFooterLogo(self, filename, height=34):
        ThemeUtils.setLogo(self.label_5, filename, height)

    def showEvent(self, event):
        self._applyTheme()
        super().showEvent(event)
        # dopiero po pokazaniu znany jest właściwy devicePixelRatio (skalowanie 125–150%)
        self._setFooterLogo(FOOTER_LOGOS[self._theme])

    def changeEvent(self, event):
        # changeEvent przychodzi już w trakcie setupUi – wtedy _theme jeszcze nie istnieje
        if (event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange)
                and getattr(self, '_theme', None) is not None):
            self._applyTheme()
        super().changeEvent(event)

    def _openHelp(self):
        url = self._readHomepage() or HOME_LINK
        QDesktopServices.openUrl(QUrl(url))

    @staticmethod
    def _readHomepage():
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(os.path.join(PLUGIN_DIR, 'metadata.txt'), encoding='utf-8')
            return parser.get('general', 'homepage', fallback='')
        except Exception:
            return ''

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
