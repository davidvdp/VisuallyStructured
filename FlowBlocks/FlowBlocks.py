from .Variables import *

__type_name = "type"
__sub_var_name = "sub_variables"


def get_dict_structure_for_var(var: Var):
    """
    Gets variable as a dict including all subvariables
    :param var: var object to serialize
    :return: dict
    """
    if var.SubVariables is None or len(var.SubVariables) < 1:
        return {"value": var.value, "is_reference": var.is_reference}
    sub_vars = {}
    for key, val in var.SubVariables.items():
        sub_vars[key] = get_dict_structure_for_var(val)
    if len(sub_vars) < 1:
        return {"value": var.value, "is_reference": var.is_reference}

    return sub_vars


class FlowBlockFactory(object):
    """
    Singleton flow block factory. This class can generate all kind of flow blocks that were added with,
    AddBlockType(blocktype, name) static function
    Creation is done by fist calling GetAvailableTypes() and then pick one to call create() with
    """

    @staticmethod
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

        def create(self, name=None, settings=None):
            self.cnt += 1
            if name == None:
                name = self.name

            # points in the name are not allowed so use last part of name.
            if name.count(".") > 0:
                name = name.split(".")[-1]

            # if cnt > than 0 it means a block with this name has already been created. Use a different name.
            if (self.cnt is not 0):
                name += "_%d" % self.cnt

            block = self.classreference(name)  # type: FlowBlock
            if settings is not None:
                block.set_variable_by_settings_dict(settings)
            return block

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
                bases = blocktype.__bases__
                if len(bases):
                    name = bases[0]().name + "." + block.name
                else:
                    name = block.name
            self._classList.append(FlowBlockFactory._BlockType(blocktype, name))

        def create(self, type, name=None, settings=None):
            """
            :param type: create type from one in list of self.GetTypes()
            :return: created block object
            """
            for blocktype in self._classList:
                if blocktype.name == type:
                    return blocktype.create(name=name, settings=settings)
            return None

    instance = None

    def __init__(self):
        if not FlowBlockFactory.instance:
            FlowBlockFactory.instance = FlowBlockFactory.__FlowBlockFactory()

    def __getattr__(self, name):
        return getattr(self.instance, name)


class FlowBlock(Var):
    """
    A flow block that holds the information on what block or blocks to execute next.
    OutputVars is a temporary storage for results of measurements and will be cleared by the controller by a result
    update (clean_output_data will be called).
    """
    type_name = "Flow_Block"

    def __init__(self, name="Generic"):
        super().__init__(name)
        self._nextSteps = []
        self.OutputVars = dict()

    @property
    def type(self):
        if self.__class__.__bases__[0].type_name == "Flow_Block":
            return self.__class__.type_name
        return self.__class__.__bases__[0].type_name + "." + self.__class__.type_name

    def GetNextSteps(self):
        return self._nextSteps

    def SetNextStep(self, flowBlock, col=0):
        while len(self._nextSteps) <= col:  # is col is not 0 than fill with nones
            self._nextSteps.append(None)
        self._nextSteps[col] = flowBlock

    def execute(self, results_controller):
        """
        This function needs to be implemented. It is called when executing a block.
        :param results_controller:
        :return:
        """
        raise NotImplementedError()

    def clean_output_data(self):
        if self.OutputVars is not None:
            for key, value in self.OutputVars.items():
                value.__init__()

    def GetResults(self):
        return self.OutputVars

def get_dict_structure_for_block(block: FlowBlock):
    """
    Gets the structure of a block in order to save it to a file.
    :param var: The var object or block
    :return: a dict containing the structure of the block as a dict containing strings.
    """
    global __type_name
    global __sub_var_name

    subvar_structure = {}
    for key, value in block.SubVariables.items():
        subvar_structure[key] = get_dict_structure_for_var(value)

    # save type of block
    result = {}
    result[block.name] = {
        __type_name: block.type,
        __sub_var_name: subvar_structure
    }

    return result


def get_block_from_dict_structure(name, property) -> FlowBlock:
    global __type_name
    global __sub_var_name
    fbf = FlowBlockFactory()
    block_obj = fbf.create(property[__type_name], name=name, settings=property[__sub_var_name])
    # for id, value in property[self.__sub_var_name].items():
    #   block_obj.set_variable_value_by_id(id, value)
    return block_obj


class FlowBlockFilter(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of diffserent filters."""
    type_name = "Filter"

    def __init__(self, name="Filter", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.SubVariables.update({
            "Image": ImageVar()
        })  # a filter always has an input
        self.OutputVars = {"Image": ImageVar()}  # and an output

    def execute(self, results_controller):
        raise NotImplementedError()


class FlowBlockMeasurement(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different measurements."""
    type_name = "Measurement"

    def __init__(self, name="Measurement"):
        super().__init__(name)

    def execute(self, results_controller):
        logging.info("Executing %s" % self.name)


class FlowBlockCondition(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different conditions."""
    type_name = "Condition"

    def __init__(self, name="Condition"):
        super().__init__(name)

    def execute(self, results_controller):
        logging.info("Executing %s" % self.name)


class FlowBlockGrabber(FlowBlock):
    """Implementation of Flowblock. It allows for the execution of different conditions."""
    type_name = "Grabber"

    def __init__(self, name="Grabber"):
        super().__init__(name)
        self.OutputVars = {"Image": ImageVar()}

    def execute(self, results_controller):
        logging.info("Executing %s" % self.name)

FlowBlockFactory.AddBlockType(FlowBlockCondition, "Condition")
FlowBlockFactory.AddBlockType(FlowBlockMeasurement, "Measurement")
