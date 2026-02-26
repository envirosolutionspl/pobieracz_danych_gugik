
from qgis.core import (
    QgsNewsFeedParser,
    QgsSettings
)
from .utils import MessageUtils
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QComboBox, QPushButton

import re
import os
import unicodedata

from .constants import INDUSTRIES, FEED_URL



class QgisFeed:
    def __init__(self, selected_industry, plugin_name):
        self.s = QgsSettings()
        self.industries_dict = INDUSTRIES

        self.industry_decoded = [key for key, val in self.industries_dict.items() if val == selected_industry]
        self.plugin_name_slug = self.create_slug(plugin_name)

        self.es_url = (
            f"{FEED_URL}?industry={self.industry_decoded[0]}&plugin={self.plugin_name_slug}" if self.industry_decoded else FEED_URL
        )
        self.parser = QgsNewsFeedParser(
            feedUrl=QUrl(self.es_url)
        )
        self.industry_url_short = self.shortenUrl(self.es_url)
        self.envirosolutionsFeedPattern_old = re.compile(f"core/NewsFeed/{self.industry_url_short}")
        self.envirosolutionsFeedPattern_new = re.compile(f"app/news-feed/items/{self.industry_url_short}")

        self.parser.fetched.connect(self.registerFeed)

    def shortenUrl(self, url):
        """
        Funkcja przetwarza zapisany adres qgisfeed'a 
        na forme zapisana w qgis settingsach
        """

        return re.sub(r'://|\.|:|/\?|=|&|-', '', url)

    def create_slug(self, text):
        """
        This function makes slug from a random text
        """
        slug = self.normalizeString(text)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug.lower())  # Remove non-alphanumeric characters except spaces and hyphens
        slug = re.sub(r'[\s]+', '-', slug)  # Replace spaces with hyphens

        return slug.strip('-')

    def normalizeString(self, text):
        return ''.join(part for part in unicodedata.normalize('NFD', text)
                       if unicodedata.category(part) != 'Mn')

    def registerFeed(self):
        """
        Function registers QGIS Feed
        """

        MessageUtils.pushLogInfo('Rejestrowanie feedu')
        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern_old.match(key) or self.envirosolutionsFeedPattern_new.match(key):
                finalKey = re.sub(
                    r'(\d+)',
                    r'9999\1',
                    key.replace(self.industry_url_short, 'httpsfeedqgisorg')
                )
                self.s.setValue(finalKey, self.s.value(key))

            # ponizszy fragment odpowiada za mozliwosc ciaglego wyswietlania wiadomosci
            # przy wlaczeniu qgis za kazdym razem
            if 'cache' in key:
                check_fetch = self.checkIsFetchTime()
                if check_fetch is True: self.s.remove(key)

        self.s.sync()
        self.s.beginGroup(f"app/news-feed/items/{self.industry_url_short}")
        self.s.setValue("last-fetch-time", 0)

    def removeDismissed(self):
        """
        Function checks whether there was already initialized QGIS Feed
        """

        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern_old.match(key) or self.envirosolutionsFeedPattern_new.match(key):
                # sprawdz czy jest odpowiadajacy w qgis
                if self.s.contains(
                        re.sub(
                            r'(\d+)',
                            r'9999\1',
                            key.replace(self.industry_url_short, 'httpsfeedqgisorg')
                        )
                ):
                    self.s.remove(key)
                # self.s.remove(key)
        self.s.sync()

    def checkIsFetchTime(self):
        """
        Function check if the fetch time from QGIS Feed was already registered
        """
        return self.s.contains(f"core/NewsFeed/{self.industry_url_short}/lastFetchTime") \
            or self.s.contains(f"app/news-feed/items/{self.industry_url_short}/last-fetch-time")

    def initFeed(self):
        """
        Function is a built in QGIS class and it is responsible for firing QGIS Feed
        """

        check_fetch = self.checkIsFetchTime()
        if check_fetch is True: self.removeDismissed()
        self.parser.fetch()


class QgisFeedDialog(QDialog):
    def __init__(self, parent=None):
        super(QgisFeedDialog, self).__init__(parent)
        self.ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'qgis_feed.ui')
        uic.loadUi(self.ui_file_path, self)

        self.comboBox = self.findChild(QComboBox, 'comboBox')
        self.pushButton = self.findChild(QPushButton, 'pushButton')
        self.pushButton.clicked.connect(self.onSaveClicked)

        self.loadPreviousSelection()

    def loadPreviousSelection(self):
        settings = QgsSettings()
        
        previous_selection = settings.value("selected_industry")
        if previous_selection:

            index = self.comboBox.findText(previous_selection)
            if index != -1:
                self.comboBox.setCurrentIndex(index)
            self.hide()

    def onSaveClicked(self):
        # zapisz wybraną branżę
        selected_industry = self.comboBox.currentText()
        settings = QgsSettings()
        settings.setValue("selected_industry", selected_industry)
        self.accept()
