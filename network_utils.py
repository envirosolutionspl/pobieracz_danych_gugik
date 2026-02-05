import json
import os
import urllib.error
from qgis.core import QgsNetworkAccessManager, QgsMessageLog
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .constants import TIMEOUT_MS

class NetworkUtils:
    """
    Klasa pomocnicza do obsługi zapytań sieciowych z wykorzystaniem standardowych wyjątków Pythona.
    """
    
    _manager = None

    @classmethod
    def get_manager(cls):
        if cls._manager is None:
            cls._manager = QgsNetworkAccessManager.instance()
        return cls._manager

    @staticmethod
    def _handle_reply_error(reply, url_str):
        """
        Analizuje błąd QNetworkReply i rzuca odpowiedni standardowy wyjątek Pythona.
        """
        error_code = reply.error()
        error_str = reply.errorString()
        
        http_status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        http_reason = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)
        
        # Logowanie błędu
        log_msg = f"Network Error | URL: {url_str} | Status: {http_status} | Code: {error_code} | Msg: {error_str}"
        QgsMessageLog.logMessage(log_msg, "PobieraczDanych", level=2)

        # Błędy HTTP
        if http_status and http_status >= 400:
            raise urllib.error.HTTPError(url_str, http_status, http_reason, None, None)
        
        # Timeout
        if error_code == QNetworkReply.TimeoutError:
            raise TimeoutError(f"Przekroczono czas oczekiwania dla: {url_str}")
            
        # Problemy z połączeniem
        if error_code == QNetworkReply.SslHandshakeFailedError:
            raise ConnectionError(f"Błąd SSL: Problem z weryfikacją certyfikatu dla: {url_str}")

        if error_code in (QNetworkReply.ConnectionRefusedError, 
                         QNetworkReply.RemoteHostClosedError, 
                         QNetworkReply.HostNotFoundError,
                         QNetworkReply.NetworkSessionFailedError):
            raise ConnectionError(f"Błąd połączenia ({error_str}) dla: {url_str}")
        
        # Inne błędy sieciowe
        raise RuntimeError(f"Nieoczekiwany błąd sieciowy ({error_str}) dla: {url_str}")

    @classmethod
    def fetch_json(cls, url, params=None, timeout_ms=TIMEOUT_MS):
        """
        Pobiera dane JSON. Rzuca wyjątki sieciowe lub json.JSONDecodeError.
        """
        content = cls.fetch_content(url, params, timeout_ms)
        return json.loads(content)

    @classmethod
    def fetch_content(cls, url, params=None, timeout_ms=TIMEOUT_MS*2):
        """
        Pobiera treść jako string. Rzuca TimeoutError, ConnectionError lub HTTPError.
        """
        qurl = QUrl(url)
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(str(key), str(value))
            qurl.setQuery(query)
            
        request = QNetworkRequest(qurl)
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        
        # pobieranie danych
        manager = cls.get_manager()
        reply = manager.get(request)
        
        # pętla do obsługi timeout
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        
        reply.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        
        timer.start(timeout_ms)
        loop.exec_()
        
        if not timer.isActive():
            reply.abort()
            reply.deleteLater()
            raise TimeoutError(f"Timeout ({timeout_ms}ms) przed otrzymaniem odpowiedzi z: {url}")
        
        timer.stop()
        
        if reply.error() != QNetworkReply.NoError:
            try:
                cls._handle_reply_error(reply, url)
            finally:
                reply.deleteLater()
                
        try:
            raw_data = reply.readAll()
            data = raw_data.data().decode('utf-8')
            return data
        except UnicodeDecodeError as e:
            raise ValueError(f"Błąd dekodowania danych (UTF-8) z: {url}") from e
        finally:
            reply.deleteLater()

    @classmethod
    def download_file(cls, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS * 6):
        """
        Pobiera plik. Rzuca wyjątki sieciowe, IOError lub InterruptedError przy anulowaniu.
        """
        qurl = QUrl(url)
        request = QNetworkRequest(qurl)
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        
        manager = cls.get_manager()
        reply = manager.get(request)
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        
        reply.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            reply.abort()
            reply.deleteLater()
            raise FileNotFoundError(f"Katalog docelowy nie istnieje: {dest_dir}")

        try:
            with open(dest_path, 'wb') as f:
                timer.start(timeout_ms)
                
                while reply.isRunning():
                    loop.processEvents(QEventLoop.ExcludeUserInputEvents, 100)
                    
                    if obj and obj.isCanceled():
                        reply.abort()
                        raise InterruptedError("Pobieranie anulowane przez użytkownika.")
                        
                    if reply.bytesAvailable() > 0:
                        f.write(reply.readAll().data())
                        timer.start(timeout_ms) # Resetuj timer przy każdej paczce danych
                    
                    if not timer.isActive():
                        reply.abort()
                        raise TimeoutError("Przerwano pobieranie: brak danych od serwera (Timeout).")

                if reply.error() != QNetworkReply.NoError:
                    cls._handle_reply_error(reply, url)
                
                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
                    
        finally:
            reply.deleteLater()
            
        return True