import datetime


class Nmt:
    def __init__(
            self,
            url,
            godlo,
            aktualnosc,
            format,
            charakterystykaPrzestrzenna,
            bladSredniWysokosci,
            bladSredniPolozenia,
            ukladWspolrzednychPoziomych,
            ukladWspolrzednychPionowych,
            calyArkuszWypelnionyTrescia,
            modulArchiwizacji,
            numerZgloszeniaPracy,
            aktualnoscRok,
            zrDanych,
            dt_pzgik
    ):
        #zerowanie niepotrzebnych wartości
        bladSredniPolozenia = 0

        self.url = url
        self.godlo = godlo
        self.aktualnosc = datetime.datetime.strptime(aktualnosc, '%Y-%m-%d').date()
        self.charakterystykaPrzestrzenna = float(charakterystykaPrzestrzenna.split()[0])
        self.format = format
        self.bladSredniWysokosci = float(bladSredniWysokosci)
        self.bladSredniPolozenia = float(bladSredniPolozenia)
        self.ukladWspolrzednych = ukladWspolrzednychPoziomych
        self.ukladWysokosci = ukladWspolrzednychPionowych
        self.calyArkuszWyeplnionyTrescia = calyArkuszWypelnionyTrescia
        self.modulArchiwizacji = modulArchiwizacji
        self.zrDanych = zrDanych
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = int(aktualnoscRok)
        self.dt_pzgik = str(dt_pzgik)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


