from tkinter import *
from tkinter.filedialog  import askopenfilename
from GUI.tkinterGUIHelper import  *
from GUI.tkinterViewMenu import ViewMenu
from GUI.tkinterViewFlow import ViewFlow
from GUI.tkinterViewControl import ViewControl
from GUI.tkinterViewResults import ViewResults
from GUI.tkinterViewProperties import ViewProperties
import logging
from FlowBlocks import *

class GUI(object):
    """This is the general gui class that starts all other interfaces"""
    def __init__(self, controller):
        """
        Constructor initializes all other subviews as aggregate relations.
        """
        self.root = Tk()

        self.root.title( controller.name )
        self.controller = controller
        self.viewmenu = ViewMenu(self)
        self.viewcontrol = ViewControl(self)
        self.viewflow = ViewFlow(self,col=0,row=1)
        self.viewresult = ViewResults(self, col=1, row=1)
        self.viewproperties = ViewProperties(self,col=0,row=2,columnspan=2)

        self.root.rowconfigure(1,weight=1)
        self.root.columnconfigure(1,weight=1)

        self.root.geometry(controller.settings.window_geometry)

        self.width=None
        self.height=None

    def Start(self):
        self.viewmenu.Start()
        self.viewflow.Start()
        self.root.bind("<Configure>", self.configure)  # handle resize events
        self.root.bind("<F11>", self.configure) # handle resize events
        self.root.mainloop()

    def set_window_size(self, height=None, width=None):
        pass

    def configure(self, event):
        if self.root.attributes("-fullscreen"):
            logging.info("Window geometry changed to: Fullscreen")
            self.controller.SetWindowSize("Fullscreen")
        else:
            logging.info("Window geometry changed to: %s" %self.root.geometry())
            self.controller.SetWindowSize(self.root.geometry())










