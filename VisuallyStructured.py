import logging
import os
from time import localtime, strftime

from Controller import Controller
from StandardSettings import Settings


# these imports make the blocks available for the blockfactory.
from FlowBlocks.Filters import Blur, Sobel, Normalize, HeatMap, Debayer, LightCorrection, AddValue, MultiplyValue, \
    SelectChannel
from FlowBlocks.Grabbers import File, picam, webcam
from FlowBlocks import save_image, lidar_lite_v2, data_logger

# TODO: Create tree like structure for properties within a block
# TODO: Use icon to distinguish block types from one another

# TODO: Add conditions / multiple columns / for x in bla
# TODO: Allow for the use of del ctrl-c, ctrl-v etc.
# TODO: Make sure that all user events have a try catch
# TODO: Think of a name. Visico, VisuallyStructured
# TODO: Add ruler profile and histogram options for image analysis
# TODO: value tool on mouse over
# TODO: Add Icons for grabber, filter, meas and condition
# TODO: When adding blocks to a already saved and loaded flw name is not automatically indexed like Sobel_1 Sobel_2 etc
# TODO: When setting up grabber extension filter is not OK
# TODO: Cannot insert new block in between two other blocks
# TODO: Automatic new line for text in block
# TODO: Feedback for saving changes for property does also popup when current block is selected again.
# TODO: Add option to show results. No showing increases processing speed.
# TODO: Fix picam grabber issue; grabber thread is not properly exited.
# TODO: Add help property per variable to show in GUI.


def set_logging(settings):
    print("In here 1")
    log_dir = settings.log_dir

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    print("In here 1")
    # clean log dir
    files = os.listdir(log_dir)
    nr_files = len(files)
    max_files = settings.max_log_history_days

    print("Nr files: %d" %(max_files))

    if nr_files > max_files:
        files.sort()
        for i, file in enumerate(files):
            if i >= nr_files - max_files:
                break
            os.remove(os.path.join( log_dir, file) )

    time = strftime("%Y%m%d", localtime())

    log_file = os.path.join(log_dir, "%s_log.csv" % time)
    print(log_file)

    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s;%(levelname)s;%(message)s')
    log_formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


def main():
    settings = Settings()
    set_logging(settings)

    controller = Controller(name="Visually Structured", settings=settings)
    controller.StartGUI()

    logging.info("Closing Software")
    return 0


if __name__ == '__main__':
    exit(main())
