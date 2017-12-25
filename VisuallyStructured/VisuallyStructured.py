from Controller import *
import logging
from time import localtime, strftime
import os
from StandardSettings import Settings

from Filters import Sobel
from Filters import Blur
from Grabbers import File

#TODO: Execute Filters
#TODO: When creating a new block or changing it's name; check if a block with the same name already exists.
#TODO: Make sure block name can only exist once
#TODO: When settings in properties are changes but not saved; add warning.
#TODO: properties of a block should all be saved at once.
#TODO: Add Continuous flow execution.
#TODO: Create tree like structure for properties within a block
#TODO: Use icon to distinguish block types from one another

#TODO: Show save state.
#TODO: Add conditions / multiple columns
#TODO: Allow for the use of del ctrl-c, ctrl-v etc.
#TODO: Make sure that all user events have a try catch
#TODO: Think of a name. Visico, VisuallyScructured
#TODO: Add ruler profile and histogram options for image analysis
#TODO: Add Icons for grabber, filter, meas and condition
#TODO: When adding blocks to a already saved and loaded flw name is not automatically indexed like Sobel_1 Sobel_2 etc


def setLogging(settings):
    log_dir = settings.log_dir

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    # clean log dir
    files = os.listdir(log_dir)
    nr_files = len(files)
    max_files = settings.max_log_history_days
    if nr_files > max_files:
        files.sort()
        for i, file in enumerate(files):
            if i >= nr_files - max_files:
                break
            os.remove(log_dir+"\\"+file)


    time = strftime( "%Y%m%d", localtime())
    logging.basicConfig(filename="%s\%s_log.csv" %(log_dir, time),level=logging.INFO,format='%(asctime)s;%(levelname)s;%(message)s')
    logFormatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

def main():
    settings = Settings()
    setLogging(settings)

    controller = Controller(name="Visually Structured", settings=settings)
    controller.StartGUI()


    logging.info("Closing Software")

if __name__ == '__main__':
    main()