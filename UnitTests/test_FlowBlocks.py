import unittest
from FlowBlocks import FlowBlockFactory
from ControllerResults import ControllerResults
from Filters.Sobel import Sobel
import cv2

class TestFlowBlocks(unittest.TestCase):
    def test_factory_gettypes(self):
        types = FlowBlockFactory().GetTypes()
        self.assertGreater(len(types),0)

    def test_sobel_creation(self):
        sobel = FlowBlockFactory().create("Filter.Sobel")
        self.assertIsInstance(sobel,Sobel)
        ids = sobel.GetVariableIDs()
        ids_expected = {
            'Sobel.Image.Image': None,
            'Sobel.Kernel_Size.Int': 5,
            'Sobel.dx.Bool': True,
            'Sobel.dy.Bool': False,
            'Sobel.abs.Bool': False
        }
        self.assertEqual(ids,ids_expected)

    def test_sobel_execution(self):
        sobel = FlowBlockFactory().create("Filter.Sobel")
        image = cv2.imread("..\\TestImages\\image5_Sobel.png", 0)

        #test dx
        sobel.set_variable_value_by_id("Image", image)
        sobel.execute(None)
        image_out=sobel.OutputVars["Image"].value
        mean_up = image_out[2:182,105].mean()
        mean_down = image_out[2:182, 97].mean()
        mean_neutral = image_out[2:182, 110:247].mean()
        self.assertEqual(mean_up,255,"Vertical line for dx=True rising border not correct.")
        self.assertEqual(mean_down, 0, "Vertical line for dx=True falling border not correct.")
        self.assertEqual(mean_neutral, 127, "Neutral zone for dx=True not correct.")

        #test dy
        sobel.set_variable_value_by_id("dx", False)
        sobel.set_variable_value_by_id("dy", True)
        sobel.execute(None)
        image_out = sobel.OutputVars["Image"].value
        mean_up = image_out[195,1:94].mean()
        mean_down = image_out[186, 1:94].mean()
        mean_neutral = image_out[2:182, 110:247].mean()
        self.assertEqual(mean_up,255,"Vertical line for dx=True rising border not correct.")
        self.assertEqual(mean_down, 0, "Vertical line for dx=True falling border not correct.")
        self.assertEqual(mean_neutral, 127, "Neutral zone for dx=True not correct.")




if __name__ == "__main__":
    unittest.main()