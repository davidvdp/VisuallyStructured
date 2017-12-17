from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import cv2
import ControllerResults
import numpy as np

class Sobel(FlowBlockFilter):
    """Class that implements a sobel kernel filter"""
    type_name = "Sobel"
    def __init__(self, name="Sobel"):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Kernel_Size": IntVar(5,min=1),
            "dx": BoolVar(True),
            "dy": BoolVar(False),
            "abs": BoolVar(False)
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)

        ker_size = self.get_subvariable_value("Kernel_Size", results_controller)
        dx = self.get_subvariable_value("dx", results_controller)
        dy = self.get_subvariable_value("dy", results_controller)
        abs = self.get_subvariable_value("abs",results_controller)

        image = self.get_subvariable_value("Image", results_controller)
        if image is None:
            logging.warning("input image of %s is empty." %self.name)
            return

        if dx==False and dy==False:
            logging.warning("dx and dy for %s are both false." %self.name)
            self.OutputVars["Image"].value = image
            return

        #check if grayscaled image
        if len(image.shape) != 2:
            image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        if dx:
            resdx = cv2.Sobel(image, ddepth=cv2.CV_16S, dx=1, dy=0, ksize=ker_size)
        if dy:
            resdy = cv2.Sobel(image, ddepth=cv2.CV_16S, dx=0, dy=1, ksize=ker_size)

        if dx and dy:
            res = resdx + resdy
        elif dx:
            res = resdx
        else:
            res = resdy
        if abs:
            res = np.abs(res)
        res = res - np.min(res)
        res = np.array( res / np.max(res) * 255, dtype=np.uint8 )

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")



FlowBlockFactory.AddBlockType(Sobel)