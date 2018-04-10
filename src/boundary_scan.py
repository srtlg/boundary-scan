import urjtag
from bsdl import bsdlParser
from bsdl_entities import PinMapString

__all__ = ('TestPOD', 'UrJTAGPOD', 'Chain', 'Device')


class TestPOD(object):
    def __init__(self):
        pass

    def initialize_device(self, dev, regexp=None):
        raise NotImplementedError

    def initialize_pins(self):
        raise NotImplementedError

    def query_all_pins_starts(self):
        raise NotImplementedError

    def query_input_pin(self, name):
        """:returns: 0 for low and any other value for high """
        raise NotImplementedError

    def get_scanned_pin_names(self):
        raise NotImplementedError




class UrJTAGPOD(TestPOD):
    def __init__(self, cable):
        super().__init__()
        self.chain = urjtag.chain()
        self.chain.cable(cable)


class Chain(object):
    def __init__(self):
        self.devices = None  # type: list[Device]
        self.pod = None  # type: TestPOD


class Device(object):
    def __init__(self, bsd_ast):
        assert len(bsd_ast.device_package_pin_mappings) == 1
        self._name_to_type = dict([(d.identifier_list[0], d.pin_type) for d in bsd_ast.logical_port_description])
        self._device_package = bsd_ast.device_package_pin_mappings[0].pin_mapping_name.replace('_PACKAGE', '')
        self.component_name = bsd_ast.component_name
        self._name_to_pin = None  # type: dict
        self._pin_to_name = None  # type: dict
        self._name_to_type = self._build_name_to_type(bsd_ast)
        self._build_dicts(bsd_ast)
        self.number_of_pins = len(self._name_to_pin)

    @staticmethod
    def _build_name_to_type(bsd_ast):
        ret = dict()
        for description in bsd_ast.logical_port_description:
            for i in description.identifier_list:
                ret[i] = description.pin_type
        return ret

    @staticmethod
    def _build_name_to_dimension(bsd_ast):
        ret = dict()
        for description in bsd_ast.logical_port_description:
            for i in description.identifier_list:
                ret[i] = description.port_dimension
        return ret

    def _build_dicts(self, bsd_ast):
        self._name_to_pin = dict()
        self._pin_to_name = dict()
        name_to_dimension = self._build_name_to_dimension(bsd_ast)
        pin_map = PinMapString(bsd_ast.device_package_pin_mappings[0].pin_map)
        for name in list(self._name_to_type.keys()):
            dimension = name_to_dimension[name]
            if dimension == 'bit':
                assert len(pin_map[name]) == 1
                pin = int(pin_map.fuzzy_int(pin_map[name][0]))
                self._name_to_pin[name] = pin
                self._pin_to_name[pin] = name
            elif hasattr(dimension, 'bit_vector'):
                for i, pin_str in enumerate(pin_map[name]):
                    pin = pin_map.fuzzy_int(pin_str)
                    namei = '%s_%d' % (name, i+1)
                    self._name_to_pin[namei] = pin
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
