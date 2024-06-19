import re

expr = re.compile(r"\{{1}.*\}{1}")

class WMS:
    def __init__(self, **attributes):
        self.attributes = attributes

    def __getattr__(self, item):
        return self.attributes.get(item, None)

    def __eq__(self, other):
        return self.attributes.get('url') == other.attributes.get('url')

    def __hash__(self):
        return hash(('url', self.attributes.get('url')))


def get_wms_objects(request_response):
    if not request_response[0]:
        return None
    req_elements = expr.findall(request_response[1])
    req_list = []
    for req_element in req_elements:
        element = req_element.strip("{").strip("}").split(',')
        attributes = {}
        for el in element:
            item = el.strip().split(':')
            key = item[0].strip('"')
            val = item[1].strip('"')
            if len(item) > 2:
                val = ":".join(item[1:]).strip('"')
            attributes[key] = val
        processed_elem = WFS(**attributes)
        req_list.append(processed_elem)
    return req_list
