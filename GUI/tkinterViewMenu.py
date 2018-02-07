from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import logging
from GUI.GUIInterface import View
import os

class ViewMenu(View):
    def __init__(self, parent):
        self.menu = Menu(parent.root)
        parent.root.config(menu=self.menu)
        filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.onNewFile)
        filemenu.add_command(label="Open...", command=self.on_open_file)
        filemenu.add_command(label="Save As...", command=self.on_save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=parent.root.quit)

        helpmenu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.onAbout)

        self.__file_types =[("Flow File", "*.flw")]

        self._parent = parent

    def onNewFile(self):
        if messagebox.askyesno("New Flow", "Are you sure you want to start a new flow?\nUnsaved work will be lost."):
            self.get_controller().flow.NewFlow()

    def on_open_file(self):
        last_selected_dir = self.get_controller().settings.last_selected_dir
        filename = filedialog.askopenfilename(defaultextension=".flw",
                                                initialdir=last_selected_dir,
                                                initialfile="Untitled.flw",
                                                filetypes=self.__file_types)
        if filename == None:
            return

        self.get_controller().flow.load_flow_from_file(filename)

    def on_save_file(self):
        last_selected_dir = self.get_controller().settings.last_selected_dir
        filename = filedialog.asksaveasfilename(defaultextension=".flw",
                                            initialdir=last_selected_dir,
                                            initialfile="Untitled.flw",
                                            filetypes=self.__file_types)
        if filename == None:
            return

        self.get_controller().flow.save_flow_to_file(filename)

    def onAbout(self):
        print("onAbout not implemented")

    def Start(self):
        pass