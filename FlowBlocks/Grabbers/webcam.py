import logging
from time import sleep
import cv2
from threading import Thread
from queue import Queue

from FlowBlocks.Variables import BoolVar
from FlowBlocks import FlowBlockGrabber
from FlowBlocks import FlowBlockFactory

class WebCam(FlowBlockGrabber):
    type_name = "WebCam"

    def __init__(self, name=type_name):
        super().__init__(name=name)
        self.SubVariables = {
            "Gray": BoolVar(False)
        }

        self.__capture_started = False
        # TODO: Queuesize should be a setting. It allows for passed frames to be processed as well.
        self.__image_buffer = Queue(1)
        self.__thread_run = False
        self.__thread = None

    def close(self):
        logging.debug("Trying to stop %s capture thread." % self.name)
        self.__thread_run = False
        cnt = 0
        while self.__thread.is_alive():
            sleep(0.01)
            cnt += 1
            if cnt > 500:
                logging.error("Could not stop %s capture thread." % self.name)
                break
        logging.info("Stopped %s capture thread." % self.name)

    def __start_capture(self):
        logging.debug("Trying to start %s capture." % self.name)
        try:
            self.__thread_run = True
            self.__thread = Thread(target=self.__start_capture_thread, args=[self.__image_buffer])
            if self.__thread.is_alive():
                logging.error("Could not start capture thread for %s because it is still alive." %self.name)
                return
            self.__thread.start()
            self.__capture_started = True
        except RuntimeError as ex:
            logging.exception("Error while trring to start capture thread for %s" %self.name)

    def __start_capture_thread(self, image_buffer):
        # class that allows you to use with ...
        class WebCamCapture(object):
            def __enter__(self):
                self.camera = cv2.VideoCapture(0)
                return self.camera

            def __exit__(self, type, value, traceback):
                self.camera.release()
        logging.info("Starting %s capture thread..." % self.name)
        try:
            with WebCamCapture() as camera:
                while self.__thread_run:
                    print("test")
                    _, image = camera.read()
                    if image_buffer.full():
                        # if full remove oldest frame and add new one
                        image_buffer.get_nowait()
                    image_buffer.put_nowait(image)
        except Exception as e:
            logging.exception("Error while trying to capture in %s" %self.name)
        finally:
            self.__thread_run = False
            self.__capture_started = False
        logging.info("Stopping %s capture thread." % self.name)

    def __get_image(self):
        if not self.__capture_started:
            self.__start_capture()
        return self.__image_buffer.get(timeout=2)


    def execute(self, results_controller):
        logging.info("Executing %s" %self.name)
        image = self.__get_image()
        if len(image) < 1:
            logging.error("Could not capture %s frame." %self.name)
            return

        gray = self.SubVariables["Gray"].value
        if gray:
            image - cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        self.OutputVars["Image"].value = image

FlowBlockFactory.AddBlockType(WebCam)