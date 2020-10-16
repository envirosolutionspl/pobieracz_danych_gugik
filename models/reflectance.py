import datetime


class Reflectance:
    def __init__(
            self,
            url,
            godlo,
            aktualnosc,
            wielkoscPiksela,
            ukladWspolrzednych,
            modulArchiwizacji,
            zrodloDanych,
            metodaZapisu,
            zakresIntensywnosci,
            numerZgloszeniaPracy,
            aktualnoscRok
    ):
        self.url = url
        self.godlo = godlo
        self.aktualnosc = datetime.datetime.strptime(aktualnosc, '%Y/%m/%d').date()
        self.wielkoscPiksela = float(wielkoscPiksela)
        self.ukladWspolrzednych = ukladWspolrzednych
        self.modulArchiwizacji = modulArchiwizacji
        self.zrodloDanych = zrodloDanych
        self.metodaZapisu = metodaZapisu
        self.zakresIntensywnosci = int(zakresIntensywnosci)
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = int(aktualnoscRok)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


