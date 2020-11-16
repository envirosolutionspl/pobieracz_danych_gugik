from qgis.core import QgsNewsFeedParser, QgsSettings, QgsNewsFeedModel, QgsMessageLog
from PyQt5.QtCore import QUrl
import re

class QgisFeed:
    def __init__(self):
        self.s = QgsSettings()
        self.qgisFeedPattern = re.compile('core/NewsFeed/httpsfeedqgisorg/9999\d+/\w+')
        self.envirosolutionsFeedPattern = re.compile('core/NewsFeed/httpsqgisfeedenvirosolutionspl/\d+/\w+')
        self.parser = QgsNewsFeedParser(QUrl("https://qgisfeed.envirosolutions.pl/"))
        self.parser.fetched.connect(self.registerFeed)

    def registerFeed(self):
        QgsMessageLog.logMessage('asdasdas33')
        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern.match(key):
                finalKey = re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))
                self.s.setValue(finalKey, self.s.value(key))

    def removeDismissed(self):
        for key in self.s.allKeys():
            if self.envirosolutionsFeedPattern.match(key):
                # sprawdz czy jest odpowiadajacy w qgis
                if not self.s.contains(re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))):
                    self.s.remove(key)

    def initFeed(self):
        if self.s.contains('core/NewsFeed/httpsqgisfeedenvirosolutionspl/lastFetchTime'):  # już istnieje feed
            self.removeDismissed()
        self.parser.fetch()

