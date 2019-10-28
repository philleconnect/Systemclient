#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - VNC-Server
# © 2019 Johannes Kreutz.

# Include dependencies
import threading
import time
from subprocess import Popen, PIPE

# Class definition
class vncserver(threading.Thread):
    # Initialization
    def __init__(self):
        self.__shouldTerminate = False
        threading.Thread.__init__(self)

    # Thread runner
    def run(self):
        self.__process = Popen(["C:\\Program Files\\PhilleConnect\\vnc\\winvnc.exe"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        while not self.__shouldTerminate:
            time.sleep(0.1)
        self.__process.kill()

    # End vnc session
    def stop(self):
        self.__shouldTerminate = True
