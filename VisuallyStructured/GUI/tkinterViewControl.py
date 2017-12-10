import logging
from tkinter import *
from GUI.GUIInterface import *
from SubjectObserver import Observer

class ViewControl(Observer,View):
    """Takes care of the presentation of the Flow diagram."""
    def __init__(self, parent, col=0, row=0):
        super().__init__(parent, col=col, row=row)
        self._buttonStart = Button(self._frame,
                                   text="Start", fg="green",
                                   command=self.FlowStart)
        self._buttonStart.pack(side=LEFT)
        self._buttonPause = Button(self._frame,
                                   text="Pause", fg="red",
                                   command=self.FlowPause)
        self._buttonPause.pack(side=LEFT)
        self._buttonNextStep = Button(self._frame,
                                      text="Next Step",
                                      command=self.FlowNextStep)
        self._buttonNextStep.pack(side=LEFT)

    def FlowStart(self):

        logging.warning("Starting flow has not been implemented yet.")
        raise NotImplementedError("Starting flow has not been implemented yet.")

    def FlowPause(self):
        logging.warning("Pausing flow has not been implemented yet.")
        raise NotImplementedError("Pausing flow has not been implemented yet.")


    def FlowNextStep(self):
        self._parent.controller.flow.ExecuteNextStepLevel()
        #logging.warning("Steppingg though flow has not been implemented yet.")
        #raise NotImplementedError("Steppingg though flow has not been implemented yet.")