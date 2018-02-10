import cv2
import numpy as np

from ..FlowBlocks import FlowBlockFilter
from ..FlowBlocks import FlowBlockFactory
from ..Variables import *
from Controller import ControllerResults


class LightCorrection(FlowBlockFilter):
    """Class that implements LightCorrection"""
    type_name = "LightCorrection"

    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Correction_image": PathVar()
        }
        self.__cor_mat_file = None
        self.__cor_mat = None

    def __get_corr_mat(self):
        image_file = self.get_variable_by_id("Correction_image").value
        if self.__cor_mat_file == image_file and self.__cor_mat is not None:
            return self.__cor_mat

        self.__cor_mat_file = image_file
        if os.path.isfile(image_file):
            image = cv2.imread(image_file, 0)
            self.__cor_mat = np.array(image, dtype=np.float16) - 128.0

        return self.__cor_mat

    def execute(self, results_controller: ControllerResults):
        logging.info("Executing %s" % self.name)

        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        cor_mat = self.__get_corr_mat()
        if cor_mat is None:
            logging.warning("Not a valid correction mat was provided for %s." % self.name)

        if cor_mat.shape[0] is not image.shape[0] or cor_mat.shape[1] is not image.shape[1]:
            logging.error("Correction matrix and image do not match in dimensions for block %s" % self.name)

        if len(image.shape) > 2:
            res = image.copy()
            for channel in range(res.shape[2]):
                res[:, :, channel] = image[:, :, channel] - cor_mat
        else:
            res = image - cor_mat

        if res.shape[0] > 0 and res.shape[1] > 0:
            self.OutputVars["Image"].value = res
        else:
            logging.warning("The image your are trying to load has a size of 0.")


FlowBlockFactory.AddBlockType(LightCorrection)
