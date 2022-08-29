import datetime
class Linie_mozaikowania:
    def __init__(
            self,
            url,
            id,
            zgloszenie
    ):
        self.url = url
        self.id = id
        self.zgloszenie = zgloszenie

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


