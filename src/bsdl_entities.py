from bsdl_entities_parser import bsdlEntitiesParser


class PinMapString(object):
    def __init__(self, list_of_str):
        string = ''.join(list_of_str)
        parser = bsdlEntitiesParser()
        ast = parser.parse(string, 'pin_map_string', parseinfo=False)
        self._name_to_pins = dict([(v.port_name, v.pin_list) for v in ast.port_map])
        self._prefixed = False

    def __getitem__(self, item):
        return self._name_to_pins[item]

    def fuzzy_int(self, value):
        if value.startswith('P'):
            return int(value[1:])
        else:
            return int(value)

