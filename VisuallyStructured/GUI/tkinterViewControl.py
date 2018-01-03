import logging
from tkinter import *
from GUI.GUIInterface import *
from SubjectObserver import Observer

class ViewControl(Observer,View):
    """Takes care of the presentation of the Flow diagram."""
    def __init__(self, parent, col=0, row=0):
        super().__init__(parent, col=col, row=row)
        self.control_image_pause = PhotoImage(file="GUI\\icons\\control_pause.png")
        self.control_image_single_run = PhotoImage(file="GUI\\icons\\control_single_run.png")
        self.control_image_single_step = PhotoImage(file="GUI\\icons\\control_single_step.png")

        self._buttonPause = Button(self._frame,
                                   #text="Pause", fg="red",
                                   command=self.FlowPause,
                                   image=self.control_image_pause)
        self._buttonPause.pack(side=LEFT)

        self._buttonNextStep = Button(self._frame,
                                      #text="Next Step",
                                    command=self.FlowNextStep,
                                    image=self.control_image_single_step)
        self._buttonNextStep.pack(side=LEFT)

        self._buttonStart = Button(self._frame,
                                   #text="Start", fg="green",
                                   command=self.FlowStart,
                                   image=self.control_image_single_run)
        self._buttonStart.pack(side=LEFT)



    def FlowStart(self):
        self._parent.controller.flow.run_flow_once()
        #logging.warning("Starting flow has not been implemented yet.")
        #raise NotImplementedError("Starting flow has not been implemented yet.")

    def FlowPause(self):
        logging.warning("Pausing flow has not been implemented yet.")
        raise NotImplementedError("Pausing flow has not been implemented yet.")


    def FlowNextStep(self):
        self._parent.controller.flow.execute_next_step_level()
        #logging.warning("Steppingg though flow has not been implemented yet.")
        #raise NotImplementedError("Steppingg though flow has not been implemented yet.")