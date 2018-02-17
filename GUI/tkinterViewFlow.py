import logging
from tkinter import *
from tkinter.font import Font
from GUI.GUIInterface import *
from FlowBlocks import FlowBlockFactory
from SubjectObserver import Observer
import inspect


class ViewFlow(Observer, View):
    """Takes care of the presentation of the Flow diagram."""

    def __init__(self, parent, col=0, row=0, root=None):
        super().__init__(parent, col=col, row=row, scrollbars=True, sticky=NSEW, root=root)
        self._startCircle = None
        self._addblock = None

        self._currentFlowBlocks = []

    def Start(selfs):
        pass

    def Redraw(self):
        pass

    def Update(self):
        # get current flow
        startBlock = self.get_controller().flow.GetFlow().GetStartBlock()

        # clear everything
        while len(self._currentFlowBlocks) is not 0:
            flowObject = self._currentFlowBlocks.pop()
            flowObject._destroy()

        if self._startCircle is not None:
            self._startCircle._destroy()
            self._startCircle = None

        if self._addblock is not None:
            self._addblock._destroy()
            self._addblock = None

        # first add start block
        self._startCircle = FlowStartBlockGUI(self)

        # then add all blocks from flow
        while startBlock is not None:
            self._currentFlowBlocks.append(FlowActionBlockGUI(self, startBlock))
            nextSteps = startBlock.GetNextSteps()
            if len(nextSteps):
                startBlock = nextSteps[0]
            else:
                startBlock = None

        # finish by adding a + block for adding extra blocks
        self._addblock = FlowAddBlockGUI(self)


class FlowBlockGUI(object):
    def __init__(self, parent: ViewFlow, name: str, flow_block_object=None, height=150):
        self._flowBlockObject = flow_block_object
        self._colorHover = "white"
        self._colorClick = "grey"
        self._color = "lightblue"
        self._w = Canvas(parent._frame, width=100, height=height)
        self._w.pack()
        self._w.bind("<Button-1>", self._on_click_coloring_button_press)
        self._w.bind("<ButtonRelease-1>", self._on_click_coloring_button_release)
        self._w.bind("<ButtonRelease-3>", self.__on_right_click_coloring)
        self._w.bind("<Enter>", self.__on_hover_enter)
        self._w.bind("<Leave>", self.__on_hover_leave)
        self._entered = False
        self._parent = parent

    def _destroy(self):
        '''This is used to forget this block. Used when the flow is updated.'''
        self._w.destroy()
        self._w.pack_forget()

    def draw_arrow(self, start, end):
        """
        Draws arrow from bottom of block to end of block frame.
        :param start: start coordinates as a tuple of the arrow
        :param end: end coordinates as a tuple of the arrow
        :return:
        """
        self._w.create_line(start[0], start[1], end[0], end[1])
        sizeArrowPoint = 10
        pointsPolygon = [end[0], end[1], end[0] - sizeArrowPoint / 2, end[1] - sizeArrowPoint,
                         end[0] + sizeArrowPoint / 2, end[1] - sizeArrowPoint]
        self._w.create_polygon(pointsPolygon)

    def _on_click_coloring_button_press(self, event):
        self._w.itemconfig(self._block, fill=self._colorClick)
        self._w.update_idletasks()

    def _on_click_coloring_button_release(self, event):
        if self._entered:
            self._w.itemconfig(self._block, fill=self._colorHover)
        else:
            self._w.itemconfig(self._block, fill=self._color)
        self._w.update_idletasks()
        self.OnLeftClick(event)

    def __on_right_click_coloring(self, event):
        self.OnRightClick(event)

    def __on_hover_enter(self, event):
        self._w.itemconfig(self._block, fill=self._colorHover)
        self._w.update_idletasks()
        self._entered = True

    def __on_hover_leave(self, event):
        self._w.itemconfig(self._block, fill=self._color)
        self._w.update_idletasks()
        self._entered = False

    def ContextMenu(self, x, y):
        factory = FlowBlockFactory()
        types = factory.GetTypes()

        rmenu = Menu(self._parent._frame, tearoff=0, takefocus=0)
        flowBlockMenu = Menu(self._parent._frame)
        rmenu.add_cascade(label="Add Block", menu=flowBlockMenu)
        for type in types:
            flowBlockMenu.add_command(label=type, command=lambda t=type: self.ContextFlowBlockSelected(t))
        rmenu.add_command(label="Delete", command=self.delete)
        rmenu.add_command(label="Rename...", command=self.rename)

        self._parent._frame.tk.call('tk_popup', rmenu, x, y)

    def delete(self):
        '''Sends a remove request to the controller. The actual removal is done with an update of the flow.'''
        self._parent._parent.controller.flow.RemoveBlock(self._flowBlockObject)

    def rename(self):
        '''Opens a dialog asking user to enter a new name'''

        class RenameDialog:
            def __init__(self, parent):
                top = self.top = Toplevel(parent._frame)

                Label(top, text="New Name").pack()

                self.e = Entry(top)
                self.e.pack(padx=5)

                b = Button(top, text="OK", command=self.ok)
                b.pack(pady=5)

                self.new_name = None

            def ok(self):
                self.new_name = self.e.get()
                self.top.destroy()

        dialog = RenameDialog(self._parent)
        self._parent._frame.wait_window(dialog.top)
        if dialog.new_name is None or dialog.new_name == "":
            return  # invalid name specified
        if self._flowBlockObject.name == dialog.new_name:
            return  # did not change
        self._parent.get_controller().flow.change_name_of_block(self._flowBlockObject, dialog.new_name)

        # self.parent.parent.controller.SetVariableValueByID(self.id, value=newvalue)

    def ContextFlowBlockSelected(self, type):
        logging.info("Adding flowblock of type %s" % type)
        self._parent._parent.controller.flow.AddBlock(blocktype=type, afterblock=self._flowBlockObject)

    def OnLeftClick(self, event):
        logging.warning("OnLeftClick was not implemented for this type op block.")

    def OnRightClick(self, event):
        logging.warning("OnRightClick was not implemented for this type op block.")


class FlowStartBlockGUI(FlowBlockGUI):
    """Circle that represents the start of the flow and image source"""

    def __init__(self, master):
        height = 100
        super(FlowStartBlockGUI, self).__init__(master, "Start", height=height)
        self._block = self._w.create_oval(2, 2, 100, 50, fill=self._color)
        self._w.create_text(50, 25, text="Start")
        self.draw_arrow((50, 50), (50, height))

    def OnLeftClick(self, event):
        pass


class FlowActionBlockGUI(FlowBlockGUI):
    """Square that represents a flow action"""

    def __init__(self, master, flow_block_object: FlowBlockGUI):
        super(FlowActionBlockGUI, self).__init__(master, name=flow_block_object.name,
                                                 flow_block_object=flow_block_object)
        self._block = self._w.create_rectangle(2, 2, 100, 100, fill=self._color)
        self._w.create_text(50, 50, text=flow_block_object.name)
        small = Font(size=7, weight='bold')
        self._w.create_text(4, 4, text=flow_block_object.type, anchor="nw", font=small)
        self.draw_arrow((50, 100), (50, 150))

    def OnRightClick(self, event):
        try:
            self.ContextMenu(event.x_root, event.y_root)
        except:
            if (__debug__):
                raise sys.exc_info()[0](sys.exc_info()[1])
            logging.error("Unexpected error: %s; " % (sys.exc_info()[0], sys.exc_info()[1]))

    def OnLeftClick(self, event):
        '''This loads the parameters of the block in the properties window'''
        self._parent.get_controller().OpenPropertiesWindowsFor(self._flowBlockObject)



class FlowAddBlockGUI(FlowBlockGUI):
    """Square that represents a flow action"""

    def __init__(self, master):
        super(FlowAddBlockGUI, self).__init__(master, "+", height=50)
        helv36 = Font(family='Helvetica', size=36, weight='bold')
        self._block = self._w.create_text(50, 25, text="+", font=helv36, fill=self._color)

    def OnLeftClick(self, event):
        try:
            self.ContextMenu(event.x_root, event.y_root)
        except:
            if (__debug__):
                raise sys.exc_info()[0](sys.exc_info()[1])
            logging.error("Unexpected error: %s; " % (sys.exc_info()[0], sys.exc_info()[1]))
