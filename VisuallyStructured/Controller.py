import logging
from GUI.tkinterGUI import GUI
from ModelFlow import Flow
#from ModelFlow import ModelFlow
from ModelResults import ModelResults
from GUI.tkinterGUI import *
from FlowBlocks import *
from copy import deepcopy
from ThreadPool import ThreadPool
from ControllerFlow import *


class Controller(object):
    """The controller functions as a communicator between view and model. It instantiates the model and view."""
    def __init__(self, name, settings):
        self.__name = name
        self.settings = settings
        self.threadpool = ThreadPool(extra_debug_info=True)

        logging.info("Instantiating result model...")
        self._resultmodel = ModelResults()
        logging.info("Result model instantiated.")

        self.flow = ControllerFlow(self, settings=settings)

        logging.info("Instantiating GUI...")
        self._view = GUI(controller=self)
        logging.info("GUI instantiated.")

        self.flow.Attach_View(self._view.viewflow)

        logging.info("Subscribing result view to result model...")
        self._resultmodel.Attach(self._view.viewresult)
        logging.info("Subscribed result view to result model.")

    @property
    def name(self):
        return self.__name

    def StartGUI(self):
        logging.info("Starting GUI...")
        self._view.Start()
        logging.info("GUI closed.")

    def GetResults(self, block=None) -> ModelResults:
        results = self._resultmodel.get_result()
        if block == None:
            return results
        return results.find_all_results_for_block_name(block.name)

    def OpenPropertiesWindowsFor(self,block):
        self._view.viewproperties.load_properties(block)

    def add_blocks_to_result(self, blocks_with_result):
        for block in blocks_with_result:
            self._resultmodel.add_result(block)
            block.clean_output_data()


    def SetWindowSize(self, geometry):
        self.settings.window_geometry = geometry

    def GetWindowSize(self):
        return self.settings.window_size

