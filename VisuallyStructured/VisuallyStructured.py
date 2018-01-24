from Controller import *
import logging
from time import localtime, strftime
import os
from StandardSettings import Settings

from Filters import Blur, Sobel, Normalize, HeatMap, Debayer, LightCorrection, AddValue, MultiplyValue, SelectChannel
from Grabbers import File, picam
#TODO: Instead of pickeling, save settings to human readable YAML
#TODO: Create tree like structure for properties within a block
#TODO: Use icon to distinguish block types from one another

#TODO: Should also work headless
#TODO: Add conditions / multiple columns / for x in bla
#TODO: Allow for the use of del ctrl-c, ctrl-v etc.
#TODO: Make sure that all user events have a try catch
#TODO: Think of a name. Visico, VisuallyScructured
#TODO: Add ruler profile and histogram options for image analysis
#TODO: value tool on mouse over
#TODO: Add Icons for grabber, filter, meas and condition
#TODO: When adding blocks to a already saved and loaded flw name is not automatically indexed like Sobel_1 Sobel_2 etc
#TODO: When setting up grabber extension filter is not OK
#TODO: Cannot insert new block in between two other blocks
#TODO: Automatic new line for text in block
#TODO: Feedback for saving changes for property does also popup when current block is selected again.


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
            try:
                os.remove(os.path.join( log_dir, file) )
            except PermissionError as ex:
                logging.error("Could not remove file %s due to permission error." %os.path.join( log_dir, file))


    time = strftime( "%Y%m%d", localtime())
    try:
        logging.basicConfig(filename="%s_log.csv" %(os.path.join( log_dir, time )),level=logging.INFO,format='%(asctime)s;%(levelname)s;%(message)s')
    except PermissionError as ex:
        logging.error("Could not create logging file %s due to permission error." % os.path.join(log_dir, time))

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