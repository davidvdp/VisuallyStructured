from GUI.GUIInterface import Observer
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
        self.Notify()

    def Detach(self, observer):
        self._observers.remove(observer)

    def Notify(self):
        for observer in self._observers:
            observer.Update()

