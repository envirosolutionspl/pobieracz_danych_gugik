# -*- coding: utf-8 -*-

def classFactory(iface):
    from .pobieracz_danych_gugik import PobieraczDanychGugik
    from . import qgis_feed
    qgis_feed.removeDismissed()
    qgis_feed.updateOnStart()
    return PobieraczDanychGugik(iface)
