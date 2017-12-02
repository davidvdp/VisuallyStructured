from Controller import *
import logging
from time import localtime, strftime
import os
from StandardSettings import Settings

from Filters import Sobel
from Filters import Blur
from Grabbers import File

#TODO: Add save option (Save as... and Save)
#TODO: Show save state.
#TODO: Save last used settings.
#TODO: Make it multithreaded. Manage threads in controller
#TODO: Execute Filters
#TODO: Add option to change block names
#TODO: Make start block smaller

#TODO: Add conditions / multiple columns
#TODO: Allow for the use of del ctrl-c, ctrl-v etc.
#TODO: Make sure that all user events have a try catch
#TODO: Think of a name. Visico, VisuallyScructured
#TODO: Add ruler profile and histogram options for image analysis

settings = Settings()

def setLogging():
    global settings

    log_dir = settings.settings_values["log_dir"]

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    # clean log dir
    files = os.listdir(log_dir)
    nr_files = len(files)
    max_files = settings.settings_values["max_log_history_days"]
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

    setLogging()

    controller = Controller(name="Visually Structured", settings_file="settings.xml")
    controller.StartGUI()


    logging.info("Closing Software")

if __name__ == '__main__':
    main()