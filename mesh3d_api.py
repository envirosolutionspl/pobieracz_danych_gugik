import re

from .models.mesh3d import Mesh3d
from . import service_api

URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/ModeleSiatkowe3D?"
c = re.compile(r"\{{1}.*\}{1}")


def getMesh3dListbyPoint1992(point):
    x = point.x()
    y = point.y()
    LAYERS = [
        'SkorowidzeModeleSiatkowe3D'
    ]

    PARAMS = {
        'SERVICE': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': ','.join(LAYERS),
        'styles': '',
        'srs': 'EPSG:2180',
        'bbox': '%f,%f,%f,%f' % (x-50, y-50, x+50, y+50),
        'width': '101',
        'height': '101',
        'format': 'image/png',
        'transparent': 'true',
        'query_layers': ','.join(LAYERS),
        'i': '50',
        'j': '50',
        'INFO_FORMAT': 'text/html'
    }
    resp = service_api.getRequest(params=PARAMS, url=URL)
    if resp[0]:
        aeros = c.findall(resp[1])
        mesh_objs = []
        for aero in aeros:
            element = aero.strip("{").strip("}").split(',')
            params = {}
            for el in element:
                item = el.strip().split(':')
                val = item[1].strip('"')
                if len(item) > 2:
                    val = ":".join(item[1:]).strip('"')
                params[item[0]] = val
            mesh = Mesh3d(**params)
            mesh_objs.append(mesh)
        return mesh_objs
    else:
        return None
