# -*- coding: utf-8 -*-

def classFactory(iface):

    from .pobieracz_danych_gugik import PobieraczDanychGugik

    return PobieraczDanychGugik(iface)
