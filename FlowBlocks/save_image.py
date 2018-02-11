from .Variables import PathVar, TextVar, ImageVar
from .FlowBlocks import FlowBlock
from .FlowBlocks import FlowBlockFactory
import os
import cv2
import logging


class SaveImage(FlowBlock):
    type_name = "SaveImage"

    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "Dir": PathVar(),
            "ImageName": TextVar()
        }
        self.__validExtensions = (".jpg", ".bmp", ".png")
        self.__cnt = 0

    @property
    def Dir(self):
        return self.SubVariables["Dir"].value

    @Dir.setter
    def DirOrFile(self, Dir):
        self.SubVariables["Dir"].value = Dir

    def __checkExtension(self, filename):
        if (filename.endswith(self.__validExtensions)):
            return True
        return False

    def execute(self, results_controller):
        logging.info("Executing save image")
        path = self.SubVariables["Dir"].value
        image_name_template = self.SubVariables["ImageName"].value
        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value
        
        if image is None:
            logging.warning("input image of %s is empty." % self.name)
            return

        if not self.__checkExtension(image_name_template):
            logging.error("Filename for %s block is not valid; extension unknown" % self.name)
            return

        if path is None:
            logging.error("Could not save image for block %s; directory not provided" % self.name)
            return

        if not os.path.exists(path):
            logging.error("Could not save image for block %s; directory does not exist." % self.name)
            return

        self.__cnt += 1

        image_name = image_name_template.replace("%i", str(self.__cnt))
        full_image_name = os.path.join(path, image_name)
        cv2.imwrite(full_image_name, image)


FlowBlockFactory.AddBlockType(SaveImage)
