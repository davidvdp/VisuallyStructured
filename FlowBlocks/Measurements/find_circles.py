import logging

import cv2
import numpy as np

from FlowBlocks import FlowBlockFactory, FlowBlockMeasurement
from FlowBlocks.Variables import ImageVar, IntVar, CircleVar, PointVar, FloatVar


class FindCircles(FlowBlockMeasurement):
    type_name = "FindCircles"

    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Image": ImageVar(),
            "MinRadius": IntVar(min=-1),
            "MaxRadius": IntVar(min=-1),
            "Threshold": IntVar(128, min=0, max=255),
            "MinDistance": IntVar(20,min=0)
        }
        self.OutputVars = {"Circles": []}  # and an output

    def execute(self, results_controller):
        super(FindCircles, self).execute(results_controller)
        self.OutputVars["Circles"] = []
        min_dist = self.get_subvariable_or_referencedvariable("MinDistance", results_controller).value
        min_radius = self.get_subvariable_or_referencedvariable("MinRadius", results_controller).value
        max_radius = self.get_subvariable_or_referencedvariable("MaxRadius", results_controller).value
        threshold = self.get_subvariable_or_referencedvariable("Threshold", results_controller).value
        image = self.get_subvariable_or_referencedvariable("Image", results_controller).value

        if image is None:
            logging.error("Could not load image for block %s" % self.name)
            return

        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if min_radius == -1:
            min_radius = 0

        if max_radius == -1:
            max_radius = max(image.shape[0], image.shape[1])

        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, min_dist, param1=threshold,
                                   param2=int(threshold * 0.6),
                                   minRadius=min_radius, maxRadius=max_radius)

        if circles is None:
            return

        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            circle_var = CircleVar(PointVar(FloatVar(i[0]),FloatVar(i[1])), FloatVar(i[2]))
            self.OutputVars["Circles"].append(circle_var)



FlowBlockFactory.AddBlockType(FindCircles)
