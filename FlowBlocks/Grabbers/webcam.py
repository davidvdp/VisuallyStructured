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
        self.__thread = Thread(target=self.__start_capture_thread, args=[self.__image_buffer])

    def close(self):
        logging.info("Stopping %s capture thread." % self.name)
        self.__thread_run = False

    def __start_capture(self):
        logging.info("Starting %s capture." % self.name)
        self.__thread_run = True
        self.__thread.start()
        self.__capture_started = True

    def __start_capture_thread(self, image_buffer):
        class WebCamCapture(object):
            def __enter__(self):
                self.camera = cv2.VideoCapture(0)
                return self.camera

            def __exit__(self, type, value, traceback):
                self.camera.release()

        with WebCamCapture() as camera:
            while self.__thread_run:
                _, image = camera.read()
                if image_buffer.full():
                    image_buffer.get_nowait()
                image_buffer.put_nowait(image)

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