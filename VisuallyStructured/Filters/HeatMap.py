from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import ControllerResults
import cv2
import numpy as np

class HeatMap(FlowBlockFilter):
    """Class that implements image normalization"""
    type_name = "HeatMap"
    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar()
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)


        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        res = image.copy()
        cv2.applyColorMap(image, cv2.COLORMAP_JET, res)

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(HeatMap)