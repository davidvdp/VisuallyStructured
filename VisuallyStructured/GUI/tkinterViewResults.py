import logging
from tkinter import *
from tkinter.ttk import Notebook
from GUI.GUIInterface import *
from PIL import Image, ImageTk
import numpy as np
import cv2
import matplotlib.pyplot as plt
from Variables import *
from SubjectObserver import Observer

class ImageTab(Frame):
    def __init__(self, name, notebook):
        super().__init__(notebook)
        self._notebook = notebook
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._canvas = Canvas(self)
        self._canvas.columnconfigure(0, weight=1)
        self._canvas.rowconfigure(0, weight=1)
        self._canvas.config(highlightthickness=0)

        self._sbarVertical = Scrollbar(self, orient=VERTICAL)
        self._sbarHorizontal = Scrollbar(self, orient=HORIZONTAL)
        self._sbarVertical.config(command=self._canvas.yview)
        self._sbarHorizontal.config(command=self._canvas.xview)
        self._canvas.config(yscrollcommand=self._sbarVertical.set)
        self._canvas.config(xscrollcommand=self._sbarHorizontal.set)
        self._canvas.config(background='black')

        self._scale = 1
        self._name = name
        self.SetTabTitle()
        #self._tabid = notebook.index(nameComplete)
        self._canvas.grid(sticky=NSEW, row=0, column=0)

        self._sbarVertical.grid(sticky=N+S,row=0,column=1)
        self._sbarHorizontal.grid(sticky=E + W, row=1, column=0)

        self._canvas.bind("<MouseWheel>", self._onMouseWheel )
        self._canvas.bind("<Button-3>", self._onRightButton)
        self.npimage = None

    def SetTabTitle(self, customText = None):
        zoomlevel = self._scale * 100
        if customText:
            name = "%s (%s, %d%%)" % (self._name, customText, zoomlevel)
        else:
            name = "%s (%d%%)" %(self._name, zoomlevel)
        self._notebook.add(self, text=name )

    def GetName(self):
        return self._name

    def _onRightButton(self,event):
        self.ContextMenu(event.x_root, event.y_root)

    def ZoomIn(self):
        newscale = self.GetScale() * 1.2
        self.RescaleImage(newscale)

    def ZoomOut(self):
        newscale = self.GetScale() / 1.2
        self.RescaleImage(newscale)

    def ZoomFit(self):
        widthFrame = self.winfo_width()
        heightFrame = self.winfo_height()

        heightImage = self.npimage.shape[0]
        widthImage = self.npimage.shape[1]

        widthRatio = widthFrame/widthImage
        heightRatio = heightFrame/heightImage

        if widthRatio < heightRatio:
            newscale = widthRatio
        else:
            newscale = heightRatio

        self.RescaleImage(newscale)
        self.SetTabTitle("Fit")

    def _onMouseWheel(self, event):
        if event.delta < 0:
            scalechange = 1/(-event.delta/100)
        else:
            scalechange = event.delta/100
        newscale = self.GetScale() * scalechange
        self.RescaleImage(newscale)

    def SetImage(self, npimage):

        if self.npimage is npimage:
            return

        if len(npimage.shape) is 3:
            npimage = cv2.cvtColor( npimage, cv2.COLOR_BGR2RGB)

        self.npimage = npimage
        self.RescaleImage()

    def GetScale(self):
        return self._scale

    def SetScale(self, scale):
        if scale < 0.00001: return
        self._scale = scale

    def RescaleImage(self, scale = None):
        if scale:
            self.SetScale(scale)
            if scale < 0.00001:
                return

        newSize = [0.0,0.0]
        newSize[0] = self.npimage.shape[1] * self._scale # width
        newSize[1] = self.npimage.shape[0] * self._scale  # height
        if newSize[0] < 1:
            return
        if newSize[1] < 1:
            return
        rescaledimages = cv2.resize(self.npimage,(int(newSize[0]),int(newSize[1])))
        height = rescaledimages.shape[0]
        width = rescaledimages.shape[1]
        self._canvas.config(scrollregion=(0, 0, width, height))
        #self.im = Image.fromarray(plt.cm.gist_earth(rescaledimages, bytes=True))
        if len(self.npimage.shape) is 3:
            self.im = Image.frombytes('RGB', (rescaledimages.shape[1], rescaledimages.shape[0]), rescaledimages.astype('b').tostring())
        else:
            self.im = Image.frombytes('L', (rescaledimages.shape[1], rescaledimages.shape[0]), rescaledimages.astype('b').tostring())
        self.photo = ImageTk.PhotoImage(image=self.im)
        self._canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.SetTabTitle()

    def ContextMenu(self, x, y):
        rmenu = Menu(self, tearoff=0, takefocus=0)
        rmenu.add_command(label="Zoom In (Scroll wheel)", command=self.ZoomIn)
        rmenu.add_command(label="Zoom Out (Scroll wheel)", command=self.ZoomOut)
        rmenu.add_command(label="Zoom Fit", command=self.ZoomFit)
        rmenu.add_command(label="Zoom 100%", command=lambda: self.RescaleImage(scale=1.0))

        self.tk.call('tk_popup', rmenu, x, y)

class ViewResults(Observer, View):
    """Takes care of the presentation of the Flow diagram."""
    def __init__(self, parent, col=0, row=0, root=None):
        super().__init__(parent, col=col, row=row, sticky=NSEW, scrollbars=False, root=root)
        self._notebook = Notebook(self._frame, name="nb")
        self._notebook.columnconfigure(0, weight=1)
        self._notebook.rowconfigure(0, weight=1)
        self._notebook.config()
        self._notebook.grid(sticky=NSEW)
        self._notebook.grid(sticky=NSEW)
        self._tabs = []
        self._results = None

        #TODO: Work around below should be fixed; need to create a tab first and delete it, or background is old image in constant scale.
        name_init = "initialization_image"
        self.AddTab(np.zeros((1,1,3),dtype=np.uint8), name_init)
        self.RemoveTab(name_init)

    def RemoveTab(self, name):
        for tab in self._tabs:
            if name is tab.GetName():
                tab.destroy()
                self._tabs.remove(tab)

    def AddTab(self, npimage, name):

        if npimage is None:
            return

        for tab in self._tabs:
            if tab.GetName() == name:
                tab.SetImage(npimage=npimage)
                return

        tab = ImageTab(name=name,notebook=self._notebook)

        tab.SetImage(npimage=npimage)
        self._tabs.append(tab)

    def __findAllImagesAndShow(self):
        if self._results is None:
            return
        imageVars = self._results.FindAllOfType(ImageVar().name)
        for key, var in imageVars.items():
            name = key.split(".")[0]
            self.AddTab(var.value,name)

    def Update(self):
        self._results = self.get_controller().GetResults()
        self.__findAllImagesAndShow()


