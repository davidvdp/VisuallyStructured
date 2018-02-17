import logging
import os
from yaml import dump, load
from threading import Lock

from SubjectObserver import Subject
from Controller import ControllerResults
from FlowBlocks.FlowBlocks import get_dict_structure_for_block, get_block_from_dict_structure
from time import time

level_execution_lock = Lock()


class Flow(object):
    def __init__(self):
        self.__yamlfile = "flow.current"
        self.__startBlock = None
        self.__nextBlocksToBeExecuted = [self.__startBlock]

    @property
    def next_blocks_to_execute(self):
        return self.__nextBlocksToBeExecuted

    def reset_next_block_to_be_executed(self):
        self.__nextBlocksToBeExecuted = [self.__startBlock]

    def save(self):
        global setttings
        flow_file = self.__yamlfile
        self.save_to(flow_file)

    def save_to(self, destination_file: str):
        """
        Saves yaml file with all settings of flow blocks and their order
        :param destination_file: file to save to
        :return: None
        """
        # remove old file
        if os.path.exists(destination_file):
            os.remove(destination_file)

        yaml_data = {}

        # get all blocks and extract data from them
        block_names = self.get_list_of_block_names()

        # save execution order
        order = [block_name for block_name in block_names]
        yaml_data["order"] = order

        for block_name in block_names:
            block = self.get_block_by_name(block_name)
            yaml_data.update(get_dict_structure_for_block(block))

        with open(destination_file, 'w') as stream:
            dump(yaml_data, stream, default_flow_style=False)

        logging.info("Saved flow to file: %s." % destination_file)

    def clear(self):
        self.__startBlock = None
        self.__nextBlocksToBeExecuted = [self.__startBlock]

    def load(self):
        global setttings
        self.load_from(self.__yamlfile)

    def load_from(self, source_file: str):
        if os.path.isfile(source_file):
            with open(source_file, 'r') as stream:
                yaml_data = load(stream)
                if yaml_data is None:
                    return False
                elif len(yaml_data) is 0:
                    return False

            # remove old blocks
            self.clear()
            order = yaml_data.get("order", None)
            if order is None:
                logging.error("Source yaml does not contain an 'order' record.")
                return

            for block_name in order:
                properties = yaml_data.get(block_name, None)
                if properties is None:
                    logging.error("Could not find block %s in YAML even though it is specified in the 'order' record.")
                    continue
                block_obj = get_block_from_dict_structure(block_name, properties)
                self.AddFlowBlock(block_obj)

    def GetStartBlock(self):
        return self.__startBlock

    def _getLastFlowBlock(self, col=0):
        """Finds last flow block. Optionally a column can be provided to find the last one within a column"""
        if self.__startBlock is None:
            return None
        current = self.__startBlock
        while len(current.GetNextSteps()) > col:
            next = current.GetNextSteps()[col]
            if next is None:
                break
            current = next
        return current

    def AddFlowBlock(self, flowBlock, col=0, afterblock=None, beforeblock=None):
        if afterblock and beforeblock:
            logging.error("Cannot add block; an afterblock and beforeblock has be specified.")
            return False
        if self.__startBlock is None:
            self.__startBlock = flowBlock
        else:
            if afterblock:
                nextSteps = afterblock.GetNextSteps()
                if len(nextSteps) > col:
                    flowBlock.SetNextStep(nextSteps[col])
                afterblock.SetNextStep(flowBlock, col)
            else:
                lastFlowBlock = self._getLastFlowBlock(col)
                lastFlowBlock.SetNextStep(flowBlock, col)
        return True

    def __removeBlock(self, blockToRemove, startblock):
        '''Recursive function'''
        nextsteps = startblock.GetNextSteps()
        for istep in range(len(nextsteps)):
            step = nextsteps[istep]
            if step.name is blockToRemove.name:
                nextsteps2 = step.GetNextSteps()
                if len(nextsteps2):
                    # if a condition keep only the first column
                    startblock.SetNextStep(nextsteps2[0], istep)
                    return True
                else:
                    # last one in line
                    startblock.SetNextStep(None, istep)
                    return True

        for step in nextsteps:
            if self.__removeBlock(blockToRemove, step):
                return True

        return False

    def __getBlockByName(self, name, startblock):
        if startblock.name == name:
            return startblock
        else:
            for nextblock in startblock.GetNextSteps():
                result = self.__getBlockByName(name, nextblock)
                if result:
                    return result
        return None

    def __getListOfBlockNames(self, startblock):
        names = []
        if startblock is None:
            return names
        for nextblock in startblock.GetNextSteps():
            names = self.__getListOfBlockNames(nextblock)
        names.append(startblock.name)
        return names

    def get_list_of_block_names(self):
        return self.__getListOfBlockNames(self.__startBlock)[::-1]

    def get_block_by_name(self, name):
        return self.__getBlockByName(name, self.__startBlock)

    def RemoveBlock(self, blockToRemove):
        """
        This function fist checks the start block, and then checks all other steps recursively using the _removeBlock
        function.
        :param blockToRemove:
        :return: successfully removed block
        """
        if self.__startBlock.name is blockToRemove.name:
            nextsteps = self.__startBlock.GetNextSteps()
            if len(nextsteps):
                # if it is a condition only the first column is kept
                self.__startBlock = nextsteps[0]
                return True
            else:
                # Removed only step in the flow
                self.__startBlock = None
                return True
        else:
            # use recursive function to find step to remove
            return self.__removeBlock(blockToRemove, self.__startBlock)

    def execute_flow_once(self, controller_results: ControllerResults):
        not_started_yet = True

        blocks_executed = []
        execution_times = []

        while not self.__startBlock in self.next_blocks_to_execute or not_started_yet:
            not_started_yet = False
            blocks_executed_new, execution_times_new = self.execute_step_by_step(controller_results=controller_results)
            blocks_executed.extend(blocks_executed_new)
            execution_times.extend(execution_times_new)

        for block, time in zip(blocks_executed, execution_times):
            logging.debug("Block %s took %.2f miliseconds to execute" % (block.name, time*1000))

        return blocks_executed

    def execute_step_by_step(self, controller_results: ControllerResults):
        blocksExecuted = []
        if self.__nextBlocksToBeExecuted is None:
            return None

        if len(self.__nextBlocksToBeExecuted) is 0:
            self.__nextBlocksToBeExecuted = [self.GetStartBlock()]

        nextBlocks = []
        blocksExecuted = []
        execution_times = []
        for block in self.__nextBlocksToBeExecuted:
            if block is None: block = self.GetStartBlock()
            start_time = time()
            block.execute(controller_results)
            execution_times.append(time() - start_time)
            blocksExecuted.append(block)
            nextBlocks = nextBlocks + block.GetNextSteps()

        self.__nextBlocksToBeExecuted = nextBlocks

        if len(self.__nextBlocksToBeExecuted) is 0:
            self.__nextBlocksToBeExecuted = [self.GetStartBlock()]

        controller_results.add_blocks_to_result(blocksExecuted)

        return blocksExecuted, execution_times


class ModelFlow(Subject):
    """This holds the actual flow and is able to pass it to a subscriber when needed."""

    def __init__(self, settings, modelresult=None):
        super().__init__()
        self._flow = Flow()

        flow_file = settings.last_flow
        if os.path.isfile(flow_file):
            self._flow.load()

        self.__modelresult = modelresult

    def GetFlow(self) -> Flow:
        return self._flow

    def SetFlow(self, flow: Flow):
        self._flow = flow
        self._flow.save()
        self.__modelresult.OnFlowModelChange(flow)
        self._notify()

    def execute_step_by_step(self, controller_results: ControllerResults):
        blocksExecuted = self._flow.execute_step_by_step(controller_results)
        return blocksExecuted

    def execute_flow_once(self, controller_results: ControllerResults):
        blocksExecuted = self._flow.execute_flow_once(controller_results)
        return blocksExecuted

    def load_flow_from_file(self, file_name: str):
        self._flow.load_from(file_name)
        self._notify()

    def save_flow_to_file(self, file_name: str):
        self._flow.save_to(file_name)

    def get_next_block_to_execute(self):
        return self._flow.next_blocks_to_execute
