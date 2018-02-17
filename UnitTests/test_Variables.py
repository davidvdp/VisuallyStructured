import unittest
from Variables import *


class TestVar(unittest.TestCase):
    def test_linevar(self):
        lineVar = LineVar()
        structuredPrint = lineVar.get_variable_ids()
        expected = {'Line.start.x.Float': 0.0, 'Line.start.y.Float': 0.0, 'Line.end.x.Float': 0.0,
                    'Line.end.y.Float': 0.0}
        self.assertEqual(structuredPrint, expected)

    def test_savedump(self):
        lineVar = LineVar()
        filename = "testDump.vsf"
        lineVar.Save(filename)
        loadedlineVar = Var.Load(filename)
        self.assertEqual(lineVar.get_variable_ids(), loadedlineVar.get_variable_ids())

    def test_minmax_guard_int(self):
        intVar = IntVar(intvalue=-2, min=1, max=2)
        self.assertEqual(intVar.value, 1)
        intVar.value = 3
        self.assertEqual(intVar.value, 2)

    def test_minmax_guard_float(self):
        floatVar = FloatVar(floatvalue=-2.0, min=1.0, max=2.0)
        self.assertEqual(floatVar.value, 1.0)
        floatVar.value = 3.0
        self.assertEqual(floatVar.value, 2.0)


if __name__ == "__main__":
    unittest.main()
