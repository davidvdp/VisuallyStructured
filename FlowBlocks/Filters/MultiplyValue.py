import numpy as np

from ..FlowBlocks import FlowBlockFilter
from ..FlowBlocks import FlowBlockFactory
from ..Variables import *
from Controller import ControllerResults


class MultiplyValue(FlowBlockFilter):
    """Class that implements MultiplyValue"""
    type_name = "MultiplyValue"

    def __init__(self, name=type_name, settings=None):
        super().__init__(name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Value": FloatVar(min=0.0, max=255.0)
        }

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)

        value = self.get_subvariable_or_referencedvariable("Value", results_controller).value

        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        res = np.array(np.array(image, dtype=np.float16) * value, dtype=np.uint8)

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(MultiplyValue)
