from tkinter import *
from GUI.tkinterGUIHelper import *
import Controller


"""
View Class that other views derive from.
"""

class View(object):
    """view class"""
    def __init__(self, parent, row=None, col=None, sticky=None, scrollbars=False,columnspan=1, root=None):
        if root is not None:
            self._root = root
        else:
            self._root = parent.root
        if not row is None and not col is None:
            if scrollbars:
                self._frameScroll = VerticalScrolledFrame(self._root)
                if sticky:
                    self._frameScroll.grid_rowconfigure(0,weight=1)
                    self._frameScroll.grid_columnconfigure(0,weight=1)
                self._frame = self._frameScroll.interior
                self._frameScroll.grid(column=col, row=row, sticky=sticky,columnspan=columnspan)
            else:
                self._frame = Frame(self._root)
                self._frame.grid(column=col,row=row, sticky=sticky, columnspan=columnspan)
                if sticky:
                    self._frame.grid_rowconfigure(0,weight=1)
                    self._frame.grid_columnconfigure(0,weight=1)
        else:
            self._frame.grid(sticky=sticky,columnspan=columnspan)
        self._parent = parent

    def Start(self):
        raise NotImplementedError

    def get_controller(self) -> Controller :
        return self._parent.controller

    def SetHeight(self,height):
        self._frame.config(height=height)

    def SetWidth(self, width):
        self._frame.config(width=width)