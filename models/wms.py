import re



class WMS:
    def __init__(self, **attributes):
        self.attributes = attributes

    def __getattr__(self, item):
        return self.attributes.get(item, None)

    def __eq__(self, other):
        return self.attributes.get('url') == other.attributes.get('url')

    def __hash__(self):
        return hash(('url', self.attributes.get('url')))


