from SubjectObserver import Subject
from FlowBlocks.FlowBlocks import FlowBlock
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

        def FindAllOfType(self, var_type):
            result = dict()
            for keyflowblock, valflowblock in self._results.items():
                for key, val in valflowblock.items():
                    if type(val) is list:
                        for i,val_list in enumerate(val):
                            result2 = val_list.get_variables_by_type(var_type)
                            for key2, val2 in result2.items():
                                result[keyflowblock + "." + key+"["+str(i)+"]." + key2] = val2
                    else:
                        result2 = val.get_variables_by_type(var_type)
                        for key2, val2 in result2.items():
                            result[keyflowblock + "." + key + "." + key2] = val2
            return result

        def find_all_results_for_block_name(self, block_name):
            return self._results.get(block_name)

        def exists(self, id: str) -> bool:
            """
            For now only searches 2 deep
            :param id: id as a string (e.g. Block1.File)
            :return: found id
            """
            splitted_id = id.split(".")
            block_name = splitted_id[0]
            result = self.find_all_results_for_block_name(block_name)
            if result is None or len(result) == 0:
                return False
            if len(splitted_id) == 2:
                if result.get(splitted_id[1]) is None:
                    return False
            return True

        def getvalue(self, id: str):
            splitted_id = id.split(".")
            block_name = splitted_id[0]
            result = self.find_all_results_for_block_name(block_name)
            if result is None or len(result) == 0:
                return None
            if len(splitted_id) < 2:
                if result.get(splitted_id[1]) is None:
                    return None
            return result.get(splitted_id[1])

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

    def OnFlowModelChange(self, flow):
        """Removes all blocks from results that have been removed from flow, keeps data of blocks that are kept and adds new blocks"""
        listofnames = flow.get_list_of_block_names()
        oldresults = self._results.GetResultDict()
        keysToKeep = set(oldresults) & set(listofnames)
        oldresults = {key: oldresults[key] for key in keysToKeep}  # remove results not in the new flow
        keystoadd = set(listofnames) - set(oldresults)
        for key in keystoadd:
            flowblock = flow.get_block_by_name(key)
            if flowblock.OutputVars is None or len(flowblock.OutputVars) is 0:
                continue
            oldresults[key] = flowblock.OutputVars  # add result for new blocks
        self._results.SetResultDict(oldresults)
        self._notify()

    def add_result(self, flowblock: FlowBlock):
        if flowblock is None:
            return
        if flowblock.OutputVars is None or len(flowblock.OutputVars) is 0:
            return
        self._results.AddToResult(flowblock.name, deepcopy(flowblock.OutputVars))
        self._notify(flowblock_name=flowblock.name)

    def exists(self, id: str) -> bool:
        return self._results.exists(id)

    def getvalue(self, id: str):
        return self._results.getvalue(id)
