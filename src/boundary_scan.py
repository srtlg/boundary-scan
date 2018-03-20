import urjtag
from bsdl import bsdlParser

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
        self.ast = bsd_ast
        assert len(self.ast.device_package_pin_mappings) == 1
        assert all([len(d.identifier_list) == 1 for d in self.ast.logical_port_description])
        self._name_to_pin = dict([(n, int(p.rstrip(','))) for n, p in
                                  [v.split(':') for v in self.ast.device_package_pin_mappings[0].pin_map]])
        self._pin_to_name = dict([(int(p.rstrip(',')), n) for n, p in
                                  [v.split(':') for v in self.ast.device_package_pin_mappings[0].pin_map]])
        self._name_to_type = dict([(d.identifier_list[0], d.pin_type) for d in self.ast.logical_port_description])

    def get_package(self) -> str:
        return self.ast.device_package_pin_mappings[0].pin_mapping_name

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
