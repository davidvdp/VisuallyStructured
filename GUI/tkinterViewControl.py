import logging
from tkinter import *
from GUI.GUIInterface import *
from SubjectObserver import Observer
import os


class ViewControl(Observer, View):
    """Takes care of the presentation of the Flow diagram."""

    def __init__(self, parent, col=0, row=0, columnspan=1):
        super().__init__(parent, col=col, row=row, columnspan=columnspan, sticky=NSEW)
        self.__dir_path = os.path.dirname(os.path.realpath(__file__))

        self.control_image_pause = PhotoImage(file=os.path.join(self.__dir_path, "icons/control_pause.png"))
        self.control_image_single_run = PhotoImage(file=os.path.join(self.__dir_path, "icons/control_single_run.png"))
        self.control_image_single_step = PhotoImage(file=os.path.join(self.__dir_path, "icons/control_single_step.png"))
        self.control_image_continuous = PhotoImage(file=os.path.join(self.__dir_path, "icons/control_loop.png"))

        self._buttonPause = Button(self._frame,
                                   # text="Pause", fg="red",
                                   command=self.flow_pause,
                                   image=self.control_image_pause)
        self._buttonPause.pack(side=LEFT)

        self._buttonNextStep = Button(self._frame,
                                      # text="Next Step",
                                      command=self.flow_next_step,
                                      image=self.control_image_single_step)
        self._buttonNextStep.pack(side=LEFT)

        self._buttonStart = Button(self._frame,
                                   # text="Start", fg="green",
                                   command=self.flow_start,
                                   image=self.control_image_single_run)
        self._buttonStart.pack(side=LEFT)

        self._buttonContinuous = Button(self._frame,
                                        # text="Next Step",
                                        command=self.flow_continuous,
                                        image=self.control_image_continuous)
        self._buttonContinuous.pack(side=LEFT)
        self._label_mouse_info = Label(self._frame, text=self._get_text_mouse_location_info(0, 0, "-"))
        self._label_mouse_info.pack(side=LEFT)

    def flow_start(self):
        self._parent.controller.flow.run_flow_once()

    def flow_pause(self):
        self._parent.controller.flow.stop()

    def flow_next_step(self):
        self._parent.controller.flow.execute_next_step_level()

    def flow_continuous(self):
        self._parent.controller.flow.run_flow_continous()

    def _get_text_mouse_location_info(self, x, y, color):
        return "(%d, %d) = %s" % (x, y, color)

    def show_mouse_location_info(self, x, y, color):
        self._label_mouse_info.config(text=self._get_text_mouse_location_info(x,y,color))