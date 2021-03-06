import pickle
import os
import logging
#used for typing
from numpy import ndarray
import cv2

from Vision.helper_functions import get_inverted_color, enlarge_alpha_image


class Var(object):
    """
    Var object allow you to generate a structured text of the parameter including all sub-parameters that are nested in
    self.SubVariables.

    GetVariableIDs() gets an address like string for every parameter associated to this variable. Implement own
    GetVariableIDs() when type is a stub (i.e. does not have other SubVariables like float or int).

    It allows objects that inherit from Var to draw itself (implement when necessary).
    """

    def __init__(self, name):
        """
        Takes a name for your custom variable, and initializes the dictionary containing all sub variables.
        Optionally settings might be provided to create the subvariables with
        :param name: Name of variable
        """
        self.SubVariables = dict()  # contains all nested variables (e.g. a line can be constructed from
        self.__name = name
        self.Limits = None
        self.__delimiter = "."
        self.flowidreference = None
        self.is_reference = False

    def __del__(self):
        self.close()

    def __repr__(self):
        if self.stub:
            # is stub just return name and value 'name: value'
            if (type(self.value) == ndarray):
                if len(self.value.shape) == 3:
                    channels = self.value.shape[2]
                else:
                    channels = 1
                value = "width: %d, height: %d, channels: %d, type: %s" % (
                    self.value.shape[1],
                    self.value.shape[0],
                    channels,
                    str(self.value.dtype)
                )
            else:
                value = str(self.value)
            return ": " + value
        else:
            # if not stub then iterate over subvariable and print out like:
            # subvarname --> subsubvarname ..
            #            |-> subsubvarname ..
            first = True
            output = ""
            for key, value in self.SubVariables.items():
                if first:
                    first = False
                    insert = " --> " + key
                    output += insert + str(value)
                    output = output.replace("\n", "\n" + len(insert) * " ")

                else:
                    #
                    output += "\n"
                    output += " |-> " + key + str(value)
            return output



    def close(self):
        pass

    def is_flowblock(self):
        return False

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name


    def draw(self, image: ndarray, relative_size = 1, color = (255, 255, 255)) -> ndarray:
        for drawable in self.SubVariables:
            image = drawable.draw(image, relative_size, color)
        return image

    @property
    def value(self):
        raise ValueError("Cannot get value. Value getter and setter not implemented")

    @value.setter
    def value(self, value):
        raise ValueError("Cannot set value. Value getter and setter not implemented")

    def Print(self, level=0):
        """
        Gets a representation of all data needed for this object, and returns this as structured text
        :param level: determines the indentation level.
        :return: a string of structured text
        """
        tabs = ""
        for i in range(level): tabs += "\t"

        printout = ""
        for key, val in self.SubVariables.items():
            printout += "\n" + tabs + " (" + str(key) + ")"
            printout += val.Print(level=level + 1)
        return "\n" + tabs + self.name + printout

    def GetLimits(self, id):
        obj = self.get_variable_by_id(id)
        if obj is None:
            return None
        return obj.Limits

    def get_variable_ids(self, var_name=None):
        """
        Get the id of all variable. Do not use var_name, it is only used for recursion.
        :param var_name: Do not use.
        :return: variable id.
        """
        if self.Stub():
            raise NotImplementedError(
                "Stub variable types should implement their own GetVariableIDs(name) method. %s of type %s didn't." % (
                    self.name, str(type(self))))
        if var_name is None:
            var_name = self.name
        varids = dict()
        for key, val in self.SubVariables.items():
            subvarids = val.get_variable_ids(key)
            for keysub, valsub in subvarids.items():
                varids[var_name + self.__delimiter + keysub] = valsub
        return varids

    def set_variable_by_settings_dict(self, settings):
        """
        Saves settings typically coming from a yaml flow file to the subvariables of this specific block. It uses
        set_variable_value_by_id.
        :param settings: settings dict
        :return: None
        """

        def __set_var(self, settings: dict, accumulated_id: str):
            value = settings.get('value')
            is_reference = settings.get('is_reference')
            # check if this is a stub variable
            if 'value' in settings and is_reference is not None:  # value should exist but can be None
                self.set_variable_value_by_id(accumulated_id, value, is_reference)
            else:
                for key, value in settings.items():
                    accumulated_id_new = accumulated_id + '.' + key
                    __set_var(self, value, accumulated_id_new)

        for key, value in settings.items():
            __set_var(self, value, key)

    def set_variable_value_by_id(self, id: str, value, is_reference=False):
        """
        Sets a specific subvariable of this Var object. Id is in the form of:
        Blockname.Variablename.Variabletype.Variablename.VariableType...
        :param id: variable id to set
        :param value: value to set it to
        :param is_reference: is the value a reference to a result?
        :return: value it has been set to. It might change if the value does not adhere to the rules of that variable.
        """
        if self.stub:
            obj = self
        else:
            obj = self.get_variable_by_id(id)

        if obj is None:
            return None

        obj.is_reference = is_reference
        obj.value = value
        return obj.value

    def get_variable_by_id(self, id: str):
        splitted_id = id.split(self.__delimiter)[1:]
        if len(splitted_id) is 0:
            splitted_id = [id]
        obj = self
        for subid in splitted_id:
            if obj.Stub():
                break
            if obj.is_reference:
                break
            nextObj = obj.SubVariables.get(subid)
            if nextObj is None:
                return None
            else:
                obj = nextObj
        return obj

    def get_subvariable_or_referencedvariable(self, id: str, results_controller):
        """
        Gets the value of a subvariable. It might also get the value from the results model if the value is a reference
        to an output of a different block.
        :param id: id of the viable
        :param results_controller:  results controller. Needs this to retrieve the value in case of a output reference.
        :return: The value requested.
        """
        subvar = self.get_variable_by_id(self.name + self.__delimiter + id)
        if subvar is None:
            logging.warning("Subvariable %s does not exist in %s." % (id, self.name))
            return None

        try:
            is_reference = subvar.is_reference
        except:  # TODO: Somehow the is_reference property is not inherited.
            is_reference = False
            logging.warning("%s.is_reference property does not exist." % id)
        if is_reference:
            if results_controller is not None:
                subvar = results_controller.getvalue(subvar.value)

        return subvar

    def get_variables_by_type(self, type: str):
        """
        Gets all variables that are of the specified type. This is the type as specified in
        :param type:
        :return:
        """
        vars = dict()
        ids = self.get_variable_ids()
        for key, var in ids.items():
            if type in key:
                obj = self.get_variable_by_id(key.split("type")[0] + type)
                if not obj:
                    continue
                vars[key] = obj
        return vars

    def Stub(self):
        """
        If no sub variables are available it returns True.
        :return: is this a stub? as a bool
        """
        if (len(self.SubVariables)):
            return False
        elif self.is_flowblock():  # in case of a flowblock not having subvariables is not a sign of being a stub
            return False
        else:
            return True

    @property
    def stub(self):
        return self.Stub()


class StubVar(Var):
    def __init__(self, type, name, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.__type = type
        self.SubVariables = dict()

    def Print(self, level=0):
        tabs = ""
        for i in range(level): tabs += "\t"
        return "\n" + tabs + self.name + ": " + str(self.value)

    def get_variable_ids(self, name=None):
        if name:
            varids = {name + "." + self.__type: self.value}
        else:
            varids = {self.__type: self.value}
        return varids


class TextVar(StubVar):  # not stringvar because this has already been used by tkinter
    def __init__(self, stringvalue="", name="String"):
        super().__init__("String", name=name)
        self.value = stringvalue

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return self.__value

    @value.setter
    def value(self, value):
        self.flowidreference = None
        self.__value = value


class ImageVar(StubVar):
    def __init__(self, image=None, name="Image"):
        super().__init__("Image", name=name)
        self.value = image

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class BoolVar(StubVar):
    def __init__(self, boolvalue=False, name="Bool"):
        super().__init__(name, name=name)
        self.value = boolvalue

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return bool(self.__value)

    @value.setter
    def value(self, value):
        if self.is_reference:
            self.__value = value
            return
        if not isinstance(value, bool):
            if value == "True" or value == "true" or value == "1":
                value = True
            elif value == "False" or value == "false" or value == "0":
                value = False
            else:
                return  # not parsable, do not change a thing
        self.__value = value


class IntVar(StubVar):
    def __init__(self, intvalue=0, name="Int", min=None, max=None):
        super().__init__("Int", name=name)
        # self.SubVariables = dict()
        if min is not None and max is not None and max < min:
            temp = min
            min = max
            max = temp
        self.Limits = {"min": min, "max": max}
        self.value = intvalue

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return self.__value

    @value.setter
    def value(self, value):
        if not isinstance(value, int):
            value = int(value)
        self.flowidreference = None
        if self.Limits["min"] is not None and value < self.Limits["min"]:
            value = self.Limits["min"]
        if self.Limits["max"] is not None and value > self.Limits["max"]:
            value = self.Limits["max"]
        self.__value = value


class FloatVar(StubVar):
    def __init__(self, floatvalue=0.0, name="Float", min=None, max=None):
        super().__init__("Float", name=name)
        # self.SubVariables = dict()
        if min is not None and max is not None and max < min:
            temp = min
            min = max
            max = temp
        self.Limits = {"min": min, "max": max}
        self.value = floatvalue

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return self.__value

    @value.setter
    def value(self, value):
        if self.is_reference:
            self.__value = value
            return
        if not isinstance(value, float):
            value = float(value)
        self.flowidreference = None
        if self.Limits["min"] is not None and value < self.Limits["min"]:
            value = self.Limits["min"]
        if self.Limits["max"] is not None and value > self.Limits["max"]:
            value = self.Limits["max"]
        self.__value = value


class PathVar(StubVar):
    def __init__(self, path=None, name="Path"):
        super().__init__("Path", name=name)
        self.value = path

    @property
    def value(self):
        if self.flowidreference:
            return self.__value.__value
        return self.__value

    @value.setter
    def value(self, value):
        if self.is_reference:
            self.__value = value
            return
        if value is None:
            self.__value = None
            return
        self.flowidreference = None
        if not isinstance(value, str):
            value = str(value)

        if os.path.exists(value):
            self.__value = value
            return
        dir = os.path.dirname(value)
        if os.path.exists(dir):
            self.__value = value
        else:
            logging.warning("Path %s that was provided to the %s does not have a valid directory." % (self.name, value))


class IntPointVar(Var):
    def __init__(self, x=IntVar(), y=IntVar(), name="Point"):
        super().__init__(name)
        self.SubVariables = {"x": IntVar(), "y": IntVar()}
        self.x = x
        self.y = y

    @property
    def x(self):
        return self.SubVariables["x"]

    @x.setter
    def x(self, x):
        if not isinstance(x, IntVar):
            raise ValueError
        self.SubVariables["x"] = x

    @property
    def y(self):
        return self.SubVariables["y"]

    @y.setter
    def y(self, y):
        if not isinstance(y, IntVar):
            raise ValueError
        self.SubVariables["y"] = y


class PointVar(Var):
    def __init__(self, x=FloatVar(), y=FloatVar(), name="Point"):
        super().__init__(name)
        self.SubVariables = {"x": x, "y": y}

    @property
    def x(self):
        return self.SubVariables["x"]

    @x.setter
    def x(self, x):
        if not isinstance(x, FloatVar):
            raise ValueError
        self.SubVariables["x"] = x

    @property
    def y(self):
        return self.SubVariables["y"]

    @y.setter
    def y(self, y):
        if not isinstance(y, FloatVar):
            raise ValueError
        self.SubVariables["y"] = y

    def draw(self, image: ndarray, relative_size=1, color=(255,255,255,255)) -> ndarray:
        line_thickness_foreground = int(1 * relative_size)
        if line_thickness_foreground < 1: line_thickness_foreground = 1
        line_thickness_background = 3 * line_thickness_foreground

        width_needed = self.x.value + line_thickness_background + 2
        height_needed = self.y.value + line_thickness_background + 2
        image = enlarge_alpha_image(image, width_needed, height_needed)

        color_inv = get_inverted_color(color)

        cv2.circle(image, (int(self.x.value), int(self.y.value)), int(line_thickness_foreground), color_inv,
                   thickness=line_thickness_background)
        cv2.circle(image, (int(self.x.value), int(self.y.value)), int(line_thickness_foreground), color, thickness=line_thickness_foreground)

        return image


class LineVar(Var):
    def __init__(self, start=PointVar(), end=PointVar(), name="Line"):
        super().__init__(name)
        self.SubVariables = {"start": PointVar(), "end": PointVar()}
        self.start = start
        self.end = end

    @property
    def start(self) -> PointVar:
        return self.SubVariables["start"]

    @start.setter
    def start(self, start):
        if not isinstance(start, PointVar):
            raise ValueError
        self.SubVariables["start"] = start

    @property
    def end(self) -> PointVar:
        return self.SubVariables["end"]

    @end.setter
    def end(self, end):
        if not isinstance(end, PointVar):
            raise ValueError
        self.SubVariables["end"] = end

    def draw(self, image: ndarray, relative_size=1, color=(255,255,255,255)) -> ndarray:
        line_thickness_foreground = int(1 * relative_size)
        if line_thickness_foreground < 1: line_thickness_foreground = 1
        line_thickness_background = 3 * line_thickness_foreground

        width_needed = max(self.end.x.value, self.end.x.value) + line_thickness_background + 2
        height_needed = max(self.end.y.value, self.end.y.value) + line_thickness_background + 2
        image = enlarge_alpha_image(image, width_needed, height_needed)

        color_inv = get_inverted_color(color)

        cv2.line(image, (int(self.start.x.value), int(self.start.y.value)),
                 (int(self.end.x.value), int(self.end.y.value)), color_inv, thickness=line_thickness_background)
        cv2.line(image, (int(self.start.x.value), int(self.start.y.value)), (int(self.end.x.value), int(self.end.y.value)), color, thickness=line_thickness_foreground)

        return image

class CircleVar(Var):
    def __init__(self, center=PointVar(), radius=FloatVar(), name="Circle"):
        super().__init__(name)
        self.SubVariables = {"center": center, "radius": radius}

    @property
    def center(self):
        return self.SubVariables["center"]

    @center.setter
    def center(self, center):
        if not isinstance(center, PointVar):
            raise ValueError
        self.SubVariables["center"] = center

    @property
    def radius(self):
        return self.SubVariables["radius"]

    @radius.setter
    def radius(self, radius):
        if not isinstance(radius, IntVar):
            raise ValueError
        self.SubVariables["radius"] = radius

    def draw(self, image: ndarray, relative_size=1, color=(255,255,255,255)) -> ndarray:
        line_thickness_foreground = int(1 * relative_size)
        if line_thickness_foreground < 1: line_thickness_foreground = 1
        line_thickness_background = 3 * line_thickness_foreground

        width_needed = self.center.x.value + self.radius.value + line_thickness_background + 2
        height_needed = self.center.y.value + self.radius.value + line_thickness_background + 2
        image = enlarge_alpha_image(image, width_needed, height_needed)

        color_inv = get_inverted_color(color)

        cv2.circle(image, (int(self.center.x.value), int(self.center.y.value)), int(self.radius.value), color_inv,
                   thickness=line_thickness_background)
        cv2.circle(image, (int(self.center.x.value), int(self.center.y.value)), int(self.radius.value), color, thickness=line_thickness_foreground)

        image = self.center.draw(image, relative_size, color)

        return image

def main():
    line = LineVar(IntPointVar(FloatVar(1.0), FloatVar(1.0)), IntPointVar(FloatVar(2.0), FloatVar(2.0)))
    print(line.Print())

    # Pickle Serialization
    filename = "SavedFlows\\testSaveVariables.vsf"
    pickle.dump(line, open(filename, "wb"))

    unpickeldline = pickle.load(open(filename, "rb"))

    # Varid's
    varids = unpickeldline.get_variable_ids()
    print(varids)


if __name__ == "__main__":
    main()
