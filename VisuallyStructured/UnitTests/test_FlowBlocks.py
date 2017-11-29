import unittest
from FlowBlocks import FlowBlockFactory
from Filters.Sobel import Sobel

class TestFlowBlocks(unittest.TestCase):
    def test_factory_gettypes(self):
        types = FlowBlockFactory().GetTypes()
        self.assertGreater(len(types),0)

    def test_sobel_creation(self):
        sobel = FlowBlockFactory().Create("Filter.Sobel")
        self.assertIsInstance(sobel,Sobel)
        ids = sobel.GetVariableIDs()
        ids_expected = {'Sobel.Image.Image': None, 'Sobel.Kernel_Size.Int': 5}
        self.assertEqual(ids,ids_expected)




if __name__ == "__main__":
    unittest.main()