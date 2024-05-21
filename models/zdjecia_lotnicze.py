# -*- coding: utf-8 -*-
import datetime

class ZdjeciaLotnicze:
    def __init__(
            self,
            adresUrlMiniatur,
            nrSzeregu,
            nrZdjecia,
            rokWykonania,
            dataNalotu,
            charakterystykaPrzestrzenna,
            przestrzenBarwna,
            zrodloDanych,
            nrZgloszenia,
            kartaPracy,
            dt_pzgik

    ):
        if adresUrlMiniatur == "":
            self.url = "brak zdjęcia"
        else:
            self.url = adresUrlMiniatur
        self.nrSzeregu = nrSzeregu
        self.nrZdjecia = nrZdjecia
        self.rokWykonania = rokWykonania
        self.dataNalotu = datetime.datetime.strptime(dataNalotu, '%Y-%m-%d').date()
        self.charakterystykaPrzestrzenna = charakterystykaPrzestrzenna
        self.kolor = przestrzenBarwna
        self.zrodloDanych = zrodloDanych
        self.nrZgloszenia = nrZgloszenia
        self.kartaPracy = kartaPracy
        self.dtPzgik = str(dt_pzgik)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


