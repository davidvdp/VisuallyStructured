from GUI.tkinterGUI import *
from .ControllerFlow import *
from .ControllerResults import *


class Controller(object):
    """The controller functions as a communicator between view and model. It instantiates the model and view."""

    def __init__(self, name, settings):
        self.__name = name
        self.settings = settings
        self.threadpool = ThreadPool(extra_debug_info=True)

        self.results = ControllerResults(self, settings=settings)
        self.flow = ControllerFlow(self, settings=settings)

        logging.info("Instantiating GUI...")
        self._view = GUI(controller=self)
        logging.info("GUI instantiated.")

        self.results.attach_view(self._view.viewresult)
        self.flow.attach_view(self._view.viewflow)

    @property
    def name(self):
        return self.__name

    def StartGUI(self):
        logging.info("Starting GUI...")
        self._view.Start()
        # make sure all blocks are correctly close (some blocks have threads running.)
        self.flow.close()
        logging.info("GUI closed.")

    def OpenPropertiesWindowsFor(self, block):
        self._view.viewproperties.load_properties(block)
