#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - User mode process communication manager
# © 2019 Johannes Kreutz.

# Include dependencies
import threading
import time
from multiprocessing.connection import Listener

# Class definition
class upcommserver(threading.Thread):
    # Initialization
    def __init__(self):
        self.__listener = Listener(("localhost", 34568), authkey=b"SECRET_REPLACE_ON_COMPILE")
        self.__connection = None
        self.__isConnected = False
        self.__lastResponse = "__EMPTY"
        threading.Thread.__init__(self)

    # Thread runner (to allow reconnecting on close)
    def run(self):
        while True:
            try:
                self.__connection = self.__listener.accept()
                self.__isConnected = True
                while True:
                    self.__lastResponse = self.__connection.recv()
            except ConnectionResetError:
                self.__isConnected = False
                continue

    # Send to connection
    def send(self, message):
        if self.__isConnected:
            self.__connection.send(message)
            while self.__lastResponse == "__EMPTY":
                time.sleep(0.1)
            cache = self.__lastResponse
            self.__lastResponse = "__EMPTY"
            return cache

    # Check connection
    def isConnected(self):
        return self.__isConnected
