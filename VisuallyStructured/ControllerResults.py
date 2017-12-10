import logging
from ModelResults import ModelResults
import Controller

class ControllerResults(object):
    def __init__(self, controller: Controller, settings):
        self.__controller = Controller
        self.__settings = settings

        logging.info("Instantiating result model...")
        self._resultmodel = ModelResults()
        logging.info("Result model instantiated.")

    def GetResults(self, block=None) -> ModelResults:
        results = self._resultmodel.get_result()
        if block == None:
            return results
        return results.find_all_results_for_block_name(block.name)

    def add_blocks_to_result(self, blocks_with_result):
        for block in blocks_with_result:
            self._resultmodel.add_result(block)
            block.clean_output_data()

    def attach_view(self, view):
        logging.info("Subscribing result view to result model...")
        self._resultmodel.Attach(view)
        logging.info("Subscribed result view to result model.")