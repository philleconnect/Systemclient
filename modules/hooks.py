#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - mouse and keyboard hooks
# © 2019 Johannes Kreutz.

# Include dependencies
import threading

# Include modules
import modules.keyboardhook as kh
import modules.mousehook as mh

# Class definition
class hooks:
    # Initialization
    def __init__(self):
        self.__keyThread = kh.keyboardHook()
        self.__keyThread.daemon = True
        self.__keyThread.start()
        self.__mouseThread = mh.mouseHook()
        self.__mouseThread.daemon = True
        self.__mouseThread.start()
        self.__keyThread.enableStrict()

    # CONTROL FUNCTIONS
    # Control keyboard hook
    def controlKeyboard(self, mode):
        if mode:
            self.__keyThread.lock()
        else:
            self.__keyThread.unlock()

    # Control mouse hook
    def controlMouse(self, mode):
        if mode:
            self.__mouseThread.lock()
        else:
            self.__mouseThread.unlock()
