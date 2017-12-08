import shutil
import os
import logging
from FlowBlocks import *

class Subject(object):
    """One part of de observer pattern. Use Attach() and Detach() to subscribe for updates"""
    def __init__(self):
        self._observers = []

    def Attach(self, observer):
        self._observers.append(observer)
        self.__notify()

    def Detach(self, observer):
        self._observers.remove(observer)

    def __notify(self):
        for observer in self._observers:
            observer.Update()

class Observer(object):
    def Update(self):
        raise NotImplementedError