import datetime


class Las:
    def __init__(
            self,
            url,
            godlo,
            aktualnosc,
            charakterystykaPrzestrzenna,
            format,
            bladSredniWysokosci,
            ukladWspolrzednych,
            ukladWysokosci,
            calyArkuszWyeplnionyTrescia,
            modulArchiwizacji,
            zrodloDanych,
            kolor,
            numerZgloszeniaPracy,
            aktualnoscRok,
            nazwaPliku,
            idSerie,
            isLaz=False
    ):
        self.url = url
        self.godlo = godlo
        self.aktualnosc = datetime.datetime.strptime(aktualnosc, '%Y/%m/%d').date()
        self.charakterystykaPrzestrzenna = float(charakterystykaPrzestrzenna.split()[0])
        self.format = format
        self.bladSredniWysokosci = float(bladSredniWysokosci)
        self.ukladWspolrzednych = ukladWspolrzednych
        self.ukladWysokosci = ukladWysokosci
        self.calyArkuszWyeplnionyTrescia = calyArkuszWyeplnionyTrescia
        self.modulArchiwizacji = modulArchiwizacji
        self.zrodloDanych = zrodloDanych
        self.kolor = kolor
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = int(aktualnoscRok)
        self.nazwaPliku = nazwaPliku
        self.idSerie = idSerie
        self.urlLaz = "https://opendata.geoportal.gov.pl/NumDaneWys/DanePomiaroweLAZ/" + idSerie + "/" + nazwaPliku + ".laz"
        if isLaz:
            self.url = self.urlLaz
        # print(self.urlLaz)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


