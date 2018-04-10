"""
A simple view of a boundary scan description file
"""
from tkinter import *
from boundary_scan import *


class QFP(object):
    def __init__(self, name):
        self.apins, self.bpins = self._name2npins(name)
        self.npins = 2 * (self.apins + self.bpins)
        self.pin_color = [None] * self.npins
        self.center = 0, 0
        self.wpin = 15
        self.hpin = 30
        self.marking = None
        self._pinhdl = []

    def plot(self, canvas: Canvas):
        cx, cy = self.center
        x0 = cx - self.apins * self.wpin / 2
        y0 = cy - self.bpins * self.wpin / 2
        x1 = cx + self.apins * self.wpin / 2
        y1 = cy + self.bpins * self.wpin / 2
        for i in range(self.apins):
            h = canvas.create_rectangle(x0 + i * self.wpin, y1, x0 + (i+1) * self.wpin, y1 + self.hpin)
            canvas.create_text(x0 + (i+0.5) * self.wpin, y1 + self.hpin / 2, text=str(i + 1), angle=90)
            self._pinhdl.append(h)
        for i in range(self.bpins):
            h = canvas.create_rectangle(x1, y1 - i * self.wpin, x1 + self.hpin, y1 - (i+1) * self.wpin)
            canvas.create_text(x1 + self.hpin / 2, y1 - (i + 0.5) * self.wpin, text=str(self.apins + i + 1))
            self._pinhdl.append(h)
        for i in range(self.apins):
            h = canvas.create_rectangle(x1 - i * self.wpin, y0, x1 - (i+1) * self.wpin, y0 - self.hpin)
            canvas.create_text(x1 - (i + 0.5) * self.wpin, y0 - self.hpin / 2, text=str(self.apins + self.bpins + i + 1),
                               angle=90)
            self._pinhdl.append(h)
        for i in range(self.bpins):
            h = canvas.create_rectangle(x0, y0 + i * self.wpin, x0 - self.hpin, y0 + (i+1) * self.wpin)
            canvas.create_text(x0 - self.hpin / 2, y0 + (i+0.5) * self.wpin, text=str(2*self.apins + self.bpins + i + 1))
            self._pinhdl.append(h)
        assert len(self._pinhdl) == self.npins
        if self.marking:
            r = self.wpin
            canvas.create_oval(x0 + 0.5 * self.wpin, y1 - self.hpin, x0 + 0.5 * self.wpin + r, y1 - self.hpin + r,
                              fill='black')
            canvas.create_text(cx, cy, text='\n'.join(self.marking.split('_')), justify=CENTER)
        self.replot(canvas)
        if False:
            canvas.create_text(x0, y0, text='0,0')
            canvas.create_text(x1, y0, text='1,0')
            canvas.create_text(x0, y1, text='0,1')
            canvas.create_text(x1, y1, text='1,1')

    def replot(self, canvas):
        for i in range(self.npins):
            if self.pin_color[i]:
                canvas.itemconfig(self._pinhdl[i], fill=self.pin_color[i])

    @staticmethod
    def _name2npins(name):
        uname = name.upper()
        if uname.startswith('TQFP'):
            npins = int(uname[4:])
        elif uname.startswith('QFPN'):
            npins = int(uname[4:])
        elif uname.startswith('VQ'):
            npins = int(uname[2:])
        elif uname.startswith('TQ'):
            npins = int(uname[2:])
        else:
            raise RuntimeError('unsupported package %s' % name)
        assert npins % 4 == 0, 'assume a square package'
        return npins // 4, npins // 4


class DevicePlotter(Canvas):
    def __init__(self, device, master: Tk, **kwargs):
        super().__init__(master, **kwargs)
        self.device = device
        self.qfp = QFP(device.get_package())
        self.qfp.marking = device.component_name
        self.qfp.center = kwargs['width'] // 2, kwargs['height'] // 2
        for i in range(self.qfp.npins):
            if self.device.get_pin_type(i + 1) == 'linkage':
                self.qfp.pin_color[i] = 'gray'
            elif self.device.is_jtag_name(self.device.get_pin_name(i + 1)):
                self.qfp.pin_color[i] = 'white'
        self.qfp.plot(self)
        self.test_pod = None  # type: TestPOD

    def update_pin_state(self):
        if self.test_pod is None:
            return
        self.test_pod.query_all_pins_starts()
        for name in self.test_pod.get_scanned_pin_names():
            i = self.device.get_pin(name)
            pin_type = self.device.get_pin_type(i)
            if pin_type in ('inout', 'in'):
                state = self.test_pod.query_input_pin(name)
                if state == 0:
                    self.qfp.pin_color[i] = 'blue'
                else:
                    self.qfp.pin_color[i] = 'red'
        self.qfp.replot(self)
        self.after(1000, self.update_pin_state)


def main(bsd_file):
    master = Tk()
    master.winfo_toplevel().title('BSD – ' + bsd_file)
    dev1 = Device.from_bsd_file(bsd_file)
    w = DevicePlotter(dev1, master, width=1024, height=720)
    w.pack(fill=BOTH, expand=YES)
    mainloop()


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
