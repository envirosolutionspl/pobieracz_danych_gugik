from .utils import getTypenamesFromWFS

resp = getTypenamesFromWFS('https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze')
print(resp[1])

"""
wfsUrl = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze'
layer = iface.activeLayer()
feat = next(layer.getFeatures())
geom = feat.geometry()
wkt = geom.asWkt()
print(wkt)
#wkt =
dsu = QgsDataSourceUri()
dsu.setParam( 'url', wfsUrl )
dsu.setParam( 'version', '2.0.0' )
dsu.setParam( 'typename', 'gugik:SkorowidzOrtofomapy2020')
#dsu.setParam( 'maxNumFeatures', '10')
dsu.setParam( 'srsname', 'urn:ogc:def:crs:EPSG::3857')
dsu.setParam( 'filter', "intersects($geometry, geomFromWKT('%s'))" % wkt)

#dsu.setParam( 'filter', "intersects($geometry, geomFromWKT('Polygon ((17.84319299999999942 52.99999700000000047, 18.18789100000000047 52.93750200000000206, 18.31216900000000081 52.79166599999999931, 18.06204899999999824 52.77083199999999863, 17.84430300000000003 52.77083900000000227, 17.84319299999999942 52.99999700000000047))'))")
l = QgsVectorLayer( dsu.uri(), "jj2021", "WFS" )
QgsProject.instance().addMapLayer(l)
"""

