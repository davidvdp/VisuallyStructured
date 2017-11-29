from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import cv2

class Blur(FlowBlockFilter):
    """Class that implements a sobel kernel filter"""
    def __init__(self, name="Blur"):
        super().__init__(name=name)
        self.SubVariables = {"Kernel_Size": IntPointVar(x=IntVar(min=3),y=IntVar(min=3))}

FlowBlockFactory.AddBlockType(Blur)