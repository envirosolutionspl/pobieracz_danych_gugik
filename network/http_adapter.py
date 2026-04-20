import requests
import json
import os
import ssl
from functools import partial
from requests.adapters import HTTPAdapter
from qgis.core import QgsBlockingNetworkRequest, QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer, QT_VERSION_STR
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager
from ..constants import (
    TIMEOUT_MS,
    MAX_ATTEMPTS,
    CANCEL_CHECK_MS,
    QT_VER,
    HTTP_ERROR_THRESHOLD,
    DEFAULT_ENCODING,
    NETWORK_ATTRS,
    ERR_TIMEOUT,
    ERR_NONE,
    ERR_CANCELED,
    REDIRECT_POLICY_NAME,
    REDIRECT_POLICY_NO_LESS_SAFE,
    DEFAULT_REDIRECT_POLICY,
    MSG_FILE_WRITE_ERROR,
    MSG_DOWNLOAD_CANCELED,
    MSG_EMPTY_CONTENT,
    MSG_JSON_DECODE_ERROR,
    MSG_HTTP_ERROR,
    MSG_TIMEOUT,
    MSG_NETWORK_ERROR,
    MSG_NO_CONNECTION,
    TRANSPORT_MARKERS,
    ERROR_MARKERS,
)

class SslContextHttpAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        if self.ssl_context is not None:
            pool_kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if self.ssl_context is not None:
            proxy_kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)

class BaseHttpAdapter:
    '''
    Klasa bazowa do pobierania tekstu/JSON/pliku
    '''

    def fetchJson(self, url, params=None, timeout_ms=TIMEOUT_MS):
        is_success, result = self.fetchContent(url, params, timeout_ms)
        if not is_success:
            return False, result
        try:
            return True, json.loads(result)
        except json.JSONDecodeError as e:
            return False, MSG_JSON_DECODE_ERROR.format(str(e))

    @staticmethod
    def timeoutToSeconds(timeout_ms):
        return max(timeout_ms / 1000.0, 0.001)


class QgisHttpAdapter():
    '''
    Klasa do pobierania tekstu/JSON/pliku za pomocą QgsBlockingNetworkRequest
    '''
    def __init__(self):
        self.manager = QNetworkAccessManager()
        self.manager.setProxy(QgsNetworkAccessManager.instance().proxy())
        self.isCompatibleQtVersion = self._isCompatibleQtVersion(QT_VERSION_STR, 6)

    def _isCompatibleQtVersion(self, cur_version, tar_version):
        return cur_version.startswith(QT_VER[tar_version])

    def getAttributeEnum(self, attr_name):
        """Pobiera atrybut QNetworkRequest"""
        if self.isCompatibleQtVersion:
            if hasattr(QNetworkRequest, 'Attribute'):
                val = getattr(QNetworkRequest.Attribute, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkRequest, attr_name, None)

    def getErrorEnum(self, attr_name):
        """Pobiera kod błędu QNetworkReply"""
        if self.isCompatibleQtVersion:
            if hasattr(QNetworkReply, 'NetworkError'):
                val = getattr(QNetworkReply.NetworkError, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkReply, attr_name, None)

    def setAttributes(self, request, timeout_ms):
        """Ustawia atrybuty zapytania"""
        redirect_attr = self.getAttributeEnum(NETWORK_ATTRS['REDIRECT'])
        if redirect_attr is not None:
            redirect_policy_class = getattr(QNetworkRequest, REDIRECT_POLICY_NAME, QNetworkRequest)
            redirect_policy = getattr(redirect_policy_class, REDIRECT_POLICY_NO_LESS_SAFE, DEFAULT_REDIRECT_POLICY)
            request.setAttribute(redirect_attr, redirect_policy)
        
        timeout_attr = self.getAttributeEnum(NETWORK_ATTRS['TIMEOUT'])
        if timeout_attr is not None:
            request.setAttribute(timeout_attr, timeout_ms)

    def handleReplyError(self, reply, url_str):
        """Centralna obsługa błędów sieciowych i HTTP"""
        
        error_code = reply.error()
        error_str = reply.errorString()
        
        status_attr = self.getAttributeEnum(NETWORK_ATTRS['HTTP_STATUS'])
        reason_attr = self.getAttributeEnum(NETWORK_ATTRS['HTTP_REASON'])
        timeout_err = self.getErrorEnum(ERR_TIMEOUT)

        http_status = reply.attribute(status_attr)
        http_reason = reply.attribute(reason_attr)
        
        if http_status and http_status >= HTTP_ERROR_THRESHOLD:
            return False, MSG_HTTP_ERROR.format(http_status, http_reason)
        
        if error_code == timeout_err:
            return False, MSG_TIMEOUT.format(url_str)
            
        return False, MSG_NETWORK_ERROR.format(error_str, url_str)

    def hasErrorOccurred(self, reply):
        """Sprawdza czy wystąpił błąd w odpowiedzi"""
        no_error = self.getErrorEnum(ERR_NONE)
        return reply.error() != no_error

    def handleReadyRead(self, reply, file):
        if reply.bytesAvailable() > 0:
            file.write(reply.readAll().data())

    def loopForCancel(self, obj, reply, event_loop):
        cancel_timer = QTimer()
        cancel_timer.timeout.connect(lambda: reply.abort() if (obj and obj.isCanceled()) else None)
        cancel_timer.start(CANCEL_CHECK_MS)
        
        event_loop.exec()

        cancel_timer.stop()

    def finalizeDownload(self, reply, url):
        if self.hasErrorOccurred(reply):
            canceled_error = self.getErrorEnum(ERR_CANCELED)
            if reply.error() == canceled_error:
                reply.deleteLater()
                return False, MSG_DOWNLOAD_CANCELED
            
            error_res = self.handleReplyError(reply, url)
            reply.deleteLater()
            return error_res

        reply.deleteLater()
        return True, True

    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS):
        q_url = QUrl(url)
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(str(key), str(value))
            q_url.setQuery(query)
            
        request = QNetworkRequest(q_url)
        self.setAttributes(request, timeout_ms)
        
        blocking_request = QgsBlockingNetworkRequest()
        error_code = blocking_request.get(request)
        reply_content = blocking_request.reply()
        
        if error_code != QgsBlockingNetworkRequest.NoError:
            return self.handleReplyError(reply_content, url)

        raw_data = reply_content.content()
        if len(raw_data) == 0:
            return False, MSG_EMPTY_CONTENT.format(url)
            
        try:
            data = bytes(raw_data).decode(DEFAULT_ENCODING)
            return True, data
        except UnicodeDecodeError:
            return True, f"BinaryData: {len(raw_data)} bytes"

    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS):
        request = QNetworkRequest(QUrl(url))
        self.setAttributes(request, timeout_ms)

        dest_dir = os.path.dirname(dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        event_loop = QEventLoop()
        reply = self.manager.get(request)
        try:
            with open(dest_path, 'wb') as f:
                reply.readyRead.connect(partial(self.handleReadyRead, reply, f))
                reply.finished.connect(event_loop.quit)

                self.loopForCancel(obj, reply, event_loop)

                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
        except IOError as e:
            return False, MSG_FILE_WRITE_ERROR.format(str(e))
            
        return self.finalizeDownload(reply, url)

class RequestsHttpAdapter():
    '''
    Klasa do pobierania tekstu/JSON/pliku za pomocą requests
    '''
    def __init__(self):
        self.manager = requests.Session()
        ssl_context = self._buildRequestsSslContext()
        self.manager.mount("https://", SslContextHttpAdapter(ssl_context=ssl_context))

    def _buildRequestsSslContext(self):
        """
        Build SSL context for requests.
        Enables legacy renegotiation only when OpenSSL exposes this switch.
        """
        context = ssl.create_default_context()
        legacy_option = getattr(ssl, "OP_LEGACY_SERVER_CONNECT", None)
        if legacy_option is not None:
            context.options |= legacy_option
        return context

    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS):
        timeout_seconds = BaseHttpAdapter.timeoutToSeconds(timeout_ms)
        try:
            response = self.manager.get(
                url,
                params=params,
                timeout=timeout_seconds,
                allow_redirects=True
            )
            if response.status_code >= HTTP_ERROR_THRESHOLD:
                return False, MSG_HTTP_ERROR.format(response.status_code, response.reason)

            if not response.content:
                return False, MSG_EMPTY_CONTENT.format(url)

            response.encoding = response.encoding or DEFAULT_ENCODING
            return True, response.text
        except requests.exceptions.Timeout:
            return False, MSG_TIMEOUT.format(url)
        except requests.exceptions.RequestException as e:
            return False, MSG_NETWORK_ERROR.format(str(e), url)
            
    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS):
        timeout_seconds = BaseHttpAdapter.timeoutToSeconds(timeout_ms)
        dest_dir = os.path.dirname(dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        try:
            with self.manager.get(url, stream=True, timeout=timeout_seconds, allow_redirects=True) as response:
                if response.status_code >= HTTP_ERROR_THRESHOLD:
                    return False, MSG_HTTP_ERROR.format(response.status_code, response.reason)

                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if obj and obj.isCanceled():
                            f.close()
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
                            return False, MSG_DOWNLOAD_CANCELED
                        if chunk:
                            f.write(chunk)
        except IOError as e:
            return False, MSG_FILE_WRITE_ERROR.format(str(e))
        except requests.exceptions.Timeout:
            return False, MSG_TIMEOUT.format(url)
        except requests.exceptions.RequestException as e:
            return False, MSG_NETWORK_ERROR.format(str(e), url)

        return True, True

class FallbackHttpAdapter(BaseHttpAdapter):
    '''
    Klasa, która najpierw spróbuje QgisHttpAdapter, a jeśli się nie uda, to RequestsHttpAdapter
    '''
    def __init__(self, qgis_adapter=None, requests_adapter=None):
        self.qgis_adapter = qgis_adapter or QgisHttpAdapter()
        self.requests_adapter = requests_adapter or RequestsHttpAdapter()
        self.error_markers = ERROR_MARKERS
        self.transport_markers = TRANSPORT_MARKERS
    def _isFallbackNeeded(self, error_message):
        if not error_message:
            return False

        msg = str(error_message).lower()

        # Nie przełączamy adaptera dla błędów biznesowych HTTP ani anulowania.
        if self.error_markers[0] in msg or self.error_markers[1] in msg:
            return False
        if MSG_DOWNLOAD_CANCELED.lower() in msg:
            return False

        # Fallback dla najczęstszych problemów transportowych/SSL.
        return any(marker in msg for marker in self.transport_markers)

    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS):
        is_success, result = self.qgis_adapter.fetchContent(url, params=params, timeout_ms=timeout_ms)
        if is_success:
            return True, result

        if not self._isFallbackNeeded(result):
            return False, result

        return self.requests_adapter.fetchContent(url, params=params, timeout_ms=timeout_ms)

    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS):
        is_success, result = self.qgis_adapter.downloadFile(
            url=url,
            dest_path=dest_path,
            obj=obj,
            timeout_ms=timeout_ms
        )
        if is_success:
            return True, result

        if not self._isFallbackNeeded(result):
            return False, result

        return self.requests_adapter.downloadFile(
            url=url,
            dest_path=dest_path,
            obj=obj,
            timeout_ms=timeout_ms
        )