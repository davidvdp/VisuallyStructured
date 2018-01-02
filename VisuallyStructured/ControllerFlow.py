import Controller
import logging
from ModelFlow import ModelFlow
from FlowBlocks import FlowBlockFactory, FlowBlock
from ModelFlow import Flow
from copy import deepcopy
from ThreadPool import ThreadPool
from threading import Lock

level_execution_lock = Lock()

class ControllerFlow(object):
    """
    Class that separates controller flowmodel functions from other controller functions
    """
    def __init__(self, controller: Controller, settings):
        self.__controller = controller
        self.__settings = settings

        logging.info("Instantiating flow model...")
        self.__flowmodel = ModelFlow(modelresult=controller.results._resultmodel, settings=settings)
        logging.info("Flow model instantiated.")

        flow = self.__flowmodel.GetFlow()
        factory = FlowBlockFactory()

    def attach_view(self, view):
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

    def _get_name_and_index(self, name):
        '''
        Helper function to parse name and index from pattern name_index
        :param name: block name
        :return: name, index
        '''
        name = name
        index = 0
        splitted_name = name.split("_")
        if len(splitted_name) > 1:
            if splitted_name[-1].isdigit():
                name = "_".join(splitted_name[0:len(splitted_name)-1])
                index = int(splitted_name[-1])
        return name, index


    def change_name_of_block(self, block: FlowBlock, new_name: str):
        if block:
            flow = self.__flowmodel.GetFlow()

            while flow.GetBlockByName(new_name) is not None:
                name, index = self._get_name_and_index(new_name)
                new_name = name + "_" + str(index+1)

            block_in_flow = flow.GetBlockByName(block.name)
            block_in_flow.name = new_name
            self.__flowmodel.SetFlow(flow)

    def set_variable_value_by_id(self, id, value, is_reference=False):
        blockname = id.split(".")[0]
        flow = self.__flowmodel.GetFlow()
        block = flow.GetBlockByName(blockname)
        if block is None:
            return None
        new_value = block.set_variable_value_by_id(id, value=value, is_reference=is_reference) #if outside of min max value might change
        self.__flowmodel.SetFlow(flow)
        return new_value

    def run_flow_once(self):
        class task(ThreadPool.Task):
            def __init__(self, name, function_handle_execute, results):
                super().__init__(name)
                self.__function_handle_execute = function_handle_execute
                self.__results = results

            def execute(self):
                #TODO: Execution is now purely serial since every step execution is waiting on the last to finish.
                #TODO: When steps are parallel in the flow, they ought to be executed in parallel as well.
                global level_execution_lock
                level_execution_lock.acquire()
                try:
                    blocks_executed = []
                    blocks_executed = self.__function_handle_execute(self.__results)
                    self.__results.add_blocks_to_result(blocks_executed)
                finally:
                    level_execution_lock.release()

        task_step = task("ExecuteFlowOnce", self.__flowmodel.execute_flow_once, self.__controller.results)

        self.__controller.threadpool.add_task(task_step)


    def execute_next_step_level(self):
        class task(ThreadPool.Task):
            def __init__(self, name, function_handle_execute, results):
                super().__init__(name)
                self.__function_handle_execute = function_handle_execute
                self.__results = results

            def execute(self):
                #TODO: Execution is now purely serial since every step execution is waiting on the last to finish.
                #TODO: When steps are parallel in the flow, they ought to be executed in parallel as well.
                global level_execution_lock
                level_execution_lock.acquire()
                try:
                    blocks_executed = self.__function_handle_execute(self.__results)
                finally:
                    level_execution_lock.release()

        task_step = task("ExecuteNextStepLevel", self.__flowmodel.execute_step_by_step, self.__controller.results)

        self.__controller.threadpool.add_task(task_step)

    def NewFlow(self):
        flow = Flow()
        self.__flowmodel.SetFlow(flow)

    def save_flow_to_file(self, filename: str):
        self.__flowmodel.save_flow_to_file(filename)
        self.__settings.last_flow = filename

    def load_flow_from_file(self, filename: str):
        self.__flowmodel.load_flow_from_file(filename)