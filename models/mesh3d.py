class Mesh3d:
    def __init__(
            self,
            url,
            modul,
            aktualnosc,
            format,
            bladSredniWysokosci,
            bladSredniPolozenia,
            ukladWspolrzednychPoziomych,
            ukladWspolrzednychPionowych,
            modulArchiwizacji,
            numerZgloszeniaPracy,
            aktualnoscRok,
            zrDanych,
            charPrzestrzZrDanych,
            dt_pzgik
    ):
        self.url = url
        self.modul = modul
        self.aktualnosc = aktualnosc
        self.format = format
        self.bladSredniWysokosci = bladSredniWysokosci
        self.bladSredniPolozenia = bladSredniPolozenia
        self.ukladWspolrzednychPoziomych = ukladWspolrzednychPoziomych
        self.ukladWspolrzednychPionowych = ukladWspolrzednychPionowych
        self.modulArchiwizacji = modulArchiwizacji
        self.numerZgloszeniaPracy = numerZgloszeniaPracy
        self.aktualnoscRok = aktualnoscRok
        self.zrDanych = zrDanych
        self.charPrzestrzZrDanych = charPrzestrzZrDanych
        self.dt_pzgik = dt_pzgik

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


