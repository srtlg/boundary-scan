import urjtag
from bsdl import bsdlParser
from bsdl_entities import PinMapString

__all__ = ('TestPOD', 'UrJTAGPOD', 'Chain', 'Device')


class TestPOD(object):
    pass


class UrJTAGPOD(TestPOD):
    def __init__(self, cable):
        self.chain = urjtag.chain()
        self.chain.cable(cable)


class Chain(object):
    def __init__(self):
        self.devices = None  # type: list[Device]
        self.pod = None  # type: TestPOD


class Device(object):
    def __init__(self, bsd_ast):
        assert len(bsd_ast.device_package_pin_mappings) == 1
        assert all([len(d.identifier_list) == 1 for d in bsd_ast.logical_port_description])
        self._name_to_type = dict([(d.identifier_list[0], d.pin_type) for d in bsd_ast.logical_port_description])
        self._device_package = bsd_ast.device_package_pin_mappings[0].pin_mapping_name
        self._name_to_pin = None  # type: dict
        self._pin_to_name = None  # type: dict
        self._build_dicts(bsd_ast)

    def _build_dicts(self, bsd_ast):
        self._name_to_pin = dict()
        self._pin_to_name = dict()
        name_to_dimension = dict([(d.identifier_list[0], d.port_dimension) for d in bsd_ast.logical_port_description])
        pin_map = PinMapString(bsd_ast.device_package_pin_mappings[0].pin_map)
        for name in list(self._name_to_type.keys()):
            dimension = name_to_dimension[name]
            if dimension == 'bit':
                assert len(pin_map[name]) == 1
                pin = int(pin_map.fuzzy_int(pin_map[name][0]))
                self._name_to_pin[name] = pin
                self._pin_to_name[pin] = name
            elif hasattr(dimension, 'bit_vector'):
                for i, pin in enumerate(pin_map[name]):
                    namei = '%s_%d' % (name, i+1)
                    self._name_to_pin[namei] = pin_map.fuzzy_int(pin)
                    self._pin_to_name[pin] = namei
                    self._name_to_type[namei] = self._name_to_type[name]
            else:
                raise RuntimeError('unhandled dimension %s' % dimension)

    def get_package(self) -> str:
        return self._device_package

    def get_pin_name(self, pin) -> str:
        return self._pin_to_name[pin]

    def get_pin(self, name) -> int:
        return self._name_to_pin[name]

    def get_pin_type(self, pin) -> str:
        return self._name_to_type[self.get_pin_name(pin)]

    @staticmethod
    def is_jtag_name(name: str):
        uname = name.upper()
        if uname.endswith('TDI'):
            return True
        elif uname.endswith('TMS'):
            return True
        elif uname.endswith('TCK'):
            return True
        elif uname.endswith('TRST'):
            return True
        elif uname.endswith('TDO'):
            return True
        else:
            return False

    @classmethod
    def from_bsd_file(cls, path):
        with open(path) as text:
            bsd = text.read()
            parser = bsdlParser()
            ast = parser.parse(bsd, 'bsdl_description', parseinfo=False)
            return cls(ast)
