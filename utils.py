from qgis.core import QgsCoordinateReferenceSystem
import processing
from qgis.core import *

def pointTo2180(point, sourceCrs, project):
    """zamiana układu na 1992"""
    crsDest = QgsCoordinateReferenceSystem(2180)  # PL 1992
    xform = QgsCoordinateTransform(sourceCrs, crsDest, project)
    point1992 = xform.transform(point)
    return point1992

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
        bbox = geom.boundingBox()
        if bbox.area() < density ** 2:
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

