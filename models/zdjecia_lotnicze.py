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
            kartaPracy
    ):
        self.url = adresUrlMiniatur
        self.nrSzeregu = nrSzeregu
        self.nrZdjecia = nrZdjecia
        self.rokWykonania = rokWykonania
        self.dataNalotu = dataNalotu
        self.charakterystykaPrzestrzenna = charakterystykaPrzestrzenna
        self.przestrzenBarwna = przestrzenBarwna
        self.zrodloDanych = zrodloDanych
        self.nrZgloszenia = nrZgloszenia
        self.kartaPracy = kartaPracy

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


