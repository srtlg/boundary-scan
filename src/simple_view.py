from tkinter import *
from boundary_scan import *


class QFP(object):
    def __init__(self, name):
        self.apins, self.bpins = self._name2npins(name)
        self.npins = 2 * (self.apins + self.bpins)
        self.pin_color = [None] * self.npins
        self.center = 0, 0
        self.wpin = 30
        self.hpin = 60
        self._pinhdl = []

    def plot(self, canvas: Canvas):
        cx, cy = self.center
        x0 = cx - self.apins * self.wpin / 2
        y0 = cy - self.bpins * self.wpin / 2
        x1 = cx + self.apins * self.wpin / 2
        y1 = cy + self.bpins * self.wpin / 2
        for i in range(self.apins):
            h = canvas.create_rectangle(x0 + i * self.wpin, y1, x0 + (i+1) * self.wpin, y1 + self.hpin)
            canvas.create_text(x0 + (i+0.5) * self.wpin, y1 + self.hpin / 2, text=str(i + 1))
            self._pinhdl.append(h)
        for i in range(self.bpins):
            h = canvas.create_rectangle(x1, y1 - i * self.wpin, x1 + self.hpin, y1 - (i+1) * self.wpin)
            canvas.create_text(x1 + self.hpin / 2, y1 - (i + 0.5) * self.wpin, text=str(self.apins + i + 1))
            self._pinhdl.append(h)
        for i in range(self.apins):
            h = canvas.create_rectangle(x1 - i * self.wpin, y0, x1 - (i+1) * self.wpin, y0 - self.hpin)
            canvas.create_text(x1 - (i + 0.5) * self.wpin, y0 - self.hpin / 2, text=str(self.apins + self.bpins + i + 1))
            self._pinhdl.append(h)
        for i in range(self.bpins):
            h = canvas.create_rectangle(x0, y0 + i * self.wpin, x0 - self.hpin, y0 + (i+1) * self.wpin)
            canvas.create_text(x0 - self.hpin / 2, y0 + (i+0.5) * self.wpin, text=str(2*self.apins + self.bpins + i + 1))
            self._pinhdl.append(h)
        assert len(self._pinhdl) == self.npins
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
        if name.lower().startswith('vq'):
            return int(name[2:])//4, int(name[2:])//4
        else:
            raise RuntimeError()


class DevicePlotter(Canvas):
    def __init__(self, device, master, **kwargs):
        super().__init__(master, **kwargs)
        self.device = device
        self.qfp = QFP(device.get_package())
        self.qfp.center = kwargs['width'] // 2, kwargs['height'] // 2
        for i in range(self.qfp.npins):
            if not self.device.get_pin_name(i + 1).startswith('PB'):
                self.qfp.pin_color[i] = 'gray'
        self.qfp.plot(self)


def main():
    master = Tk()
    dev1 = Device.from_bsd_file('/opt/Xilinx/14.7/ISE_DS/ISE/xc9500xl/data/xc9572xl_vq44.bsd')
    w = DevicePlotter(dev1, master, width=800, height=600)
    w.pack()
    print(dev1.get_package())
    print(dev1.get_pin_name(1))
    print(dev1.get_pin_name(29))
    mainloop()


if __name__ == '__main__':
    main()
