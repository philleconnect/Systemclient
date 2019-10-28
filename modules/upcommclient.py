#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - User mode process communication client
# © 2019 Johannes Kreutz.

# Include dependencies
import time
import subprocess
from multiprocessing.connection import Client
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, QMetaObject

# Include modules
import modules.hooks as hook
import modules.vncserver as vnc
import modules.screenshot as sc

# Cöass definition
class upcommclient(QRunnable):
    # Initialization
    def __init__(self, ui):
        self.__ui = ui
        self.__vnc = None
        self.__hook = hook.hooks()
        self.__connection = None
        self.__hookProcess = None
        self.__isConnected = False
        QRunnable.__init__(self)

    # Thread worker
    def run(self):
        while True:
            try:
                self.__connection = Client(("localhost", 34568), authkey=b"SECRET_REPLACE_ON_COMPILE")
                self.__isConnected = True
                while True:
                    message = self.__connection.recv()
                    if message == "LOCK":
                        self.__hook.controlKeyboard(True)
                        self.__hook.controlMouse(True)
                        QMetaObject.invokeMethod(self.__ui, "showGui", Qt.QueuedConnection)
                        time.sleep(1)
                        QMetaObject.invokeMethod(self.__ui, "focus", Qt.QueuedConnection)
                        self.__connection.send("SUCCESS")
                    elif message == "UNLOCK":
                        self.__hook.controlKeyboard(False)
                        self.__hook.controlMouse(False)
                        QMetaObject.invokeMethod(self.__ui, "hideGui", Qt.QueuedConnection)
                        self.__connection.send("SUCCESS")
                    elif message == "SCREENSHOT":
                        self.__connection.send(sc.screenshot.create())
                    elif message == "STOPCONTROL":
                        self.__vnc.stop()
                        self.__vnc = None
                        self.__connection.send("SUCCESS")
                    elif message == "CONTROL":
                        self.__vnc = vnc.vncserver()
                        self.__vnc.start()
                        self.__connection.send("SUCCESS")
                    else:
                        self.__connection.send("ERROR")
            except (ConnectionRefusedError, ConnectionResetError) as error:
                time.sleep(0.5)
                continue
