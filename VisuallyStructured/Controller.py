import logging
from GUI.tkinterGUI import GUI
from ModelFlow import ModelFlow, Flow
from ModelResults import ModelResults
from GUI.tkinterGUI import *
from FlowBlocks import *
from copy import deepcopy
from ThreadPool import ThreadPool


class Controller(object):
    """The controller functions as a communicator between view and model. It instantiates the model and view."""
    def __init__(self, name, settings):
        self.__name = name
        self.settings = settings
        self.threadpool = ThreadPool(extra_debug_info=True)

        logging.info("Instantiating result model...")
        self._resultmodel = ModelResults()
        logging.info("Result model instantiated.")

        logging.info("Instantiating flow model...")
        self._flowmodel = ModelFlow(modelresult=self._resultmodel, settings=settings)
        logging.info("Flow model instantiated.")

        flow = self._flowmodel.GetFlow()
        factory = FlowBlockFactory()

        logging.info("Instantiating GUI...")
        self._view = GUI(controller=self)
        logging.info("GUI instantiated.")

        logging.info("Subscribing flow view to flow model...")
        self._flowmodel.Attach(self._view.viewflow)
        logging.info("Subscribed flow view to flow model.")

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

    def GetFlow(self) -> Flow:
        flow = self._flowmodel.GetFlow()
        return deepcopy( flow ) # it is not allowed to edit the flow in the model directly,

    def SetFlow(self, flow: Flow ) -> bool:
        self._flowmodel.SetFlow(flow)
        return True

    def GetResults(self, block=None) -> ModelResults:
        results = self._resultmodel.get_result()
        if block == None:
            return results
        return results.find_all_results_for_block_name(block.name)

    def AddBlock(self, blocktype, col=0, afterblock=None, beforeblock=None):
        factory = FlowBlockFactory()
        types = factory.GetTypes()
        if types.count(blocktype):
            # is an existing type so we can add it.
            flow = self._flowmodel.GetFlow()
            newBlock = factory.Create(blocktype)
            flow.AddFlowBlock(newBlock,col=col, afterblock=afterblock, beforeblock=beforeblock)
            self._flowmodel.SetFlow(flow)
        else:
            logging.error("Could not add block; the type of block does not exist.")
            return False

    def RemoveBlock(self, block_to_remove: FlowBlock ):
        if block_to_remove:
            flow = self._flowmodel.GetFlow()
            flow.RemoveBlock(block_to_remove)
            self._flowmodel.SetFlow(flow)

    def OpenPropertiesWindowsFor(self,block):
        self._view.viewproperties.load_properties(block)

    def change_name_of_block(self, block: FlowBlock, new_name: str):
        if block:
            flow = self._flowmodel.GetFlow()
            block_in_flow = flow.GetBlockByName(block.name)
            block_in_flow.name = new_name
            self._flowmodel.SetFlow(flow)

    def set_variable_value_by_id(self, id, value):
        blockname = id.split(".")[0]
        flow = self._flowmodel.GetFlow()
        block = flow.GetBlockByName(blockname)
        block.set_variable_value_by_id(id, value=value)
        self._flowmodel.SetFlow(flow)

    def ExecuteNextStepLevel(self):
        class task(ThreadPool.Task):
            def __init__(self, name, function_handle):
                super().__init__(name)
                self.__function_handle = function_handle
            def execute(self):
                self.__function_handle()

        task_step = task("ExecuteNextStepLevel",self._flowmodel.ExecuteStepByStep)

        self.threadpool.add_task(task_step)

        #self._flowmodel.ExecuteStepByStep()

    def NewFlow(self):
        flow = Flow()
        self._flowmodel.SetFlow(flow)

    def SetWindowSize(self, geometry):
        self.settings.window_geometry = geometry

    def GetWindowSize(self):
        return self.settings.window_size

    def save_flow_to_file(self, filename: str):
        self._flowmodel.save_flow_to_file(filename)
        self.settings.last_flow = filename

    def load_flow_from_file(self, filename: str):
        self._flowmodel.load_flow_from_file(filename)
