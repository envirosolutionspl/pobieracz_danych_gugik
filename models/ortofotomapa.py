import datetime
class Ortofotomapa:
    def __init__(
            self,
            url,
            godlo,
            aktualnosc,
            wielkoscPiksela,
            ukladWspolrzednych,
            calyArkuszWyeplnionyTrescia,
            modulArchiwizacji,
            rozmiarPlikuMB,
            zrodloDanych,
            kolor,
            numerZgloszeniaPracy,
            aktualnoscRok,
            dt_pzgik,
            
    ):
        rozmiarPlikuMB = None

        self.url = url
        self.godlo = godlo
        self.aktualnosc = datetime.datetime.strptime(aktualnosc, '%Y-%m-%d').date()
        self.wielkoscPiksela = float(wielkoscPiksela)
        self.ukladWspolrzednych = ukladWspolrzednych
        self.calyArkuszWyeplnionyTrescia = calyArkuszWyeplnionyTrescia
        self.modulArchiwizacji = modulArchiwizacji
        self.rozmiarPlikuMB = rozmiarPlikuMB
        self.zrodloDanych = zrodloDanych
        self.kolor = kolor
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = int(aktualnoscRok)
        self.dt_pzgik = dt_pzgik

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


