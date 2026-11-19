# -*- coding: utf-8 -*-


import os
import re
import configparser
import warnings
from functools import partial
from qgis.PyQt import QtWidgets, uic, sip
from qgis.PyQt.QtCore import pyqtSignal, QDir, QEvent, QUrl

from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QRegularExpressionValidator, QDesktopServices

from qgis._core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsFileWidget, QgsCollapsibleGroupBox

from . import PLUGIN_VERSION
from .constants import ADMINISTRATIVE_UNITS_OBJECTS, DOUBLE_VALIDATOR_OBJECTS, DATA_TIME_OBJECTS, MAP_LAYER_COMBOBOXES, \
    VOIVODESHIP_COMBOBOXES, YEARS_COMBOBOXES, WFS_URL_MAPPING, AVAILABLE_DATA_LABELS, \
    FOOTER_LINK_COLORS, FOOTER_LOGOS, HOME_LINK, MSG_LIST_LOADING, MSG_LIST_UNAVAILABLE
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
        self._pendingRequests = {}
        self.setup_dialog()
        self._setupLook()

    def setup_dialog(self):
        self.setupValidators()
        self.setupDates()
        self.setupVectorLayersFilters()
        # województwa wypełnia wtyczka po pobraniu w tle (PobieraczDanychGugik.loadVoivodeships)
        self.setVoivodeshipsLoading()
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

    # ------------------------- listy pobierane z sieci (w tle) -------------------------

    @staticmethod
    def _setComboStatus(combo_obj, status_text):
        """Czyści combo i pokazuje status („Ładowanie…”, błąd)."""
        combo_obj.blockSignals(True)
        combo_obj.clear()
        combo_obj.clearEditText()
        combo_obj.blockSignals(False)
        PobieraczDanychDockWidget._setPlaceholder(combo_obj, status_text)

    @staticmethod
    def _setPlaceholder(combo_obj, text):
        """Edytowalne combo (np. województwa) rysuje tekst w lineEdit, więc placeholder ustawiamy też tam."""
        combo_obj.setPlaceholderText(text)
        if combo_obj.isEditable():
            combo_obj.lineEdit().setPlaceholderText(text)

    @staticmethod
    def _fillCombo(combo_obj, items, select_first=False):
        """Wypełnia combo; `items` to słownik {dane: tekst} albo lista tekstów."""
        combo_obj.blockSignals(True)
        combo_obj.clear()
        PobieraczDanychDockWidget._setPlaceholder(combo_obj, '')
        if isinstance(items, dict):
            combo_obj.addItems(list(items.values()))
            for idx, val in enumerate(items.keys()):
                combo_obj.setItemData(idx, val)
        else:
            combo_obj.addItems(items)
        combo_obj.setCurrentIndex(0 if select_first and combo_obj.count() else -1)
        combo_obj.blockSignals(False)

    def setVoivodeshipsLoading(self):
        for obj_name in VOIVODESHIP_COMBOBOXES:
            self._setComboStatus(getattr(self, obj_name), MSG_LIST_LOADING)

    def setVoivodeshipsUnavailable(self):
        """Bez województw nie da się wybrać też powiatu ani gminy - wszystkie dostają ten sam status."""
        dependent_combos = [dependent for _, dependent in ADMINISTRATIVE_UNITS_OBJECTS.values()]
        for obj_name in VOIVODESHIP_COMBOBOXES + dependent_combos:
            self._setComboStatus(getattr(self, obj_name), MSG_LIST_UNAVAILABLE)

    def fillVoivodeships(self, voivodeships_dict):
        for obj_name in VOIVODESHIP_COMBOBOXES:
            self._fillCombo(getattr(self, obj_name), voivodeships_dict)

    def fillYears(self):
        for obj, years in YEARS_COMBOBOXES.items():
            getattr(self, obj).addItems(years)

    def setupAdministrativeUnitObj(self, func, dependent_combo):
        unit_data = self.sender().currentData()
        if not unit_data:
            return
        self._pendingRequests[dependent_combo] = unit_data
        self._setComboStatus(getattr(self, dependent_combo), MSG_LIST_LOADING)
        self.regionFetch.fetchUnitsByTerytAsync(
            func,
            unit_data,
            partial(self._onAdministrativeUnitsFetched, dependent_combo, unit_data)
        )

    def _onAdministrativeUnitsFetched(self, dependent_combo, teryt, unit_dict):
        if not self._isResponseCurrent(dependent_combo, teryt):
            return
        combo_obj = getattr(self, dependent_combo)
        if not unit_dict:
            self._setComboStatus(combo_obj, MSG_LIST_UNAVAILABLE)
            return
        self._fillCombo(combo_obj, unit_dict)

    def wfsServiceCmbbxCurrentTextChanged(self, text):
        if not text:
            return
        cached = self.wfsFetch.getCachedTypenames(text)
        if cached is not None:
            self._fillWfsLayers(cached)
            return
        self._pendingRequests['wfs_layer_cmbbx'] = text
        self._setComboStatus(self.wfs_layer_cmbbx, MSG_LIST_LOADING)
        self.wfsFetch.fetchTypenamesAsync(
            text,
            partial(self._onWfsTypenamesFetched, text)
        )

    def _onWfsTypenamesFetched(self, service_name, typenames_dict):
        if not self._isResponseCurrent('wfs_layer_cmbbx', service_name):
            return
        if not typenames_dict:
            self._setComboStatus(self.wfs_layer_cmbbx, MSG_LIST_UNAVAILABLE)
            return
        self._fillWfsLayers(typenames_dict)

    def _fillWfsLayers(self, typenames_dict):
        self._fillCombo(self.wfs_layer_cmbbx, sorted(typenames_dict.keys(), reverse=True), select_first=True)

    def _isResponseCurrent(self, combo_name, request_key):
        """Czy odpowiedź z zadania w tle nadal dotyczy aktualnego wyboru w doku."""
        if sip.isdeleted(self):
            # dok został usunięty, zanim zadanie się skończyło
            return False
        if self._pendingRequests.get(combo_name) != request_key:
            return False
        del self._pendingRequests[combo_name]
        return True

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
