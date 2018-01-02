from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import ControllerResults
import cv2
import numpy as np

class Normalize(FlowBlockFilter):
    """Class that implements image normalization"""
    type_name = "Normalize"
    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "alpha": IntVar(0, min=0, max=255),
            "beta": IntVar(255, min=0, max=255)
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)
        alpha = self.get_subvariable_or_referencedvariable("alpha", results_controller).value
        beta = self.get_subvariable_or_referencedvariable("beta", results_controller).value

        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        res = image.copy()
        cv2.normalize(image, res, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX)

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(Normalize)