#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - VNC-Server password setter
# © 2019 Johannes Kreutz.

# Include dependencies
import threading
from subprocess import Popen, PIPE

# Class definition
class vncpasswd:
    @staticmethod
    def setPasswd(password):
        p = Popen(["C:\\Program Files\\PhilleConnect\\vnc\\winvncstartup.exe", password, password], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.wait()
