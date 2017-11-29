import logging
from tkinter import *
from tkinter.font import Font
from GUI.GUIInterface import *
from FlowBlocks import *
import inspect

class ViewFlow(Observer,View):
    """Takes care of the presentation of the Flow diagram."""
    def __init__(self, parent, col=0, row=0, root=None):
        super().__init__(parent, col=col, row=row, scrollbars=True, sticky=NSEW, root=root)
        self._startCircle = None
        self._addblock = None
        #self._frameButtons = Frame(parent.root)
        #self._frameButtons.pack()

        self._currentFlowBlocks = []
        #self.Update()

    def Start(selfs):
        pass

    def Redraw(self):
        pass

    def Update(self):
        # get current flow
        startBlock = self.GetController().GetFlow().GetStartBlock()

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
        self._startCircle = FlowStartBlock(self)

        # then add all blocks from flow
        while startBlock is not None:
            self._currentFlowBlocks.append(FlowActionBlock(self, startBlock.name, startBlock))
            nextSteps =  startBlock.GetNextSteps()
            if len(nextSteps):
                startBlock = nextSteps[0]
            else:
                startBlock = None

        # finish by adding a + block for adding extra blocks
        self._addblock = FlowAddBlock(self)


class FlowBlock(object):
    def __init__(self,parent, name, flowblockobject=None,height=150):
        self._flowBlockObject = flowblockobject
        self._colorHover = "white"
        self._colorClick = "grey"
        self._color = "lightblue"
        self._w = Canvas(parent._frame, width=100, height=height)
        self._w.pack()
        self._w.bind("<Button-1>", self._onClickColoring)
        self._w.bind("<ButtonRelease-1>", self._onClickColoring)
        self._w.bind("<ButtonRelease-3>", self.__onRightClickColoring)
        self._w.bind("<Enter>", self.__onHover)
        self._w.bind("<Leave>", self.__onHover)
        self._entered = False
        self._parent = parent

    def _destroy(self):
        '''This is used to forget this block. Used when the flow is updates.'''
        self._w.destroy()
        self._w.pack_forget()

    def drawArrow(self, w, start, end):
        w.create_line(start[0], start[1], end[0], end[1])
        sizeArrowPoint = 10
        pointsPolygon = [end[0], end[1], end[0] - sizeArrowPoint / 2, end[1] - sizeArrowPoint,
                         end[0] + sizeArrowPoint / 2, end[1] - sizeArrowPoint]
        w.create_polygon(pointsPolygon)

    def _onClickColoring(self,event):
        if (event.type is EventType.ButtonPress):
                self._w.itemconfig(self._block, fill=self._colorClick)
                self._w.update_idletasks()
        elif (event.type is EventType.ButtonRelease):
            if self._entered:
                self._w.itemconfig(self._block, fill=self._colorHover)
            else:
                self._w.itemconfig(self._block, fill=self._color)
            self._w.update_idletasks()
            self.OnLeftClick(event)

    def __onRightClickColoring(self, event):
        if (event.type is EventType.ButtonRelease):
            self.OnRightClick(event)

    def __onHover(self, event):
        if (event.type is EventType.Enter):
                self._w.itemconfig(self._block, fill=self._colorHover)
                self._w.update_idletasks()
                self._entered = True
        elif (event.type is EventType.Leave):
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
            flowBlockMenu.add_command(label=type, command=lambda t=type: self.ContextFlowBlockSelected(t) )
        rmenu.add_command(label="Delete", command=self.Delete)

        self._parent._frame.tk.call('tk_popup', rmenu, x, y)

    def Delete(self):
        '''Sends a remove request to the controller. The actual removal is done with an update of the flow.'''
        self._parent._parent.controller.RemoveBlock(self._flowBlockObject)

    def ContextFlowBlockSelected(self, type):
        logging.info("Adding flowblock of type %s" %type)
        self._parent._parent.controller.AddBlock(blocktype=type,afterblock=self._flowBlockObject)

    def OnLeftClick(self,event):
        logging.warning("OnLeftClick was not implemented for this type op block.")

    def OnRightClick(self,event):
        logging.warning("OnRightClick was not implemented for this type op block.")


class FlowStartBlock(FlowBlock):
    """Circle that represents the start of the flow and image source"""
    def __init__(self, master):
        super(FlowStartBlock,self).__init__(master, "Start")
        self._block = self._w.create_oval(2, 2, 100, 100, fill=self._color)
        self._w.create_text(50,50,text="Start")
        self.drawArrow(self._w,(50,100),(50,150))

    def OnLeftClick(self,event):
        pass


class FlowActionBlock(FlowBlock):
    """Square that represents a flow action"""
    def __init__(self, master, name, flowblockobject):
        super(FlowActionBlock,self).__init__(master, name, flowblockobject=flowblockobject)
        self._block = self._w.create_rectangle(2, 2, 100, 100, fill=self._color)
        self._w.create_text(50,50,text=name)
        self.drawArrow(self._w,(50,100),(50,150))

    def OnRightClick(self,event):
        try:
            self.ContextMenu(event.x_root, event.y_root)
        except:
            if (__debug__):
                raise sys.exc_info()[0](sys.exc_info()[1])
            logging.error("Unexpected error: %s; " %(sys.exc_info()[0],sys.exc_info()[1]))

    def OnLeftClick(self,event):
        '''This loads the parameters of the block in the properties window'''
        try:
            self._parent.GetController().OpenPropertiesWindowsFor(self._flowBlockObject)
        except:
            if (__debug__):
                raise sys.exc_info()[0](sys.exc_info()[1])
            logging.error("Unexpected error: %s; " %(sys.exc_info()[0],sys.exc_info()[1]))


class FlowAddBlock(FlowBlock):
    """Square that represents a flow action"""
    def __init__(self, master):
        super(FlowAddBlock,self).__init__(master, "+", height=50)
        #self._block = self._w.create_oval(2, 2, 100, 100, fill=self._color)
        helv36 = Font(family='Helvetica',size=36, weight='bold')
        self._block = self._w.create_text(50,25,text="+",font=helv36, fill=self._color)
        #self._w.create_text(50,50,text="+")

    def OnLeftClick(self,event):
        try:
            self.ContextMenu(event.x_root, event.y_root)
        except:
            if (__debug__):
                raise sys.exc_info()[0](sys.exc_info()[1])
            logging.error("Unexpected error: %s; " %(sys.exc_info()[0],sys.exc_info()[1]))
