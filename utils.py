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
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager 
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
    MSG_FILE_WRITE_ERROR, 
    MSG_DOWNLOAD_CANCELED, 
    MSG_EMPTY_CONTENT, 
    MSG_JSON_DECODE_ERROR, 
    MSG_HTTP_ERROR, 
    MSG_TIMEOUT, 
    MSG_NETWORK_ERROR,
    MSG_NO_CONNECTION
)
from .network.http_adapter import FallbackHttpAdapter
from functools import partial
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

class ServiceAPI:
    def __init__(self, parent=None):
        if parent:
            self.iface = parent.iface
        else:
            self.iface = None
        self.http_adapter = FallbackHttpAdapter()

    def getRequest(self, params, url):
        attempt = 0
        while attempt <= MAX_ATTEMPTS:
            attempt += 1
            is_success, result = self.http_adapter.fetchContent(url, params=params, timeout_ms=TIMEOUT_MS * 2)
            if is_success:
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

        is_success, result = self.http_adapter.downloadFile(url, path, obj=obj)
        if is_success:
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
        is_success, _ = self.http_adapter.fetchContent(ULDK_URL, timeout_ms=TIMEOUT_MS)
        if not is_success and self.iface:
            MessageUtils.pushWarning(self.iface, MSG_NO_CONNECTION)
        return is_success


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