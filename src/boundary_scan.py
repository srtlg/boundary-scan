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
        self._name_to_pin = dict([(n, int(p.rstrip(','))) for n, p in
                                  [v.split(':') for v in self.ast.device_package_pin_mappings[0].pin_map]])
        self._pin_to_name = dict([(int(p.rstrip(',')), n) for n, p in
                                  [v.split(':') for v in self.ast.device_package_pin_mappings[0].pin_map]])

    def get_package(self) -> str:
        return self.ast.device_package_pin_mappings[0].pin_mapping_name

    def get_pin_name(self, pin) -> str:
        return self._pin_to_name[pin]

    def get_pin(self, name) -> int:
        return self._name_to_pin[name]

    @classmethod
    def from_bsd_file(cls, path):
        with open(path) as text:
            bsd = text.read()
            parser = bsdlParser()
            ast = parser.parse(bsd, 'bsdl_description', parseinfo=False)
            return cls(ast)
