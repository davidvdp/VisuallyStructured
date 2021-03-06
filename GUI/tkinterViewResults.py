import logging
from tkinter import *
from tkinter.ttk import Notebook
from GUI.GUIInterface import *
from PIL import Image, ImageTk
import numpy as np
import cv2
from FlowBlocks.Variables import *
from FlowBlocks import FlowBlock
from SubjectObserver import Observer
from queue import Queue, Empty
from typing import Dict, List
from Vision.helper_functions import combine_image_and_overlay

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
        self._tabs = [] # type: List[ImageTab]
        self._results = None
        self._parent = parent
        self.image_overlay = np.empty(shape=(0,0,0), dtype=np.uint8)


        # TODO: Work around below should be fixed; need to create a tab first and delete it, or background is old image in constant scale.
        name_init = "initialization_image"
        self.add_to_tab(np.zeros((1, 1, 3), dtype=np.uint8), name_init)
        self.RemoveTab(name_init)

        self.__temp_data_queue = Queue() # used for update function to store data in

        # add custom event handler to let updates be taken care of in tk main loop
        parent.root.bind("<<ViewResults.Update>>", self.__update)
        self._notebook.bind("<<NotebookTabChanged>>", self.__on_tabchange)

        self.__last_selected_tab = None

    def __on_tabchange(self, event):
        try:
            tab_index = self._notebook.index(self._notebook.select())
        except TclError as ex:
            return # there are no tabs yet
        if self.__last_selected_tab is not None:
            self.__last_selected_tab.on_tab_deselect()
        self.__last_selected_tab = self._tabs[tab_index]
        self.__last_selected_tab.on_tab_selected()

    def RemoveTab(self, name):
        for tab in self._tabs:
            if name is tab.GetName():
                tab.destroy()
                self._tabs.remove(tab)

    def add_to_tab(self, npimage, name):
        if npimage is None:
            return

        # check if one exists; if so use that
        for tab in self._tabs:
            if tab.GetName() == name:
                tab.SetImage(npimage=npimage)
                return
        #create new tab one
        tab = ImageTab(name=name, notebook=self._notebook, parent=self)
        self._tabs.append(tab)
        self.add_to_tab(npimage=npimage, name=name)


    def __findAllImagesAndShow(self, flowblock_name):
        if self._results is None:
            return
        imageVars = self._results.FindAllOfType(ImageVar().name)
        for key, var in imageVars.items():
            name = key.split(".")[0]
            if name == flowblock_name:
                self.add_to_tab(var.value, name)

    def __draw_all_drawables_until(self, flowblock_name=None):
        '''
        Draws al drawable results to image_overlay. Images is as large as to fit all drawables.
        :param flowblock_name: draw until this block.
        :return:
        '''
        results = self.get_controller().results.get_result_dict() # type: Dict[str,Dict[str,Var]]
        self.image_overlay = np.empty(shape=(0, 0, 0), dtype=np.uint8)
        logging.debug("Starting drawing of drawables...")
        for key, value in results.items():
            for key2, value2 in value.items():
                if type(value2) == list:
                    for value3 in value2:
                        self.image_overlay = value3.draw(self.image_overlay)
                else:
                    self.image_overlay = value2.draw(self.image_overlay)
        logging.debug("Finished drawing of drawables.")

    def __update(self, event):
        self._results = self.get_controller().results.get_results_for_block()
        try:
            flowblock_name = self.__temp_data_queue.get_nowait()["flowblock_name"]
        except Empty:
            flowblock_name = None
        if not flowblock_name is None:
            # redraw al drawables
            self.__draw_all_drawables_until(flowblock_name)
            # a flowblock has just updated, go and show all containing images
            self.__findAllImagesAndShow(flowblock_name)


    def Update(self, *args, **kwargs):
        self.__temp_data_queue.put_nowait({"flowblock_name": kwargs.get("flowblock_name", None)})
        self._parent.root.event_generate("<<ViewResults.Update>>")


class ImageTab(Frame):
    def __init__(self, name, notebook, parent: ViewResults):
        super().__init__(notebook)
        self._parent = parent
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
        # self._tabid = notebook.index(nameComplete)
        self._canvas.grid(sticky=NSEW, row=0, column=0)

        self._sbarVertical.grid(sticky=N + S, row=0, column=1)
        self._sbarHorizontal.grid(sticky=E + W, row=1, column=0)

        self._canvas.bind("<MouseWheel>", self._onMouseWheel)
        self._canvas.bind("<Button-3>", self._onRightButton)
        self._canvas.bind("<Motion>", self._hover)
        self._canvas.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        self.npimage = None

        self._prev_x = None
        self._prev_y = None

        self.selected = False # is the currently selected?

    def on_tab_selected(self):
        logging.debug("Changed tab to %s." % self._name)
        self.selected = True
        self.redraw_image()

    def on_tab_deselect(self):
        self.selected = False

    def update_mouse_hover_info(self, x, y):
        """
        Updates the info that is displayed in the control view as the mouse moves over the image displayed
        :param x: x location in image that is displayed
        :param y: y location in image that is dusplayed
        """
        if not self.selected: # only show values for the selected tab
            return
        if x is None or y is None:
            return
        if self.npimage is None:
            return
        if self._scale == 0:
            return
        image_height, image_width = self.npimage.shape[:2]
        x_scaled = x / self._scale
        y_scaled = y / self._scale
        x_scaled = int(x_scaled)
        y_scaled = int(y_scaled)
        if x_scaled >= image_width:
            return
        if y_scaled >= image_height:
            return
        if x_scaled < 0:
            return
        if y_scaled < 0:
            return
        self._parent._parent.viewcontrol.show_mouse_location_info(x_scaled, y_scaled, self.npimage[y_scaled, x_scaled])

    def _hover(self, event):
        if self.selected:
            x, y = event.x, event.y
            self._prev_x = x
            self._prev_y = y
            self.update_mouse_hover_info(x,y)

    def SetTabTitle(self, customText=None):
        zoomlevel = self._scale * 100
        if customText:
            name = "%s (%s, %d%%)" % (self._name, customText, zoomlevel)
        else:
            name = "%s (%d%%)" % (self._name, zoomlevel)
        self._notebook.add(self, text=name)

    def GetName(self):
        return self._name

    def _onRightButton(self, event):
        self.ContextMenu(event.x_root, event.y_root)

    def ZoomIn(self):
        newscale = self.GetScale() * 1.2
        self.redraw_image(newscale)

    def ZoomOut(self):
        newscale = self.GetScale() / 1.2
        self.redraw_image(newscale)

    def ZoomFit(self):
        widthFrame = self.winfo_width()
        heightFrame = self.winfo_height()

        heightImage = self.npimage.shape[0]
        widthImage = self.npimage.shape[1]

        widthRatio = widthFrame / widthImage
        heightRatio = heightFrame / heightImage

        if widthRatio < heightRatio:
            newscale = widthRatio
        else:
            newscale = heightRatio

        self.redraw_image(newscale)
        self.SetTabTitle("Fit")

    def _onMouseWheel(self, event):
        if event.delta < 0:
            scalechange = 1 / (-event.delta / 100)
        else:
            scalechange = event.delta / 100
        newscale = self.GetScale() * scalechange
        self.redraw_image(newscale)

    def SetImage(self, npimage):
        if self.npimage is npimage:
            return

        if len(npimage.shape) is 3:
            npimage = cv2.cvtColor(npimage, cv2.COLOR_BGR2RGB)

        self.npimage = npimage
        self.redraw_image()
        # we need new information for the mouse pointer since the image has changed.
        self.update_mouse_hover_info(self._prev_x, self._prev_y)

    def GetScale(self):
        return self._scale

    def SetScale(self, scale):
        if scale < 0.00001: return
        self._scale = scale

    def redraw_image(self, scale=None):
        if not self.selected: # we do not need to draw anything because the tab is not shown
            return

        if scale:
            self.SetScale(scale)
            if scale < 0.00001:
                return

        if abs(self._scale - 1) > 0.01:
            newSize = [0.0, 0.0]
            newSize[0] = self.npimage.shape[1] * self._scale  # width
            newSize[1] = self.npimage.shape[0] * self._scale  # height
            if newSize[0] < 1:
                return
            if newSize[1] < 1:
                return
            rescaledimages = cv2.resize(self.npimage, (int(newSize[0]), int(newSize[1])))
            rescaledOverlay = None
            if self._parent.image_overlay.shape[0] > 0:
                rescaledOverlay = cv2.resize(self._parent.image_overlay, None, fx=scale, fy=scale)

        else:
            rescaledimages = self.npimage
            rescaledOverlay = self._parent.image_overlay

        if rescaledOverlay and rescaledOverlay.shape[0] != 0 and rescaledOverlay.shape[1] != 0:
            rescaledimages = combine_image_and_overlay(rescaledimages, rescaledOverlay)
        height = rescaledimages.shape[0]
        width = rescaledimages.shape[1]
        self._canvas.config(scrollregion=(0, 0, width, height))
        # self.im = Image.fromarray(plt.cm.gist_earth(rescaledimages, bytes=True))
        if len(rescaledimages.shape) is 3:
            self.im = Image.frombytes('RGB', (rescaledimages.shape[1], rescaledimages.shape[0]),
                                      rescaledimages.astype('b').tostring())
        else:
            self.im = Image.frombytes('L', (rescaledimages.shape[1], rescaledimages.shape[0]),
                                      rescaledimages.astype('b').tostring())
        self.photo = ImageTk.PhotoImage(image=self.im)
        self._canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.SetTabTitle()

    def ContextMenu(self, x, y):
        rmenu = Menu(self, tearoff=0, takefocus=0)
        rmenu.add_command(label="Zoom In (Scroll wheel)", command=self.ZoomIn)
        rmenu.add_command(label="Zoom Out (Scroll wheel)", command=self.ZoomOut)
        rmenu.add_command(label="Zoom Fit", command=self.ZoomFit)
        rmenu.add_command(label="Zoom 100%", command=lambda: self.redraw_image(scale=1.0))

        self.tk.call('tk_popup', rmenu, x, y)


