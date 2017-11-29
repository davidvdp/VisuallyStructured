from SubjectObserver import Subject
import logging
import os

class ModelFlow(Subject):
    """This holds the actual flow and is able to pass it to a subscriber when needed."""
    def __init__(self,modelresult = None):
        super().__init__()
        self._flow = Flow()
        self.__modelresult = modelresult

    def GetFlow(self):
        return self._flow

    def SetFlow(self, flow):
        self._flow = flow
        self.__modelresult.OnFlowModelChange(flow)
        self.Notify()

    def ExecuteStepByStep(self):
        blocksExecuted = self._flow.ExecuteStepByStep()
        for block in blocksExecuted:
            self.__modelresult.AddResult(block)


class Flow(object):
    def __init__(self):
        self._jSONFileLocation = ""
        self.__startBlock = None
        self.__nextBlocksToBeExecuted = [self.__startBlock]

    def ReadJSON(self, file=None):
        """
        Reads a JSON file that holds information of a previously saved flow.
        :param file: Flow file location as a String.
        :return: Has the file been loaded? Boolean
        """
        if file is not None:
            if not os.path.exists(file):
                logging.error("Could not find file Flow file for reading %s" %file)
                return False

            self._jSONFileLocation = file

        if self._jSONFileLocation is None:
            logging.error("Flow file to read has not been specified.")
            return False

        logging.info("Read JSON flow file")
        return True

    def WriteJSON(self, file=None):
        logging.info("Wrote JSON flow file")
        return True

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
                break;
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
                result = self.__getBlockByName(name,nextblock)
                if result:
                    return result
        return None

    def __getListOfBlockNames(self, startblock):
        names = []
        if startblock is None:
            return names
        for nextblock in startblock.GetNextSteps():
            names = self.__getListOfBlockNames( nextblock)
        names.append(startblock.name)
        return names

    def GetListOfBlockNames(self):
        return self.__getListOfBlockNames(self.__startBlock)

    def GetBlockByName(self, name):
        return self.__getBlockByName(name,self.__startBlock)

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
            #use recursive function to find step to remove
            return self.__removeBlock(blockToRemove, self.__startBlock)

    # def __executeStepByStep(self, startblock):
    #     if startblock is None:
    #         return
    #     startblock.Execute()
    #     nextSteps = startblock.GetNextSteps()
    #     if len(nextSteps):
    #         for step in nextSteps:
    #             self.__executeStepByStep(step)

    def ExecuteStepByStep(self):
        if self.__nextBlocksToBeExecuted is None:
            return None

        if len(self.__nextBlocksToBeExecuted ) is 0:
            self.__nextBlocksToBeExecuted = [self.GetStartBlock()]

        nextBlocks = []
        blocksExecuted = []
        for block in self.__nextBlocksToBeExecuted:
            if block is None: block = self.GetStartBlock()
            block.Execute()
            blocksExecuted.append(block)
            nextBlocks = nextBlocks + block.GetNextSteps()

        self.__nextBlocksToBeExecuted = nextBlocks
        return blocksExecuted

