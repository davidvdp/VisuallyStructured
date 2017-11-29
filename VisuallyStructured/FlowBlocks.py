import logging
from Variables import *

class FlowBlockFactory(object):
    """
    Singleton flow block factory. This class can generate all kind of flow blocks that were added with,
    AddBlockType(blocktype, name) static function
    Creation is done by fist calling GetAvailableTypes() and then pick one to call Create() with
    """

    def AddBlockType(blocktype, name=None):
        """
        Static function to add new blocktype from anywhere
        :param blocktype: blocktype class name
        :param name: name for user presentation
        """
        factory = FlowBlockFactory()
        factory._AddBlockType(blocktype, name)

    class _BlockType(object):
        def __init__(self, classreference, name):
            self.classreference = classreference
            self.name = name
            self.cnt = -1

        def Create(self):
            self.cnt += 1
            name = self.name
            if name.count(".") > 0:
                name = name.split(".")[1]
            if (self.cnt is not 0):
                name += "_%d" % self.cnt

            return self.classreference(name)

    class __FlowBlockFactory(object):
        '''Actual class that manages the creation of flowblock objects'''
        def __init__(self):
            self._classList = []

        def GetTypes(self):
            """
            :return: list of possible block types
            """
            result = []
            for blocktype in self._classList:
                result.append(blocktype.name)
            return result

        def _AddBlockType(self, blocktype, name=None):
            if not name:
                block = blocktype()
                bases =  blocktype.__bases__
                if len(bases):
                    name = bases[0]().name + "." + block.name
                else:
                    name = block.name
            self._classList.append(FlowBlockFactory._BlockType(blocktype, name))

        def Create(self, type):
            """
            :param type: create type from one in list of self.GetTypes()
            :return: created block object
            """
            for blocktype in self._classList:
                if blocktype.name == type:
                    return blocktype.Create()
            return None

    instance = None

    def __init__(self):
        if not FlowBlockFactory.instance:
            FlowBlockFactory.instance = FlowBlockFactory.__FlowBlockFactory()

    def __getattr__(self, name):
        return getattr(self.instance, name)

class FlowBlock(Var):
    """A flow block that holds the information on what block or blocks to execute next"""
    def __init__(self, name="Generic"):
        super().__init__(name=name)
        self._nextSteps = []
        self.OutputVars = None

    def GetNextSteps(self):
        return self._nextSteps

    def SetNextStep(self, flowBlock, col=0):
        while len(self._nextSteps) <= col:
            self._nextSteps.append(None)
        self._nextSteps[col] = flowBlock

    def Execute(self):
        raise NotImplementedError()

class FlowBlockFilter(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different filters."""
    def __init__(self, name="Filter"):
        super().__init__(name)

    def Execute(self):
        logging.info("Executing %s" % self.name)

class FlowBlockMeasurement(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different measurements."""
    def __init__(self, name="Measurement"):
        super().__init__(name)

    def Execute(self):
        logging.info("Executing %s" %self.name)

class FlowBlockCondition(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different conditions."""
    def __init__(self, name="Condition"):
        super().__init__(name)

    def Execute(self):
        logging.info("Executing %s" % self.name)

class FlowBlockGrabber(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different conditions."""
    def __init__(self, name="Grabber"):
        super().__init__(name)
        self.OutputVars = {"Image": ImageVar()}

    def Execute(self):
        logging.info("Executing %s" % self.name)

    def GetResults(self):
        return self.OutputVars

FlowBlockFactory.AddBlockType(FlowBlockCondition, "Condition")
FlowBlockFactory.AddBlockType(FlowBlockMeasurement, "Measurement")
#FlowBlockFactory.AddBlockType(FlowBlockFilter, "Filter")