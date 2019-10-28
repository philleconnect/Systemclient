#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - process watchdog
# © 2019 Johannes Kreutz.

# Include dependencies
import psutil
import os
import threading
import time
import subprocess

# Class definition
class watchdog(threading.Thread):
    # Initialization
    def __init__(self, mode, pid = -1):
        self.__executable = ""
        self.__pid = int(pid)
        if mode == 1 or mode == 2: # I am systemclient. Keep watchdog running.
            self.__executable = "C:\\Program Files\\PhilleConnect\\dkmp.exe"
        elif mode == 3: # I am watchdog. Keep systemclient running.
            self.__executable = "C:\\Program Files\\PhilleConnect\\systemclient.exe"
        threading.Thread.__init__(self)

    # Thread runner
    def run(self):
        while True:
            if self.__pid < 0 or not psutil.pid_exists(self.__pid):
                self.__pid = self.__startDetached()
            time.sleep(0.1)

    # Start process as detached child
    def __startDetached(self):
        flags = 0
        flags |= 0x00000008  # DETACHED_PROCESS
        flags |= 0x00000200  # CREATE_NEW_PROCESS_GROUP
        flags |= 0x08000000  # CREATE_NO_WINDOW

        pkwargs = {
            #'close_fds': True,  # close stdin/stdout/stderr on child
            'creationflags': flags,
        }

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        p = subprocess.Popen([self.__executable, str(os.getpid())], **pkwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo, close_fds=True)

        # p is the cleanup process, but we need the pid of the python process, which has p's id as parent
        # Do this until we find the process (assuming it's not up immediately)
        while True:
            for proc in psutil.process_iter():
                if proc.ppid() == p.pid:
                    return proc.pid
