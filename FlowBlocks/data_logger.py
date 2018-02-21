from .Variables import FloatVar, PathVar
from .FlowBlocks import FlowBlock
from time import localtime, strftime
import os
import logging
from FlowBlocks import FlowBlockFactory

class DataLogger(FlowBlock):
    type_name = "DataLogger"

    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "File": PathVar(),
            "Data": FloatVar()
        }

    def execute(self, results_controller):
        logging.info("Executing %s" % self.name)
        file_name = self.get_subvariable_or_referencedvariable("File", results_controller).value
        data = self.get_subvariable_or_referencedvariable("Data", results_controller).value
        if file_name is None or data is None:
            return

        with open(file_name, 'a') as f:
            time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            f.write("%s; %.3f\n" %(time, data))

FlowBlockFactory.AddBlockType(DataLogger)


