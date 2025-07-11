# -*- coding: utf-8 -*-

import os 

PLUGIN_NAME = ''
PLUGIN_VERSION = ''
with open(os.path.join(os.path.dirname(__file__), 'metadata.txt'), 'r') as pluginMetadataFile:
    for line in pluginMetadataFile:
        if line.startswith("version="):
            PLUGIN_VERSION = line.strip().split('=')[-1]
        elif line.startswith("name="):
            PLUGIN_NAME = line.strip().split('=')[-1]

def classFactory(iface):

    from .pobieracz_danych_gugik import PobieraczDanychGugik

    return PobieraczDanychGugik(iface)
