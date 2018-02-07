import cv2

from ..FlowBlocks import FlowBlockFilter
from ..FlowBlocks import FlowBlockFactory
from ..Variables import *
from Controller import ControllerResults


class Blur(FlowBlockFilter):
    """Class that implements a sobel kernel filter"""
    type_name = "Blur"
    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Kernel_Size": IntPointVar(x=IntVar(min=3),y=IntVar(min=3))
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)
        ker_size_x = self.get_subvariable_or_referencedvariable("Kernel_Size.x", results_controller).value
        ker_size_y = self.get_subvariable_or_referencedvariable("Kernel_Size.y", results_controller).value

        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        res = cv2.blur(image, (ker_size_x,ker_size_y))

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(Blur)