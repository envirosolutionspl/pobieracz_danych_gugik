from qgis.core import QgsNewsFeedParser, QgsSettings, QgsNewsFeedModel, QgsMessageLog
from qgis.PyQt.QtCore import QUrl
import re

class QgisFeed:
    def __init__(self):
        self.s = QgsSettings()
        self.envirosolutionsFeedPattern_old = re.compile('core/NewsFeed/httpsqgisfeedenvirosolutionspl')
        self.envirosolutionsFeedPattern_new = re.compile('app/news-feed/items/httpsqgisfeedenvirosolutionspl/entries/items')
        # self.envirosolutionsFeedPattern = re.compile('core/NewsFeed/httpsqgisfeedenvirosolutionspl/\d+/\w+')
        self.parser = QgsNewsFeedParser(QUrl("https://qgisfeed.envirosolutions.pl/"))
        self.parser.fetched.connect(self.registerFeed)

    def registerFeed(self):
        QgsMessageLog.logMessage('Registering feed')
        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern_old.match(key) or self.envirosolutionsFeedPattern_new.match(key):
                finalKey = re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))
                self.s.setValue(finalKey, self.s.value(key))

    def removeDismissed(self):
        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern_old.match(key) or self.envirosolutionsFeedPattern_new.match(key):
                # sprawdz czy jest odpowiadajacy w qgis
                if not self.s.contains(re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))):
                    self.s.remove(key)

    def initFeed(self):
        if self.s.contains('core/NewsFeed/httpsqgisfeedenvirosolutionspl/lastFetchTime') \
                or self.s.contains('app/news-feed/items/httpsqgisfeedenvirosolutionspl/last-fetch-time'):  # już istnieje feed
            self.removeDismissed()
        self.parser.fetch()

