import datetime
class Wizualizacja_karto:
    def __init__(
            self,
            url,
            data,
            godlo,
            skala
    ):
        self.url = url
        self.data = data
        self.godlo = godlo
        self.skala = skala

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


