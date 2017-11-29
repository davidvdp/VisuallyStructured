from tkinter import *
from tkinter import messagebox
import logging
from GUI.GUIInterface import *

class ViewMenu(View):
    def __init__(self, parent):
        self.menu = Menu(parent.root)
        parent.root.config(menu=self.menu)
        filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.onNewFile)
        filemenu.add_command(label="Open...", command=self.onOpenFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=parent.root.quit)

        helpmenu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.onAbout)

        self._parent = parent

    def onNewFile(self):
        if messagebox.askyesno("New Flow", "Are you sure you want to start a new flow?\nUnsaved work will be lost."):
            self.GetController().NewFlow()

    def onOpenFile(self):
        name = askopenfilename()
        print("onOpenFile not implemented")

    def onAbout(self):
        print("onAbout not implemented")

    def Start(self):
        pass