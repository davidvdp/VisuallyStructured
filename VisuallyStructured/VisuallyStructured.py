from Controller import *
import logging

from Filters import Sobel
from Filters import Blur
from Grabbers import File

#TODO: Make it multithreaded. Manage threads in controller
#TODO: Execute Filters
#TODO: Add option to change block names

#TODO: Add conditions / multiple columns
#TODO: Allow for the use of del ctrl-c, ctrl-v etc.
#TODO: Make sure that all user events have a try catch
#TODO: Think of a name. Visico, VisuallyScructured


def setLogging():
    logging.basicConfig(filename="log.csv",level=logging.INFO,format='%(asctime)s;%(levelname)s;%(message)s')
    logFormatter = logging.Formatter('%(asctime)s; %(levelname)s; %(message)s')
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

def main():
    setLogging()

    controller = Controller(name="Visually Structured")
    controller.StartGUI()


    print("Closing Software")

if __name__ == '__main__':
    main()