import logging
from GUI.GUIInterface import *
from FlowBlocks import FlowBlock
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
            newvalue = self.parent.block.set_variable_value_by_id(self.id, value=value)
            self.entryValueStringVar.set(newvalue)
            self.parent.parent.controller.flow.set_variable_value_by_id(self.id, value=newvalue)

        def OnExternalValueChange(self,value=None):
            print(self.optionMenuStringVar.get())

        def OnOpenDir(self):
            directory = filedialog.askdirectory()
            self.entryValueStringVar.set(directory)


        def OnOpenFile(self):
            filename = filedialog.askopenfilename(title="Select File", filetypes=(("image files","*.jpg, *.bmp, *.png"),("all files","*.*")))
            self.entryValueStringVar.set(filename)

        def destroy_all(self):
            if self.labelLimit:
                self.labelLimit.destroy()
            if self.entryValue:
                self.entryValue.destroy()
            if self.optionMenuValue:
                self.optionMenuValue.destroy()
            if self.labelKey:
                self.labelKey.destroy()
            if self.buttonOpenDir:
                self.buttonOpenDir.destroy()
            if self.buttonOpenFile:
                self.buttonOpenFile.destroy()

        def add_all_to_grid(self, row: int):
            if self.labelKey:
                self.labelKey.grid(column=0, row=row)
            if self.entryValue:
                self.entryValue.grid(column=1, row=row)
            if self.buttonSave:
                self.buttonSave.grid(column=2, row=row)
            if self.labelLimit:
                self.labelLimit.grid(column=3, row=row)
            if self.optionMenuValue:
                self.optionMenuValue.grid(column=4, row=row)
            if self.buttonOpenDir:
                self.buttonOpenDir.grid(column=5, row=row)
            if self.buttonOpenFile:
                self.buttonOpenFile.grid(column=6, row=row)

    def __init__(self, parent, col=0, row=0, columnspan=1):
        super().__init__(parent, col=col, row=row, scrollbars=True, columnspan=columnspan,sticky=NSEW)
        self.parent = parent
        self.SetHeight(300)
        self._frame
        self.block = None
        self.labelFrameInput = None
        self.labelFrameOutput = None

        self.variable_fields_in = []
        self.variable_fields_out = []

    def load_properties(self, block: FlowBlock):
        """
        Shows the input variables for the block that has been provided.
        :param block: block for which to load the values
        :return:
        """
        logging.info("Loading properties for %s" %block.name)
        self.block = block

        #destroy old stuff
        for variableField in self.variable_fields_in:
            variableField.destroy_all()
        # clean old variable list
        self.variable_fields_in = []

        if self.labelFrameInput:
            self.labelFrameInput.destroy()

        var_ids_in = block.GetVariableIDs()
        if len(var_ids_in) > 0:
            # there are variables available for this block
            #first show name
            self.labelFrameInput = LabelFrame(self._frame, text=block.name + ": Inputs")
            self.labelFrameInput.grid( row=0, column=0)

            #index = -1
            for key, val in var_ids_in.items():
                varField = ViewProperties.VariableField(key, val, self)
                self.variable_fields_in.append(varField)

                varField.labelKey = Label(self.labelFrameInput, text=key)
                #self.entryvalues.append(Entry(self.labelFrameInput, textvalue=str(val), command=self.__onValueChange))
                varField.entryValueStringVar = StringVar(self.labelFrameInput)
                varField.entryValueStringVar.set(str(val))
                varField.entryValue = Entry(self.labelFrameInput, textvariable=varField.entryValueStringVar)
                varField.buttonSave = Button(self.labelFrameInput, text="Save", command=varField.OnValueSave)

                #self.parent.controller.set_variable_value_by_id()
                #self.parent.controller.ge
                varField.optionMenuOptions = ["egg","bunny","chicken"]

                #self.externalvalues.append(OptionMenu(self.labelFrameInput, "", *options, command=lambda index=index: self.__onExternalValueChange))
                varField.optionMenuStringVar = StringVar(self.labelFrameInput)
                varField.optionMenuStringVar.set("")
                varField.optionMenuValue = OptionMenu(self.labelFrameInput, varField.optionMenuStringVar, *varField.optionMenuOptions, command=varField.OnExternalValueChange)

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
                    varField.labelLimit = Label(self.labelFrameInput, text=textLimits)
                else:
                    varField.labelLimit = Label(self._frame, text="")

                if key.endswith("Path"):
                    # create path buttons
                    varField.buttonOpenDir = Button(self.labelFrameInput, text="Dir", command=varField.OnOpenDir)
                    varField.buttonOpenFile = Button(self.labelFrameInput, text="File", command=varField.OnOpenFile)

            for i,field in enumerate(self.variable_fields_in):
                field.add_all_to_grid(i)

        #destroy old stuff
        for variableField in self.variable_fields_out:
            variableField.destroy_all()
        # clean old variable list
        self.variable_fields_out = []

        if self.labelFrameOutput:
            self.labelFrameOutput.destroy()

        #get results, if available, for this block
        results = self.parent.controller.results.GetResults(block)

        if not results == None and len(results) > 0:
            # there are results to display
            self.labelFrameOutput = LabelFrame(self._frame, text=block.name + ": Outputs")
            self.labelFrameOutput.grid(row=0, column=1)
            for key, val in results.items():
                varField = ViewProperties.VariableField(key, val, self)
                self.variable_fields_out.append(varField)
                varField.labelKey = Label(self.labelFrameOutput, text=key)

            for i,field in enumerate(self.variable_fields_out):
                field.add_all_to_grid(i)

        # var_ids_out = []
        # if block.OutputVars:
        #     var_ids_out = block.OutputVars.GetVariableIDs()
        #
        # if len(var_ids_out) > 0:
        #     #there are some output variables available
        #     self.labelFrameOutput = LabelFrame(self._frame, text=block.name)
        #     self.labelFrameOutput.grid(sticky=NSEW)