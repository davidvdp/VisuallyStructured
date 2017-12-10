import Controller
import logging
from ModelFlow import ModelFlow
from FlowBlocks import FlowBlockFactory, FlowBlock
from ModelFlow import Flow
from copy import deepcopy
from ThreadPool import ThreadPool

class ControllerFlow(object):
    """
    Class that seperates controller functions using the flowmodel from other controller functions
    """
    def __init__(self, controller: Controller, settings):
        self.__controller = controller
        self.settings = settings

        logging.info("Instantiating flow model...")
        self.__flowmodel = ModelFlow(modelresult=self.__controller._resultmodel, settings=settings)
        logging.info("Flow model instantiated.")

        flow = self.__flowmodel.GetFlow()
        factory = FlowBlockFactory()



    def Attach_View(self, view):
        logging.info("Subscribing flow view to flow model...")
        self.__flowmodel.Attach(view)
        logging.info("Subscribed flow view to flow model.")

    def GetFlow(self) -> Flow:
        flow = self.__flowmodel.GetFlow()
        return deepcopy( flow ) # it is not allowed to edit the flow in the model directly,

    def SetFlow(self, flow: Flow ) -> bool:
        self.__flowmodel.SetFlow(flow)
        return True

    def AddBlock(self, blocktype, col=0, afterblock=None, beforeblock=None):
        factory = FlowBlockFactory()
        types = factory.GetTypes()
        if types.count(blocktype):
            # is an existing type so we can add it.
            flow = self.__flowmodel.GetFlow()
            newBlock = factory.Create(blocktype)
            flow.AddFlowBlock(newBlock,col=col, afterblock=afterblock, beforeblock=beforeblock)
            self.__flowmodel.SetFlow(flow)
        else:
            logging.error("Could not add block; the type of block does not exist.")
            return False

    def RemoveBlock(self, block_to_remove: FlowBlock ):
        if block_to_remove:
            flow = self.__flowmodel.GetFlow()
            flow.RemoveBlock(block_to_remove)
            self.__flowmodel.SetFlow(flow)

    def change_name_of_block(self, block: FlowBlock, new_name: str):
        if block:
            flow = self.__flowmodel.GetFlow()
            block_in_flow = flow.GetBlockByName(block.name)
            block_in_flow.name = new_name
            self.__flowmodel.SetFlow(flow)

    def set_variable_value_by_id(self, id, value):
        blockname = id.split(".")[0]
        flow = self.__flowmodel.GetFlow()
        block = flow.GetBlockByName(blockname)
        block.set_variable_value_by_id(id, value=value)
        self.__flowmodel.SetFlow(flow)

    def ExecuteNextStepLevel(self):
        class task(ThreadPool.Task):
            def __init__(self, name, function_handle_execute, function_handle_add_result):
                super().__init__(name)
                self.__function_handle_execute = function_handle_execute
                self.__function_handle_add_result = function_handle_add_result
            def execute(self):
                blocks_executed = self.__function_handle_execute()
                self.__function_handle_add_result(blocks_executed)

        task_step = task("ExecuteNextStepLevel", self.__flowmodel.ExecuteStepByStep, self.__controller.add_blocks_to_result)

        self.__controller.threadpool.add_task(task_step)

    def NewFlow(self):
        flow = Flow()
        self.__flowmodel.SetFlow(flow)

    def save_flow_to_file(self, filename: str):
        self.__flowmodel.save_flow_to_file(filename)
        self.settings.last_flow = filename

    def load_flow_from_file(self, filename: str):
        self.__flowmodel.load_flow_from_file(filename)