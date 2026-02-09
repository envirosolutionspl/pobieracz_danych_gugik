import json
import os
import urllib.error
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .constants import TIMEOUT_MS
from .utils import pushLogWarning

class NetworkUtils:
    """
    Klasa pomocnicza do obsługi zapytań sieciowych z wykorzystaniem standardowych wyjątków Pythona.
    """
    
    _manager = None 

    @classmethod
    def getManager(cls):
        """
        Tworzy i/lub zwraca manager sieciowy.
        """
        if cls._manager is None:
            cls._manager = QgsNetworkAccessManager.instance()
        return cls._manager

    @staticmethod
    def _handleReplyError(reply, url_str):
        """
        Analizuje błąd QNetworkReply i zwraca komunikat błędu.
        """
        error_code = reply.error()
        error_str = reply.errorString()
        
        http_status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        http_reason = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)
        
        # Logowanie błędu
        log_msg = f"Network Error | URL: {url_str} | Status: {http_status} | Code: {error_code} | Msg: {error_str}"
        pushLogWarning(log_msg)

        # Błędy HTTP
        if http_status and http_status >= 400:
            return False, f"Błąd HTTP {http_status}: {http_reason}"
        
        # Timeout
        if error_code == QNetworkReply.TimeoutError:
            return False, f"Przekroczono czas oczekiwania dla: {url_str}"
            
        # Problemy z połączeniem
        if error_code == QNetworkReply.SslHandshakeFailedError:
            return False, f"Błąd SSL: Problem z weryfikacją certyfikatu dla: {url_str}"

        if error_code in (QNetworkReply.ConnectionRefusedError, 
                         QNetworkReply.RemoteHostClosedError, 
                         QNetworkReply.HostNotFoundError,
                         QNetworkReply.NetworkSessionFailedError):
            return False, f"Błąd połączenia ({error_str}) dla: {url_str}"
        
        # Inne błędy sieciowe
        return False, f"Nieoczekiwany błąd sieciowy ({error_str}) dla: {url_str}"

    @classmethod
    def fetchJson(cls, url, params=None, timeout_ms=TIMEOUT_MS):
        success, result = cls.fetchContent(url, params, timeout_ms)
        if not success:
            return False, result
        try:
            return True, json.loads(result)
        except json.JSONDecodeError as e:
            return False, f"Błąd dekodowania JSON dla: {url}. Szczegóły: {str(e)}"

    @classmethod
    def fetchContent(cls, url, params=None, timeout_ms=TIMEOUT_MS*2):
        """
        Pobiera treść jako string. Zwraca tuple (success, result/error)
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
        reply = cls.getManager().get(request)
        
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
            return False, f"Timeout ({timeout_ms}ms) przed otrzymaniem odpowiedzi z: {url}"
        
        timer.stop()
        
        if reply.error() != QNetworkReply.NoError:
            success, error_msg = cls._handleReplyError(reply, url)
            reply.deleteLater()
            return success, error_msg
                
        try:
            raw_data = reply.readAll()
            data = raw_data.data().decode('utf-8')
            return True, data
        except UnicodeDecodeError as e:
            return False, f"Błąd dekodowania danych (UTF-8) z: {url}"
        finally:
            reply.deleteLater()

    @classmethod
    def downloadFile(cls, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS * 6):
        """
        Pobiera plik. Zwraca tuple (success, result/error)
        """
        qurl = QUrl(url)
        request = QNetworkRequest(qurl)
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        
        reply = cls.getManager().get(request)
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        
        reply.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            reply.abort()
            reply.deleteLater()
            return False, f"Błąd IO: Katalog docelowy nie istnieje: {dest_dir}"

        try:
            with open(dest_path, 'wb') as f:
                timer.start(timeout_ms)
                
                while reply.isRunning():
                    loop.processEvents(QEventLoop.ExcludeUserInputEvents, 100)
                    
                    if obj and obj.isCanceled():
                        reply.abort()
                        return False, "Pobieranie anulowane przez użytkownika."
                        
                    if reply.bytesAvailable() > 0:
                        f.write(reply.readAll().data())
                        timer.start(timeout_ms) 
                    
                    if not timer.isActive():
                        reply.abort()
                        return False, "Przerwano pobieranie: brak danych od serwera (Timeout)."

                if reply.error() != QNetworkReply.NoError:
                    success_err, error_msg = cls._handleReplyError(reply, url)
                    return success_err, error_msg
                
                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
                    
        except IOError as e:
            return False, f"Błąd systemu plików IOError podczas zapisu: {str(e)}"
        except OSError as e:
            return False, f"Błąd systemu plików OSError podczas zapisu: {str(e)}"
        except Exception as e:
            return False, f"Nieoczekiwany błąd podczas zapisu: {str(e)}"
        finally:
            reply.deleteLater()
            
        return True, True