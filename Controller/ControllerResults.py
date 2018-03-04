import logging
from ModelResults import ModelResults
import Controller
from FlowBlocks.FlowBlocks import FlowBlock
from typing import List


class ControllerResults(object):
    def __init__(self, controller: Controller, settings):
        self.__controller = Controller
        self.__settings = settings

        logging.info("Instantiating result model...")
        self._resultmodel = ModelResults()
        logging.info("Result model instantiated.")

    def get_results_for_block(self, block=None) -> ModelResults:
        results = self._resultmodel.get_result()
        if block == None:
            return results
        return results.find_all_results_for_block_name(block.name)

    def get_results_of_type(self, type: type):
        return self._resultmodel.get_all_of_type(type)

    def get_result_dict(self):
        return self._resultmodel.get_result().get_result_dict()

    def add_blocks_to_result(self, blocks_with_result: List[FlowBlock]):
        """
        Adds the results of a block to the result model. Results, when saved in results will be deleted from flow.
        This makes sure the flow is not getting to large in size.
        :param blocks_with_result: blocks from with results are extracted.
        :return:
        """
        for block in blocks_with_result:
            self._resultmodel.add_result(block)
            #block.clean_output_data()

    def attach_view(self, view):
        logging.info("Subscribing result view to result model...")
        self._resultmodel.Attach(view)
        logging.info("Subscribed result view to result model.")

    def exists(self, id: str) -> bool:
        """
        Checks the existence of a id in the results model
        :param id: id as a string (e.g. Thisisablock.Image)
        :return: found one or more.
        """
        return self._resultmodel.exists(id)

    def getvalue(self, id: str):
        """
        Checks the existence of a id in the results model
        :param id: id as a string (e.g. Thisisablock.Image)
        :return: found one or more.
        """
        return self._resultmodel.getvalue(id)
