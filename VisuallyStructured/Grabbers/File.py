from Variables import Var
from Variables import PathVar
from Variables import ImageVar
from FlowBlocks import FlowBlockGrabber
from FlowBlocks import FlowBlockFactory
import os
import cv2
import logging

class FileGrabber(FlowBlockGrabber):
    def __init__(self,name="File"):
        super().__init__(name=name)
        self.SubVariables = {"Dir_or_File": PathVar()}

        self.__previousPath = None
        self.__previousFileName = None
        self.__fileNameList = []
        self.__validExtensions = (".jpg",".bmp",".png")
        self.__listCnt = -1

    @property
    def DirOrFile(self):
        return self.SubVariables["Dir_or_File"].value

    @DirOrFile.setter
    def DirOrFile(self, DirOrFile):
        self.SubVariables["Dir_or_File"].value = DirOrFile

    def __checkExtension(self,filename):
        if (filename.endswith(self.__validExtensions)):
            return True
        return False

    def __gatherFileNameList(self, path):
        if os.path.isfile(path) and self.__checkExtension(path):
            self.__fileNameList = [path]
        if os.path.isdir(path):
            files = os.listdir(path)
            selectedFiles = []
            for file in files:
                filename = path+"\\"+file
                if self.__checkExtension(filename):
                    selectedFiles.append(filename)
            self.__fileNameList = selectedFiles

    def __getNextFileName(self):
        if (len(self.__fileNameList)):
            self.__listCnt += 1
            if self.__listCnt >= len(self.__fileNameList):
                self.__listCnt = 0

            logging.info("Grabbed image %d of %d; %s" %(self.__listCnt, len(self.__fileNameList), self.__fileNameList[self.__listCnt]))
            return self.__fileNameList[self.__listCnt]
        else:
            logging.warning("Could not grab image; no (valid) files are specified.")

    def Execute(self):
        logging.info("Executing File Grabber")
        path = self.SubVariables["Dir_or_File"].value
        if path is None:
            return
        if self.__previousPath is not path:
            self.__listCnt = -1
            self.__gatherFileNameList(path)
            self.__previousPath = path

        filename = self.__getNextFileName()
        if os.path.isfile(filename):
            if self.__previousFileName is not filename:
                self.__previousFileName = filename
                image  = cv2.imread(filename)
                if image.shape[0] > 0 and image.shape[1] > 0:
                    self.OutputVars["Image"].value = image
                else:
                    logging.warning("The image your are trying to load has a size of 0.")

FlowBlockFactory.AddBlockType(FileGrabber)