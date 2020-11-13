from qgis.core import QgsNewsFeedParser, QgsSettings
from PyQt5.QtCore import QUrl
import re


s = QgsSettings()
# qgisFeedPattern = re.compile('core/NewsFeed/httpsfeedqgisorg/9999\d+/\w+')
envirosolutionsFeedPattern = re.compile('core/NewsFeed/httpsqgisfeedenvirosolutionspl/\d+/\w+')
def updateOnStart():
    parser = QgsNewsFeedParser(QUrl("https://qgisfeed.envirosolutions.pl/"))
    parser.fetch()
    for key in s.allKeys():
        if 'core/NewsFeed/httpsqgisfeedenvirosolutionspl/' in key:
            finalValue = re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))
            s.setValue(finalValue, s.value(key))

def removeDismissed():
    for key in s.allKeys():
        if envirosolutionsFeedPattern.match(key):
            # sprawdz czy jest odpowiadajacy w qgis
            if not s.contains(re.sub(r'(\d+)', r'9999\1', key.replace('httpsqgisfeedenvirosolutionspl', 'httpsfeedqgisorg'))):
                s.remove(key)



