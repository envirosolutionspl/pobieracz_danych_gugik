import datetime
from qgis.core import QgsCoordinateReferenceSystem
import processing, sys, os
from qgis.core import *


def onlyNewest(data_file_list):
    """filtruje listę tylko do najnowszych plików według arkuszy"""
    updated_dict = {}
    for data_file in data_file_list:
        godlo = data_file.get('godlo')
        aktualnosc = data_file.get('aktualnosc')
        if godlo not in updated_dict or aktualnosc > updated_dict[godlo].get('aktualnosc'):
            updated_dict[godlo] = data_file
    return list(updated_dict.values())


def openFile(filename):
    """otwiera folder/plik niezależnie od systemu operacyjnego"""
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        import subprocess
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def pointTo2180(point, sourceCrs, project):
    """zamiana układu na 1992"""
    crsDest = QgsCoordinateReferenceSystem('EPSG:2180')  # PL 1992
    xform = QgsCoordinateTransform(sourceCrs, crsDest, project)
    point1992 = xform.transform(point)

    return point1992

def layerTo2180(layer):
    """zamiana układu na 1992"""
    proc = processing.run("native:reprojectlayer",
                   {'INPUT': layer,
                    'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
    return proc['OUTPUT']

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

def createPointsFromLineLayer(layer, density):
    points = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        for point in geom.densifyByDistance(density).vertices():
            if point not in points:
                points.append(point)
    return points

def createPointsFromPolygon(layer, density=1000):
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
            geom2 = geom.simplify(800)
            for point in geom2.vertices():
                punktyList.append(point)
    return punktyList


def create_report(file_path, headers, obj_list, file_name_from_url=True):
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
