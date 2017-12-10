from SubjectObserver import Subject
from Variables import *
from FlowBlocks import FlowBlock
from copy import deepcopy

class ModelResults(Subject):
    """This holds the actual flow and is able to pass it to a subscriber when needed."""
    class Results(object):
        def __init__(self, resultlist=dict()):
            self._results = resultlist

        def GetResultDict(self):
            return self._results

        def SetResultDict(self, resultdict):
            if resultdict is None:
                self._results = dict()
            else:
                self._results = resultdict

        def AddToResult(self, key, value):
            self._results[key] = value

        def FindAllOfType(self,type):
            result = dict()
            for keyflowblock, valflowblock in self._results.items():
                for key, val in valflowblock.items():
                    result2 = val.get_variables_by_type(type)
                    for key2, val2 in result2.items():
                        result[keyflowblock+"."+key+"."+key2] = val2
            return result

        def find_all_results_for_block_name(self, blockname):
            return self._results.get(blockname)

    def __init__(self):
        super().__init__()
        self._results = ModelResults.Results()

    def get_result(self) -> Results:
        """
        Returns all results that are kept here, or optionally for on specific step
        :return: results
        """
        return self._results

    def get_all_of_type(self, type):
        return self._results.FindAllOfType(type)

    def OnFlowModelChange(self,flow):
        """Removes all blocks from results that have been removed from flow, keeps data of blocks that are kept and adds new blocks"""
        listofnames = flow.GetListOfBlockNames()
        oldresults = self._results.GetResultDict()
        keysToKeep = set(oldresults) & set(listofnames)
        oldresults = {key: oldresults[key] for key in keysToKeep} # remove results not in the new flow
        keystoadd = set(listofnames) - set(oldresults)
        for key in keystoadd:
            flowblock = flow.GetBlockByName(key)
            if flowblock.OutputVars is None or len(flowblock.OutputVars) is 0:
                continue
            oldresults[key] = flowblock.OutputVars # add result for new blocks
        self._results.SetResultDict(oldresults)
        self._notify()

    def add_result(self, flowblock: FlowBlock):
        if flowblock is None:
            return
        if flowblock.OutputVars is None or len(flowblock.OutputVars) is 0:
            return
        self._results.AddToResult(flowblock.name, flowblock.OutputVars)
        self._notify()