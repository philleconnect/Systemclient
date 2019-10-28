#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - main
# © 2019 Johannes Kreutz.

# Include dependencies
import sys
import os
import time
import ctypes
from flask import Flask, request
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThreadPool

# Include modules
import modules.configreader as config
import modules.lockscreen as lock
import modules.essentials as ess
import modules.lockcaentf as lockcaentf
import modules.lockaccessibility as accessibility
import modules.upcommserver as upcommserver
import modules.upcommclient as upcommclient
import modules.smbfixup as smbfixup
import modules.watchdog as wd
import modules.shutdown as sd
import modules.request as rq
import modules.vncpasswd as vcpw

# Startup modes
if len(sys.argv) > 1:
    if len(sys.argv) == 2:
        watchdog = wd.watchdog(2, sys.argv[1])
    else:
        print("Wrong parameters. Aborting.")
        sys.exit()
elif len(sys.argv) == 1:
    watchdog = wd.watchdog(1)

# Check for admin rights
try:
    isAdmin = os.getuid() == 0
except AttributeError:
    isAdmin = ctypes.windll.shell32.IsUserAnAdmin() != 0

# Manager objects
config = config.reader()

# Main instance running in admin context
if isAdmin:
    caentf = lockcaentf.lockcaentf()
    acc = accessibility.lockaccessibility()

    # Apply windows SMB workaround
    smbfixup.smbfixup.fixHostsFile(config.get("smbserver"))
    # Stop process on teacher machines as everything is done here
    if config.get("isteachermachine") == "1":
        sys.exit()

    # Start watchdog
    watchdog.start()

    # Global status variables (why so complicated, you might think? wasn't able to get the easy way working...)
    class lockstate:
        def __init__(self):
            self.__ls = False
        def set(self, mode):
            self.__ls = mode
        def get(self):
            return self.__ls

    ls = lockstate()

    # User context events
    ups = upcommserver.upcommserver()
    ups.start()

    # Flask server definition (legacy mode)
    legacy = Flask(__name__)

    # LEGACY API ENDPOINTS
    @legacy.route("/online", methods = ["GET", "POST"])
    def onlineAnswer():
        if ups.isConnected():
            return "online"
        return "semi"

    @legacy.route("/lockstate", methods = ["GET", "POST"])
    def lockstateAnswer():
        if ls.get():
            return "locked"
        else:
            return "unlocked"

    @legacy.route("/<room>/<machine>/<command>", methods = ["GET", "POST"])
    def handleCommand(room, machine, command):
        if room == config.get("room") and machine == config.get("machinename"):
            permissioncheck = rq.request(config.get("server"), {"usage": "checkteacher", "globalpw": config.get("global"), "req": request.remote_addr}, False)
            result = permissioncheck.post()
            if result == "success":
                if command == "lock":
                    if ups.send("LOCK") == "SUCCESS":
                        caentf.enable()
                        acc.enable()
                        ls.set(True)
                        return "locked"
                    else:
                        return "error"
                elif command == "unlock":
                    if ups.send("UNLOCK") == "SUCCESS":
                        caentf.disable()
                        acc.disable()
                        ls.set(False)
                        return "unlocked"
                    else:
                        return "error"
                elif command == "shutdown":
                    sd.shutdown.now()
                    return "shutdown"
                elif command == "screenshot":
                    return ups.send("SCREENSHOT")
                elif command == "requestcontrol":
                    password = ess.essentials.randomString(8)
                    vcpw.vncpasswd.setPasswd(password)
                    if ups.send("CONTROL") == "SUCCESS":
                        return password
                    else:
                        return "error"
                elif command == "cancelcontrol":
                    if ups.send("STOPCONTROL") == "SUCCESS":
                        return "success"
                    else:
                        return "error"
                else:
                    return "Bad command."
            else:
                return "unauthorized."
        else:
            return "Bad request."

    # Create server
    if __name__ == "__main__":
        legacy.run(debug=False, host="0.0.0.0", port=34567, threaded=True)

# Worker client running in user context
else:
    # Stop process on teacher machines as everything is done here
    if config.get("isteachermachine") == "1":
        sys.exit()

    # Start watchdog
    watchdog.start()

    # GUI and communication configuration
    app = QApplication(sys.argv) # Create QApplication object
    window = lock.lockscreen() # Create window
    threadpool = QThreadPool() # Create thread pool
    upc = upcommclient.upcommclient(window) # Create communication thread
    threadpool.start(upc) # Add worker thread to thread pool
    sys.exit(app.exec_())
