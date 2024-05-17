import datetime


class Aerotriangulacja:
    def __init__(
            self,
            url,
            id,
            zgloszenie,
            dt_pzgik
    ):
        self.url = url
        self.id = id
        self.zgloszenie = zgloszenie
        self.dtPzgik = dt_pzgik

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(('url', self.url))


