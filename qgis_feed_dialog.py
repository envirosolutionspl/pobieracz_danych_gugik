
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QDir, QEvent
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QPushButton

from .constants import FOOTER_LOGOS
from .utils import ThemeUtils

PLUGIN_DIR = os.path.dirname(__file__)

# Prefiks "pdgimg:" używany w url(...) arkusza stylów w ui/qgis_feed.ui (strzałka listy).
QDir.addSearchPath('pdgimg', os.path.join(PLUGIN_DIR, 'images'))


class QgisFeedDialog(QDialog):
    def __init__(self, industries, current_code, parent=None):
        super(QgisFeedDialog, self).__init__(parent)
        self.ui_file_path = os.path.join(PLUGIN_DIR, 'ui', 'qgis_feed.ui')
        uic.loadUi(self.ui_file_path, self)
        self._theme = None

        self.comboBox = self.findChild(QComboBox, 'comboBox')
        self.pushButton = self.findChild(QPushButton, 'pushButton')
        self.comboBox.clear()
        for code, name in industries:
            self.comboBox.addItem(name, code)
        index = self.comboBox.findData(current_code)
        self.comboBox.setCurrentIndex(index if index != -1 else 0)
        self.pushButton.clicked.connect(self.accept)

        self._applyTheme()

    def selectedCode(self) -> str:
        return self.comboBox.currentData()

    # ------------------------------- Motyw -----------------------------------
    def _applyTheme(self, force=False):
        """Ustawia właściwość "theme" – kolory są zdefiniowane w arkuszu stylów ui/qgis_feed.ui."""
        theme = 'dark' if ThemeUtils.isDarkTheme() else 'light'
        if theme == self._theme and not force:
            return
        self._theme = theme
        self.setProperty('theme', theme)
        ThemeUtils.repolishAll(self)
        self._setLogo()

    def _setLogo(self, height=30):
        """Logo w stopce: zielone na jasnym tle, białe na ciemnym (FOOTER_LOGOS w constants)."""
        if self._theme is not None:
            ThemeUtils.setLogo(self.lbl_logo, FOOTER_LOGOS[self._theme], height)

    def showEvent(self, event):
        self._applyTheme()
        super().showEvent(event)
        # dopiero po pokazaniu znana jest skala ekranu – inaczej logo jest rozpikselowane
        self._setLogo()

    def changeEvent(self, event):
        # changeEvent przychodzi już w trakcie loadUi – wtedy _theme jeszcze nie istnieje
        if (event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange)
                and getattr(self, '_theme', None) is not None):
            self._applyTheme()
        super().changeEvent(event)
