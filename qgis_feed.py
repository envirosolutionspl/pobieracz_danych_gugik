
import json
import re
import unicodedata
import uuid
from functools import partial

from qgis.core import QgsApplication, QgsNetworkAccessManager, QgsNewsFeedParser, QgsSettings
from qgis.PyQt.QtCore import QTimer, QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QDialog

from .constants import (FEED_URL, INDUSTRIES_URL, INDUSTRIES_TIMEOUT_MS,
                        FEED_KEY_USER_ID, FEED_KEY_INDUSTRY,
                        FEED_APP_PROPERTY_DIALOG_HANDLED)
from .utils import MessageUtils


class FeedSettings:

    @staticmethod
    def getUserId() -> str:
        settings = QgsSettings()
        user_id = settings.value(FEED_KEY_USER_ID, '', type=str)
        if not user_id:
            user_id = uuid.uuid4().hex
            settings.setValue(FEED_KEY_USER_ID, user_id)
        return user_id

    @staticmethod
    def getIndustryCode() -> str:
        return QgsSettings().value(FEED_KEY_INDUSTRY, '', type=str)

    @staticmethod
    def setIndustryCode(code: str):
        QgsSettings().setValue(FEED_KEY_INDUSTRY, code)


class IndustriesFetch:

    def __init__(self):
        self._reply = None
        self._timer = None
        self._on_done = None
        self._finished = False

    def start(self, on_done):
        self._on_done = on_done
        request = QNetworkRequest(QUrl(INDUSTRIES_URL))
        request.setAttribute(QNetworkRequest.Attribute.CacheLoadControlAttribute,
                             QNetworkRequest.CacheLoadControl.AlwaysNetwork)
        self._reply = QgsNetworkAccessManager.instance().get(request)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._onTimeout)
        self._reply.finished.connect(self._onReplyFinished)
        self._timer.start(INDUSTRIES_TIMEOUT_MS)

    def _onTimeout(self):
        if self._finished:
            return
        self._finished = True
        self._reply.abort()
        MessageUtils.pushLogWarning(f'Lista branż: przekroczono limit czasu ({INDUSTRIES_TIMEOUT_MS} ms)')
        self._on_done(None)

    def _onReplyFinished(self):
        reply = self._reply
        self._reply = None
        reply.deleteLater()
        if self._finished:
            return
        self._timer.stop()
        self._finished = True
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if reply.error() != QNetworkReply.NetworkError.NoError:
            MessageUtils.pushLogWarning(f'Lista branż: błąd sieci ({reply.errorString()})')
            self._on_done(None)
            return
        if status != 200:
            MessageUtils.pushLogWarning(f'Lista branż: nieoczekiwany status HTTP {status}')
            self._on_done(None)
            return
        self._on_done(self.parseIndustries(bytes(reply.readAll())))

    @staticmethod
    def parseIndustries(raw: bytes):
        try:
            data = json.loads(raw.decode('utf-8'))
        except UnicodeDecodeError as e:
            MessageUtils.pushLogWarning(f'Lista branż: niepoprawne kodowanie odpowiedzi (UnicodeDecodeError): {e}')
            return None
        except json.JSONDecodeError as e:
            MessageUtils.pushLogWarning(f'Lista branż: niepoprawny JSON (JSONDecodeError): {e}')
            return None
        if not isinstance(data, list):
            MessageUtils.pushLogWarning('Lista branż: odpowiedź nie jest listą')
            return None
        industries = []
        for item in data:
            if isinstance(item, list) and len(item) == 2 and all(isinstance(value, str) for value in item):
                industries.append((item[0], item[1]))
            else:
                MessageUtils.pushLogWarning(f'Lista branż: pominięto niepoprawny element {item!r}')
        if not industries:
            MessageUtils.pushLogWarning('Lista branż: pusta lista')
            return None
        return industries

    def cancel(self):
        if self._finished:
            return
        self._finished = True
        if self._timer is not None:
            self._timer.stop()
        if self._reply is not None:
            self._reply.abort()


class QgisFeed:
    def __init__(self, plugin_name, industry_code, user_id):
        self.s = QgsSettings()
        self.es_url = self.buildFeedUrl(plugin_name, industry_code, user_id)
        self.parser = QgsNewsFeedParser(
            feedUrl=QUrl(self.es_url)
        )
        self.industry_url_short = self.shortenUrl(self.es_url)
        self.envirosolutionsFeedPattern_old = re.compile(f"core/NewsFeed/{self.industry_url_short}")
        self.envirosolutionsFeedPattern_new = re.compile(f"app/news-feed/items/{self.industry_url_short}")

        self.parser.fetched.connect(self.registerFeed)

    @staticmethod
    def buildFeedUrl(plugin_name, industry_code, user_id) -> str:
        params = (
            ('industry', industry_code),
            ('plugin', QgisFeed.createSlug(plugin_name or '')),
            ('uid', user_id),
        )
        query = QUrlQuery()
        for key, value in params:
            if value:
                query.addQueryItem(key, value)
        url = QUrl(FEED_URL)
        if not query.isEmpty():
            url.setQuery(query)
        return url.toString()

    @staticmethod
    def shortenUrl(url):
        """
        Funkcja przetwarza zapisany adres qgisfeed'a
        na forme zapisana w qgis settingsach
        """

        return re.sub(r'://|\.|:|/\?|=|&|-', '', url)

    @staticmethod
    def createSlug(text):
        """
        This function makes slug from a random text
        """
        slug = QgisFeed.normalizeString(text)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug.lower())  # Remove non-alphanumeric characters except spaces and hyphens
        slug = re.sub(r'[\s]+', '-', slug)  # Replace spaces with hyphens

        return slug.strip('-')

    @staticmethod
    def normalizeString(text):
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
                if check_fetch is True:
                    self.s.remove(key)

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
        if check_fetch is True:
            self.removeDismissed()
        self.parser.fetch()


class EnviroFeedManager:

    def __init__(self, iface, plugin_name, dialog_class):
        self.iface = iface
        self.plugin_name = plugin_name
        self.dialog_class = dialog_class
        self.feed = None
        self._user_id = ''
        self._fetch = None
        self._init_slot = None
        self._unloaded = False

    def start(self):
        self._user_id = FeedSettings.getUserId()
        code = FeedSettings.getIndustryCode()
        self._startFeed(code)
        self._fetch = IndustriesFetch()
        self._fetch.start(self._onIndustriesFetched)

    def _startFeed(self, code):
        self.feed = QgisFeed(self.plugin_name, code, self._user_id)
        self.feed.initFeed()

    def _onIndustriesFetched(self, industries):
        if self._unloaded:
            return
        if industries is None:
            MessageUtils.pushLogWarning('Brak listy branż - okno wyboru branży nie zostanie pokazane w tej sesji')
            return

        code = FeedSettings.getIndustryCode()
        known_codes = [item_code for item_code, _ in industries]
        if code in known_codes:
            return
        for item_code, item_name in industries:
            if code and item_name == code:
                FeedSettings.setIndustryCode(item_code)
                self._startFeed(item_code)
                return

        app = QgsApplication.instance()
        if app.property(FEED_APP_PROPERTY_DIALOG_HANDLED):
            return
        app.setProperty(FEED_APP_PROPERTY_DIALOG_HANDLED, True)

        if self.iface.mainWindow().isVisible():
            self._showDialog(industries)
        else:
            self._init_slot = partial(self._onInitializationCompleted, industries)
            self.iface.initializationCompleted.connect(self._init_slot)

    def _onInitializationCompleted(self, industries):
        self._disconnectInitializationCompleted()
        if not self._unloaded:
            self._showDialog(industries)

    def _disconnectInitializationCompleted(self):
        if self._init_slot is None:
            return
        try:
            self.iface.initializationCompleted.disconnect(self._init_slot)
        except TypeError as e:
            MessageUtils.pushLogWarning(f'Nie udało się odłączyć initializationCompleted (TypeError): {e}')
        self._init_slot = None

    def _showDialog(self, industries):
        dialog = self.dialog_class(industries, FeedSettings.getIndustryCode(), self.iface.mainWindow())
        if dialog.exec() == QDialog.DialogCode.Accepted and not self._unloaded:
            code = dialog.selectedCode()
            FeedSettings.setIndustryCode(code)
            self._startFeed(code)

    def unload(self):
        self._unloaded = True
        if self._fetch is not None:
            self._fetch.cancel()
            self._fetch = None
        self._disconnectInitializationCompleted()
