"""
Use Mecrisp to query the pin states

If run as toplevel it displays the pin state
"""
import os.path as osp
import re
import argparse
import serial
import tkinter

from boundary_scan import TestPOD, Device
from simple_view import DevicePlotter


DEBUG = False


class MecrispPOD(TestPOD):
    def __init__(self, port):
        super().__init__()
        self.input_pins = []
        self.label = None
        self._serial = serial.Serial(port=port, timeout=0.01)
        self._serial.write(b"\n")
        self._label_state = True

    def _wait_for_ok(self):
        block = ''
        while True:
            block += self._serial.read(512).decode('utf-8')
            if DEBUG: print('@@', repr(block))
            if block.endswith('ok.\n'):
                break
            if block.endswith('not found.\n'):
                self._serial.write(b'\n')
                print('ERROR', repr(block))
                break
        return block

    def _enter_command(self, cmd):
        if DEBUG: print('@@', cmd)
        self._wait_for_ok()
        self._serial.write(cmd.encode('utf-8') + b"\n")
        ret = self._wait_for_ok()
        self._serial.write(b'\n')
        pos = ret.find(cmd)
        assert pos >= 0
        return ret[pos + len(cmd):].replace('ok.\n', '')

    def initialize_device(self, dev: Device, regexp=None):
        if regexp is None:
            regexp = '.*'
        regexp = re.compile(regexp)
        for i in range(dev.number_of_pins):
            pin = i + 1
            pin_type = dev.get_pin_type(pin)
            name = dev.get_pin_name(pin)
            if pin_type in ('inout') and regexp.match(name):
                self.input_pins.append(name)

    def initialize_pins(self):
        for name in list(self.input_pins):
            ret = self._enter_command('IMODE-FLOAT %s io-mode!' % name)
            if ret.endswith('not found.\n'):
                self.input_pins.remove(name)

    def query_all_pins_starts(self):
        if self.label:
            if self._label_state:
                self.label.configure(text='\\')
            else:
                self.label.configure(text='/')
            self._label_state = not self._label_state

    def query_input_pin(self, name):
        ret = self._enter_command('%s io@ .' % name)
        return int(ret)

    def get_scanned_pin_names(self):
        return self.input_pins

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
    pod.initialize_device(dev, 'P[A-F][123]?[0-9]')
    pod.input_pins.remove('PA0')   # usb enable
    pod.input_pins.remove('PA11')  # usb D
    pod.input_pins.remove('PA12')  # usb D
    pod.initialize_pins()
    master = tkinter.Tk()
    master.winfo_toplevel().title('MecrispPOD – %s @%s' % (osp.basename(args.bsd_file), osp.basename(args.port)))
    w = DevicePlotter(dev, master, width=800, height=600)
    w.test_pod = pod
    w.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    w.update_pin_state()
    t = tkinter.Label(master, text='/')
    t.pack(side=tkinter.LEFT)
    pod.label = t
    master.mainloop()


if __name__ == '__main__':
    main()
