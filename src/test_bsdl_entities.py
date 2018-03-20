import unittest
from bsdl_entities import PinMapString


class TestPinMapString(unittest.TestCase):
    def test1(self):
        obj = PinMapString('PB00_00:1,\nVccio:26'.splitlines())
        self.assertEqual(['1'], obj['PB00_00'])
        self.assertEqual(['26'], obj['Vccio'])

    def test2(self):
        obj = PinMapString('JTDI\t\t: 38,   \nPA0\t\t: 10'.splitlines())
        self.assertEqual(['38'], obj['JTDI'])
        self.assertEqual(['10'], obj['PA0'])
        self.assertEqual(38, obj.fuzzy_int(obj['JTDI'][0]))
        self.assertEqual(10, obj.fuzzy_int(obj['PA0'][0]))

    def test3(self):
        obj = PinMapString('DONE:P51,\nGND: (P7, P14,\nP89)'.splitlines())
        self.assertEqual(['P51'], obj['DONE'])
        self.assertEqual(['P7', 'P14', 'P89'], obj['GND'])
        self.assertEqual(51, obj.fuzzy_int(obj['DONE'][0]))
        self.assertEqual(7, obj.fuzzy_int(obj['GND'][0]))
        self.assertEqual(14, obj.fuzzy_int(obj['GND'][1]))
        self.assertEqual(89, obj.fuzzy_int(obj['GND'][2]))
