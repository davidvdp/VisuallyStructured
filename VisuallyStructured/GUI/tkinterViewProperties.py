import logging
from GUI.GUIInterface import *
from FlowBlocks import *
from tkinter import filedialog
from SubjectObserver import Observer

class ViewProperties(Observer,View):
    """Takes care of the presentation of the Flow diagram."""

    class VariableField(object):
        def __init__(self, id, val, parent):
            self.parent = parent
            self.id = id
            self.val = val
            self.labelKey = None
            self.entryValueStringVar = None
            self.entryValue = None
            self.optionMenuValue = None
            self.optionMenuStringVar = None
            self.optionMenuOptions = None
            self.labelLimit = None
            self.buttonSave = None
            self.buttonOpenDir = None
            self.buttonOpenFile = None
            self.paths = None

        def OnValueSave(self):
            value = self.entryValueStringVar.get()
            newvalue = self.parent.block.SetVariableValueByID(self.id, value=value)
            self.entryValueStringVar.set(newvalue)
            self.parent.parent.controller.SetVariableValueByID(self.id, value=newvalue)

        def OnExternalValueChange(self,value=None):
            print(self.optionMenuStringVar.get())

        def OnOpenDir(self):
            directory = filedialog.askdirectory()
            self.entryValueStringVar.set(directory)


        def OnOpenFile(self):
            filename = filedialog.askopenfilename(title="Select File", filetypes=(("image files","*.jpg, *.bmp, *.png"),("all files","*.*")))
            self.entryValueStringVar.set(filename)



    def __init__(self, parent, col=0, row=0, columnspan=1):
        super().__init__(parent, col=col, row=row, scrollbars=True, columnspan=columnspan,sticky=NSEW)
        self.parent = parent
        self.SetHeight(300)
        self._frame
        self.block = None
        self.labelFrame = None

        self.variableFields = []

    def LoadProperties(self, block):
        logging.info("Loading properties for %s" %block.name)
        self.block = block
        varids = block.GetVariableIDs()

        for variableField in self.variableFields:
            variableField.labelLimit.destroy()
            variableField.entryValue.destroy()
            variableField.optionMenuValue.destroy()
            variableField.labelKey.destroy()
            if variableField.buttonOpenDir:
                variableField.buttonOpenDir.destroy()
            if variableField.buttonOpenFile:
                variableField.buttonOpenFile.destroy()

        self.variableFields = []

        if len(varids) > 0:
            # there are variables available for this block
            if self.labelFrame:
                self.labelFrame.destroy()
            self.labelFrame = LabelFrame(self._frame, text=block.name)
            self.labelFrame.grid(sticky=NSEW)
            #index = -1
            for key, val in varids.items():
                varField = ViewProperties.VariableField(key, val, self)
                self.variableFields.append(varField)


                #index += 1
                # add label
                #self.labelkeys.append(Label(self.labelFrame,text=key))
                varField.labelKey = Label(self.labelFrame,text=key)
                #self.entryvalues.append(Entry(self.labelFrame, textvalue=str(val), command=self.__onValueChange))
                varField.entryValueStringVar = StringVar(self.labelFrame)
                varField.entryValueStringVar.set(str(val))
                varField.entryValue = Entry(self.labelFrame, textvariable=varField.entryValueStringVar)
                varField.buttonSave = Button(self.labelFrame,text="Save", command=varField.OnValueSave)

                varField.optionMenuOptions = ["egg","bunny","chicken"]

                #self.externalvalues.append(OptionMenu(self.labelFrame, "", *options, command=lambda index=index: self.__onExternalValueChange))
                varField.optionMenuStringVar = StringVar(self.labelFrame)
                varField.optionMenuStringVar.set("")
                varField.optionMenuValue = OptionMenu(self.labelFrame, varField.optionMenuStringVar, *varField.optionMenuOptions, command=varField.OnExternalValueChange)

                limits = block.GetLimits(key)
                limitsAvailable = False
                if limits is not None and len(limits) > 0:
                    for key2, val2 in limits.items():
                        if val2 is not None:
                            limitsAvailable = True
                            break
                if limitsAvailable:
                    textLimits = "("
                    first = True
                    for key2, val2 in limits.items():
                        if val2 is None: continue
                        if not first:
                            textLimits += ","
                        textLimits += key2
                        textLimits += "="
                        textLimits += str(val2)
                        first = False
                    textLimits += ")"
                    varField.labelLimit = Label(self.labelFrame,text=textLimits)
                else:
                    varField.labelLimit = Label(self._frame, text="")

                if key.endswith("Path"):
                    # create path buttons
                    varField.buttonOpenDir = Button(self.labelFrame, text="Dir", command=varField.OnOpenDir)
                    varField.buttonOpenFile = Button(self.labelFrame, text="File", command=varField.OnOpenFile)

            for i in range(len(self.variableFields)):
                self.variableFields[i].labelKey.grid(column=0,row=i)
                self.variableFields[i].entryValue.grid(column=1, row=i)
                self.variableFields[i].buttonSave.grid(column=2, row=i)
                self.variableFields[i].labelLimit.grid(column=3, row=i)
                self.variableFields[i].optionMenuValue.grid(column=4, row=i)
                if self.variableFields[i].buttonOpenDir:
                    self.variableFields[i].buttonOpenDir.grid(column=5, row=i)
                if self.variableFields[i].buttonOpenFile:
                    self.variableFields[i].buttonOpenFile.grid(column=6, row=i)

