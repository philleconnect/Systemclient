#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - lockscreen accessibility button lock unit
# © 2019 Johannes Kreutz.

# Include dependencies
from subprocess import Popen, PIPE

# Class definition
class lockaccessibility():
    utilmanPath = "C:\\Windows\\System32\\Utilman.exe"

    # Initialization
    def __init__(self):
        takeOwnProcess = Popen(["cmd.exe", "/C takeown /F " + self.utilmanPath], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        takeOwnProcess.wait()
        return

    # Registry setter
    def __setExecutionPermissions(self, mode):
        command = "/grant"
        if mode > 0:
            command = "/deny"
        executionUsers = ["Administratoren", "Benutzer"]
        for user in executionUsers:
            setProcess = Popen(["cmd.exe", "/C icacls " + self.utilmanPath + " " + command + " " + user + ":RX"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            setProcess.wait()

    # Enable caentf lock
    def enable(self):
        return self.__setExecutionPermissions(1)

    # Disable caentf lock
    def disable(self):
        return self.__setExecutionPermissions(0)
