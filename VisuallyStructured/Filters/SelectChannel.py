from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import ControllerResults
import cv2
import numpy as np

class SelectChannel(FlowBlockFilter):
    """Class that implements SelectChannel"""
    type_name = "SelectChannel"
    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Channel": IntVar(min=1, max=3)
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)

        channel = self.get_subvariable_or_referencedvariable("Channel", results_controller).value

        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        if len(image.shape) > 2:
            #not grayscaled
            res = image[:, :, channel-1]
        else:
            logging.warning("Could not get image channel %d in %s, because image is grayscaled" % (channel, self.name))
            res = image.copy()

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(SelectChannel)