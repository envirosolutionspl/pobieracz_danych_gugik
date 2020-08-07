from qgis.core import QgsCoordinateReferenceSystem
import processing
from qgis.core import *

def pointTo2180(point, sourceCrs, project):
    """zamiana układu na 1992"""
    crsDest = QgsCoordinateReferenceSystem(2180)  # PL 1992
    xform = QgsCoordinateTransform(sourceCrs, crsDest, project)
    point1992 = xform.transform(point)
    return point1992

def createPointsFromLine(layer):
    points = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        for point in geom.densifyByDistance(1000).vertices():
            if point not in points:
                points.append(point)
    return points

def createPointsFromPolygon(layer):
    punktyList = []

    for feat in layer.getFeatures():
        geom = feat.geometry()
        bbox = geom.boundingBox()
        if bbox.area() < 1000000:
            punktyList.append(bbox.center())
        else:
            params = {
                'TYPE':0,
                'EXTENT':bbox,
                'HSPACING':1000,
                'VSPACING':1000,
                'HOVERLAY':0,
                'VOVERLAY':0,
                'CRS':QgsCoordinateReferenceSystem('EPSG:2180'),
                'OUTPUT':'TEMPORARY_OUTPUT'
            }
            proc = processing.run("qgis:creategrid", params)
            # proc = processing.run("native:creategrid", params)
            punkty = proc['OUTPUT']

            # params = {
            #     'INPUT': punkty,
            #     'OVERLAY': layer,
            #     'OUTPUT': 'TEMPORARY_OUTPUT'}
            #
            # proc = processing.run("qgis:clip", params)
            # punkty = proc['OUTPUT']
            #
            # params = {
            #     'INPUT': punkty,
            #     'OUTPUT': 'TEMPORARY_OUTPUT'}
            # proc = processing.run("qgis:multiparttosingleparts", params)
            # punkty = proc['OUTPUT']


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

