import datetime
from typing import List, Dict, Any
import json
import os
import processing
import sys
import time
from . import PLUGIN_NAME
from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsNetworkAccessManager,
    QgsBlockingNetworkRequest
)
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer, QT_VERSION_STR
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from .constants import (
    TIMEOUT_MS,
    MAX_ATTEMPTS,
    ULDK_URL,
    QT_VER,
    CANCEL_CHECK_MS,
    HTTP_ERROR_THRESHOLD,
    DEFAULT_ENCODING,
    NETWORK_ATTRS,
    ERR_TIMEOUT,
    ERR_NONE,
    ERR_CANCELED,
    REDIRECT_POLICY_NAME,
    REDIRECT_POLICY_NO_LESS_SAFE,
    DEFAULT_REDIRECT_POLICY,
)

import lxml.etree as ET



class LayersUtils:
    
    @staticmethod
    def pointToCrs(point, project, dest_crs):
        """zamiana układu na wybrany układ"""
        crsDest = QgsCoordinateReferenceSystem(f'EPSG:{dest_crs}')
        xform = QgsCoordinateTransform(project.crs(), crsDest, project)
        return xform.transform(point)

    @staticmethod
    def layerToCrs(layer, dest_crs):
        """zamiana układu na 1992"""
        proc = processing.run("native:reprojectlayer",
                    {'INPUT': layer,
                        'TARGET_CRS': QgsCoordinateReferenceSystem(f'EPSG:{dest_crs}'),
                        'OUTPUT': 'TEMPORARY_OUTPUT'})
        return proc['OUTPUT']

    @staticmethod
    def createPointsFromPointLayer(layer):
        points = []
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if geom.isMultipart():
                mp = geom.asMultiPoint()
                points.extend(mp)
            else:
                points.append(geom.asPoint())
        return points

    @staticmethod
    def createPointsFromLineLayer(layer, density):
        points = []
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom or geom.isNull():
                continue
            densified_geom = geom.densifyByDistance(density)
            for point in densified_geom.vertices():
                if point not in points:
                    points.append(point)
        return points

    @staticmethod
    def createPointsFromPolygon(layer, density):
        punktyList = []

        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom:
                continue
            bbox = geom.boundingBox()
            if bbox.width() <= density or bbox.height() <= density:
                punktyList.append(bbox.center())
            else:
                params = {
                    'TYPE':0,
                    'EXTENT':bbox,
                    'HSPACING':density,
                    'VSPACING':density,
                    'HOVERLAY':0,
                    'VOVERLAY':0,
                    'CRS':QgsCoordinateReferenceSystem('EPSG:2180'),
                    'OUTPUT':'memory:TEMPORARY_OUTPUT'
                }
                proc = processing.run("qgis:creategrid", params)
                punkty = proc['OUTPUT']


                for pointFeat in punkty.getFeatures():
                    point = pointFeat.geometry().asPoint()
                    if geom.contains(point):
                        punktyList.append(point)


                # dodanie werteksów poligonu
                # uproszczenie geometrii
                geom2 = geom.simplify(400 if density < 1000 else 800)
                for point in geom2.vertices():
                    punktyList.append(point)
        return punktyList
    
    @staticmethod
    def removeLayer(project, canvas, layer_id):
        layer = project.mapLayer(layer_id)
        if layer:
            project.removeMapLayer(layer_id)
            canvas.refresh()

class FilterUtils:
    
    @staticmethod
    def onlyNewest(data_file_list):
        """filtruje listę tylko do najnowszych plików według arkuszy"""
        updated_dict = {}
        for data_file in data_file_list:
            godlo = data_file.get('godlo')
            aktualnosc = data_file.get('aktualnosc')
            if godlo not in updated_dict or aktualnosc > updated_dict[godlo].get('aktualnosc'):
                updated_dict[godlo] = data_file
        return list(updated_dict.values())

    @staticmethod
    def removeDuplicatesFromListOfDicts(dict_list: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        seen = set()
        unique_dict_list = []
        for _dict in dict_list:
            fset = frozenset(_dict.items())
            if fset not in seen:
                seen.add(fset)
                unique_dict_list.append(_dict)
        return unique_dict_list

class FileUtils:
    
    @staticmethod
    def openFile(filename):
        """otwiera folder/plik niezależnie od systemu operacyjnego"""
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


    @staticmethod
    def createReport(file_path, headers, obj_list, file_name_from_url=True):
        file_path = f'{file_path}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
        if file_name_from_url:
            obj_list = [{**obj, 'url': obj.get('url', '').split('/')[-1]} for obj in obj_list]
        valid_headers = {header: key for header, key in headers.items() if
                        any(key in obj for obj in obj_list)}
        with open(file_path, 'w') as report_file:
            report_file.write(','.join(valid_headers.keys()) + '\n')
            for obj in obj_list:
                row = [str(obj.get(key, '')) for key in valid_headers.values()]
                report_file.write(','.join(row) + '\n')

class MessageUtils:

    @staticmethod
    def pushMessageBoxCritical(parent, title: str, message: str):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))

        msg_box.exec()

    @staticmethod
    def pushMessageBoxInfo(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))

        msg_box.exec()

    @staticmethod
    def pushMessageBoxYesNo(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def pushMessage(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            'Informacja',
            message,
            level=Qgis.Info,
            duration=10
        )
    
    @staticmethod
    def pushSuccess(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            "Sukces",
            message,
            level=Qgis.Success,
            duration=0
        )

    @staticmethod
    def pushWarning(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            'Ostrzeżenie',
            message,
            level=Qgis.Warning,
            duration=10
        )

    @staticmethod
    def pushLogInfo(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Info
        )

    @staticmethod
    def pushLogWarning(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Warning
        )

    @staticmethod
    def pushLogCritical(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Critical
        )

class NetworkUtils:
    def __init__(self):
        self.manager = QgsNetworkAccessManager.instance()

    def _handle_reply_error(self, reply, url_str):
        """Centralna obsługa błędów sieciowych i HTTP"""
        from .constants import HTTP_ERROR_THRESHOLD, MSG_HTTP_ERROR, MSG_TIMEOUT, MSG_NETWORK_ERROR
        error_code = reply.error()
        error_str = reply.errorString()
        
        status_attr = self._get_attribute_enum(NETWORK_ATTRS['HTTP_STATUS'])
        reason_attr = self._get_attribute_enum(NETWORK_ATTRS['HTTP_REASON'])
        timeout_err = self._get_error_enum(ERR_TIMEOUT)

        http_status = reply.attribute(status_attr)
        http_reason = reply.attribute(reason_attr)
        
        if http_status and http_status >= HTTP_ERROR_THRESHOLD:
            return False, MSG_HTTP_ERROR.format(http_status, http_reason)
        
        if error_code == timeout_err:
            return False, MSG_TIMEOUT.format(url_str)
            
        return False, MSG_NETWORK_ERROR.format(error_str, url_str)

    def _has_error_occurred(self, reply):
        """Sprawdza czy wystąpił błąd w odpowiedzi"""
        no_error = self._get_error_enum(ERR_NONE)
        return reply.error() != no_error

    def _get_attribute_enum(self, attr_name):
        """Pobiera atrybut QNetworkRequest"""
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            if hasattr(QNetworkRequest, 'Attribute'):
                val = getattr(QNetworkRequest.Attribute, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkRequest, attr_name, None)

    def _get_error_enum(self, attr_name):
        """Pobiera kod błędu QNetworkReply"""
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            if hasattr(QNetworkReply, 'NetworkError'):
                val = getattr(QNetworkReply.NetworkError, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkReply, attr_name, None)

    def _set_attributes(self, request, timeout_ms):
        """Ustawia atrybuty zapytania"""
        redirect_attr = self._get_attribute_enum(NETWORK_ATTRS['REDIRECT'])
        if redirect_attr is not None:
            redirect_policy_class = getattr(QNetworkRequest, REDIRECT_POLICY_NAME, QNetworkRequest)
            redirect_policy = getattr(redirect_policy_class, REDIRECT_POLICY_NO_LESS_SAFE, DEFAULT_REDIRECT_POLICY)
            request.setAttribute(redirect_attr, redirect_policy)
        
        timeout_attr = self._get_attribute_enum(NETWORK_ATTRS['TIMEOUT'])
        if timeout_attr is not None:
            request.setAttribute(timeout_attr, timeout_ms)
            
    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS):
        from .constants import MSG_EMPTY_CONTENT
        q_url = QUrl(url)
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(str(key), str(value))
            q_url.setQuery(query)
            
        request = QNetworkRequest(q_url)
        self._set_attributes(request, timeout_ms)
        
        blocking_request = QgsBlockingNetworkRequest()
        error_code = blocking_request.get(request)
        reply_content = blocking_request.reply()
        
        if error_code != QgsBlockingNetworkRequest.NoError:
            return self._handle_reply_error(reply_content, url)

        raw_data = reply_content.content()
        if len(raw_data) == 0:
            return False, MSG_EMPTY_CONTENT.format(url)
            
        try:
            data = bytes(raw_data).decode(DEFAULT_ENCODING)
            return True, data
        except UnicodeDecodeError:
            return True, f"BinaryData: {len(raw_data)} bytes"

    def fetchJson(self, url, params=None, timeout_ms=TIMEOUT_MS):
        from .constants import MSG_JSON_DECODE_ERROR
        success, result = self.fetchContent(url, params, timeout_ms)
        if not success:
            return False, result
        try:
            return True, json.loads(result)
        except json.JSONDecodeError as e:
            return False, MSG_JSON_DECODE_ERROR.format(str(e))
  
    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS):
        from .constants import MSG_FILE_WRITE_ERROR, MSG_DOWNLOAD_CANCELED
        q_url = QUrl(url)
        request = QNetworkRequest(q_url)
        self._set_attributes(request, timeout_ms)

        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        event_loop = QEventLoop()
        reply = self.manager.get(request)
        try:
            with open(dest_path, 'wb') as f:
                def handleReadyRead():
                    if reply.bytesAvailable() > 0:
                        f.write(reply.readAll().data())

                def handleFinished():
                    if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
                        event_loop.quit()
                    else:
                        event_loop.exit()

                reply.readyRead.connect(handleReadyRead)
                reply.finished.connect(handleFinished)

                cancel_timer = QTimer()
                cancel_timer.timeout.connect(lambda: reply.abort() if (obj and obj.isCanceled()) else None)
                cancel_timer.start(CANCEL_CHECK_MS)
                
                if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
                    event_loop.exec()
                else:
                    event_loop.exec_()

                cancel_timer.stop()
                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
        except IOError as e:
            return False, MSG_FILE_WRITE_ERROR.format(str(e))
            
        if self._has_error_occurred(reply):
            canceled_error = self._get_error_enum(ERR_CANCELED)
            if reply.error() == canceled_error:
                reply.deleteLater()
                return False, MSG_DOWNLOAD_CANCELED
            
            error_res = self._handle_reply_error(reply, url)
            reply.deleteLater()
            return error_res

        reply.deleteLater()
        return True, True

class ServiceAPI:
    def __init__(self):
        self.network_utils = NetworkUtils()

    def getRequest(self, params, url):
        attempt = 0
        while attempt <= MAX_ATTEMPTS:
            attempt += 1
            success, result = self.network_utils.fetchContent(url, params=params, timeout_ms=TIMEOUT_MS * 2)
            if success:
                return True, result
            time.sleep(2)
        return False, "Nieudana próba połączenia"

    def retreiveFile(self, url, destFolder, obj):
        file_name = url.split('/')[-1]
        if '?' in file_name:
            file_name = (file_name.split('?')[-1].replace('=', '_')) + '.zip'

        if 'Budynki3D' in url:
            if 'LOD1' in url:
                file_name = f"Budynki_3D_LOD1_{file_name}"
            elif 'LOD2' in url:
                file_name = f"Budynki_3D_LOD2_{file_name}"

            if len(url.split('/')) == 9:
                file_name = url.split('/')[6] + '_' + file_name

        elif 'PRG' in url:
            file_name = f"PRG_{file_name}"
        elif 'bdot10k' in url and 'Archiwum' not in url:
            file_name = f"bdot10k_{file_name}"
        elif 'Archiwum' in url and 'bdot10k' in url:
            file_name = "archiwalne_bdot10k_" + url.split('/')[5] + '_' + file_name
        elif 'bdoo' in url:
            file_name = "bdoo_" + 'rok' + url.split('/')[4] + '_' + file_name
        elif 'ZestawieniaZbiorczeEGiB' in url:
            file_name = "ZestawieniaZbiorczeEGiB_" + 'rok' + url.split('/')[4] + '_' + file_name
        elif 'osnowa' in url:
            file_name = f"podstawowa_osnowa_{file_name}"

        path = os.path.join(destFolder, file_name)
        self.cleanupFile(path)

        success, result = self.network_utils.downloadFile(url, path, obj=obj)
        if success:
            FileUtils.openFile(destFolder)
            return True, True
        self.cleanupFile(path)
        return False, result


    def getAllLayers(self, url, service="WMS"):
        # Poprawne parametry GetCapabilities
        params = {
            "SERVICE": service,
            "REQUEST": "GetCapabilities",
            "VERSION": "1.3.0",
        }

        ok, payload = self.getRequest(params, url)
        if not ok or not payload:
            return []

        # Parsowanie XML
        parser = ET.XMLParser(recover=True)
        try:
            root = ET.fromstring(payload.encode(DEFAULT_ENCODING), parser=parser)
        except Exception:
            # gdyby serwer odesłał już bytes w UTF-8
            root = ET.fromstring(payload, parser=parser)

        # Obsługa przestrzeni nazw (lub jej braku)
        #    lxml: root.nsmap może mieć None dla domyślnego ns
        ns_uri = None
        try:
            ns_uri = root.nsmap.get(None)  # domyślna przestrzeń nazw, np. 'http://www.opengis.net/wms'
        except AttributeError:
            ns_uri = None  # brak nsmap -> brak przestrzeni nazw

        layers = []

        if ns_uri:
            # XPath: tylko 'Layer' mające 'Name' -> bierzemy 'Layer/Name'
            ns = {"wms": ns_uri}
            names = root.xpath(".//wms:Capability//wms:Layer[wms:Name]/wms:Name", namespaces=ns)
            layers = [el.text for el in names if el is not None and el.text]
        else:
            # Bez przestrzeni nazw – klasyczne ścieżki
            for layer in root.findall(".//Layer"):
                name_el = layer.find("Name")
                if name_el is not None and name_el.text:
                    layers.append(name_el.text)

        # zwróć tylko unikalne nazwy w kolejności wystąpienia
        seen = set()
        unique_layers = []
        for n in layers:
            if n not in seen:
                seen.add(n)
                unique_layers.append(n)

        return unique_layers



    def checkInternetConnection(self):
        # próba połączenia z serwerem np. gugik
        success, _ = self.network_utils.fetchContent(ULDK_URL, timeout_ms=TIMEOUT_MS)
        return success


    def cleanupFile(self, path):
        if os.path.exists(path):
            try:
                os.remove(path)
            except PermissionError:
                MessageUtils.pushLogWarning(f'Nie udało się usunąć pliku {path} - plik jest używany przez inny proces')
            except OSError as e:
                MessageUtils.pushLogWarning(f"Błąd podczas usuwania pliku {path}: {e}")

class ParsingUtils:

    @staticmethod
    def getSafelyFloat(value):
        """Konwertuje wartość na float, obsługując przecinki i jednostki (np. '1.00 m')."""
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        if not isinstance(value, str):
            return 0.0

        val_clean = value.replace(',', '.')

        try:
            parts = val_clean.split()
            if not parts:
                return 0.0
            val_numeric_candidate = parts[0]
        except IndexError:
            MessageUtils.pushLogWarning(f"Błąd konwersji wartości na float: {value}")
            return 0.0
        try:
            return float(val_numeric_candidate)
        except ValueError:
            MessageUtils.pushLogWarning(f"Błąd konwersji wartości na float: {value}")
            return 0.0
        except TypeError:
            MessageUtils.pushLogWarning(f"Błąd konwersji wartości na float: {value}")
            return 0.0

class VersionUtils:

    @staticmethod
    def isCompatibleQtVersion(cur_version, tar_version):
        return cur_version.startswith(QT_VER[tar_version])