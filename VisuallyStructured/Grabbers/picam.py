import logging

import cv2

from Variables import Var
from Variables import PathVar, BoolVar
from Variables import ImageVar
from FlowBlocks import FlowBlockGrabber
from FlowBlocks import FlowBlockFactory

picam_imports_found = True
picam_initialized = False

__camera = None
__rawCapture = None

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    picam_imports_found = False

if picam_imports_found:
    def initialize_camera():
        global __camera
        global __rawCapture
        global picam_initialized

        if not picam_initialized:
            try:
                # for pickling to work we need to remove the camera objects from PiCam
                # initialize camera
                __camera = PiCamera()

                # initialize raw capture
                __rawCapture = PiRGBArray(__camera)

                picam_initialized = True

                logging.info("PiCam initialized.")

            except Exception as ex:
                logging.error("Could not initialize camera PiCam.")
                raise ex
        else:
            logging.info("PiCam already initialized.")

    class PiCam(FlowBlockGrabber):
        type_name = "PiCam"

        def __init__(self, name=type_name):
            super().__init__(name=name)
            self.SubVariables = {
                "Gray": BoolVar(False)
            }

            initialize_camera()

        @staticmethod
        def imported():
            global picam_imports_found
            return picam_imports_found

        def execute(self, results_controller):
            global __camera
            global  __rawCapture
            logging.info("Executing PiCam")

            frame = __camera.capture(__rawCapture, format="bgr", use_video_port=True)
            image = frame.array
            if len(image) < 1:
                logging.error("Could not capture PiCam frame.")
                return

            gray = self.SubVariables["Gray"].value
            if gray:
                image - cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

            self.OutputVars["Image"].value = image

    FlowBlockFactory.AddBlockType(PiCam)
else:
    print("Could not load PiCam block.")
    #logging.warning("Could not load block PiCam")