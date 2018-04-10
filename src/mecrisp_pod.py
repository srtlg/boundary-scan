"""
Use Mecrisp to query the pin states

If run as toplevel it displays the pin state
"""
import os.path as osp
import argparse
import serial
import tkinter

from boundary_scan import TestPOD, Device
from simple_view import DevicePlotter


class MecrispPOD(TestPOD):
    def __init__(self, port):
        super().__init__()
        self.input_pins = []
        self._serial = serial.Serial(port=port, timeout=0.01)
        self._serial.write(b"\n")

    def _wait_for_ok(self):
        block = ''
        while True:
            block += self._serial.read(512).decode('utf-8')
            if block.endswith('ok.\n'):
                break
        return block

    def _enter_command(self, cmd):
        self._wait_for_ok()
        self._serial.write(cmd.encode('utf-8') + b"\n")
        ret = self._wait_for_ok()
        self._serial.write(b'\n')
        pos = ret.find(cmd)
        assert pos >= 0
        return ret[pos + len(cmd):].replace('ok.\n', '')

    def initialize_device(self, dev: Device):
        for i in range(dev.number_of_pins):
            pin = i + 1
            pin_type = dev.get_pin_type(pin)
            if pin_type == 'inout' or pin_type == 'in':
                self.input_pins.append(dev.get_pin_name(pin))

    def initialize_pins(self):
        for name in self.input_pins:
            self._enter_command('IMODE-FLOAT %s io-mode!' % name)

    def query_input_pin(self, name):
        ret = self._enter_command('%s io@ .' % name)
        return int(ret)

    def __del__(self):
        if hasattr(self, '_serial'):
            self._serial.close()


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('bsd_file')
    p.add_argument('port')
    return p.parse_args()


def main():
    args = _parse_args()
    dev = Device.from_bsd_file(args.bsd_file)
    pod = MecrispPOD(args.port)
    pod.initialize_device(dev)
    master = tkinter.Tk()
    master.winfo_toplevel().title('MecrispPOD – %s @%s' % (osp.basename(args.bsd_file), osp.basename(args.port)))
    w = DevicePlotter(dev, master, width=800, height=600)
    w.test_pod = pod
    w.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    w.update_pin_state()
    master.mainloop()


if __name__ == '__main__':
    main()
