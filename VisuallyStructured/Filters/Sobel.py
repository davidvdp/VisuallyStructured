from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import cv2
import ControllerResults

class Sobel(FlowBlockFilter):
    """Class that implements a sobel kernel filter"""
    type_name = "Sobel"
    def __init__(self, name="Sobel"):
        super().__init__(name=name)
        self.SubVariables = {"Image": ImageVar(),"Kernel_Size": IntVar(5,min=3)}

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)
        image = self.SubVariables.get("Image")
        is_reference = False
        try:
            is_reference = image.is_reference
        except: #TODO: Somehow the is_reference property is not inherited.
            is_reference = False
            logging.warning("Sobel.is_reference property does not exist.")
        if is_reference:
            image_new = results_controller.getvalue(image.value)
        else:
            image_new = image
        image = image_new.value
        res = cv2.blur(image, (31,31))
        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")



FlowBlockFactory.AddBlockType(Sobel)