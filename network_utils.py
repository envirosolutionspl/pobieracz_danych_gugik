import json
import os
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .constants import TIMEOUT_MS
from .utils import pushLogWarning

class NetworkUtils:
    def __init__(self):
        self.manager = QgsNetworkAccessManager.instance()

    def _handleReplyError(self, reply, url_str):
        error_code = reply.error()
        error_str = reply.errorString()
        
        http_status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        http_reason = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)
        
        pushLogWarning(f"Network Error | URL: {url_str} | Status: {http_status} | Code: {error_code} | Msg: {error_str}")

        if http_status and http_status >= 400:
            return False, f"Błąd HTTP {http_status}: {http_reason}"
        
        if error_code == QNetworkReply.TimeoutError:
            return False, f"Przekroczono czas oczekiwania dla: {url_str}"
            
        return False, f"Błąd sieciowy ({error_str}) dla: {url_str}"

    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS*2):
        qurl = QUrl(url)
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(str(key), str(value))
            qurl.setQuery(query)
            
        request = QNetworkRequest(qurl)
        
        request.setAttribute(QNetworkRequest.RedirectPolicyAttribute, QNetworkRequest.NoLessSafeRedirectPolicy)
        
        reply = self.manager.get(request)   
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        
        reply.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        
        timer.start(timeout_ms)
        loop.exec()
        
        if not timer.isActive():
            reply.abort()
            reply.deleteLater()
            return False, f"Timeout ({timeout_ms}ms) dla: {url}"
        
        timer.stop()
        
        if reply.error() != QNetworkReply.NoError:
            success, error_msg = self._handleReplyError(reply, url)
            reply.deleteLater()
            return success, error_msg
                
        try:
            data = reply.readAll().data().decode('utf-8')
            return True, data
        except Exception:
            return False, f"Błąd dekodowania danych z: {url}"
        finally:
            reply.deleteLater()

    def fetchJson(self, url, params=None, timeout_ms=TIMEOUT_MS):
        success, result = self.fetchContent(url, params, timeout_ms)
        if not success:
            return False, result
        try:
            return True, json.loads(result)
        except json.JSONDecodeError as e:
            return False, f"Błąd JSON: {str(e)}"

    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS * 6):
        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.RedirectPolicyAttribute, QNetworkRequest.NoLessSafeRedirectPolicy)
        
        reply = self.manager.get(request)
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        
        reply.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            reply.abort()
            reply.deleteLater()
            return False, f"Katalog nie istnieje: {dest_dir}"

        try:
            with open(dest_path, 'wb') as f:
                timer.start(timeout_ms)
                
                while reply.isRunning():
                    loop.exec()
                    
                    if obj and obj.isCanceled():
                        reply.abort()
                        return False, "Anulowano."
                        
                    if reply.bytesAvailable() > 0:
                        f.write(reply.readAll().data())
                        timer.start(timeout_ms) 
                
                if reply.error() != QNetworkReply.NoError:
                    return self._handleReplyError(reply, url)
                    
                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
        finally:
            reply.deleteLater()
            
        return True, True