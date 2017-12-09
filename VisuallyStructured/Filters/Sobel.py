from FlowBlocks import FlowBlockFilter
from FlowBlocks import FlowBlockFactory
from Variables import *
import cv2

class Sobel(FlowBlockFilter):
    """Class that implements a sobel kernel filter"""
    type_name = "Sobel"
    def __init__(self, name="Sobel"):
        super().__init__(name=name)
        self.SubVariables = {"Image": ImageVar(),"Kernel_Size": IntVar(5,min=3)}


FlowBlockFactory.AddBlockType(Sobel)