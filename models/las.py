import datetime


class Las:
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
            dt_pzgik
    ):
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
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = int(aktualnoscRok)
        self.dtPzgik = str(dt_pzgik)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


