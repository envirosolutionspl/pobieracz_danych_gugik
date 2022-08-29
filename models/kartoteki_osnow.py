import datetime
class Kartoteki_osnow:
    def __init__(
            self,
            url,
            rodzaj_katalogu,
            godlo
    ):
        self.url = url
        self.rodzaj_katalogu = rodzaj_katalogu
        self.godlo = godlo

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


