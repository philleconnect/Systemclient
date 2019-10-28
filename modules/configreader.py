#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - configuration file reader
# © 2019 Johannes Kreutz.

# Include dependencies
import json
import time
import sys

# Include modules
import modules.request as request
import modules.upcheck as up

# Class definition
class reader:
    # Initialization
    def __init__(self):
        self.__variables = {}
        self.__readLocalConfig()
        self.__connectionTry = 0
        self.__connected = False
        self.__pingDest = self.get("server").split(":", 1)[0] if ":" in self.get("server") else self.get("server")
        while self.__connectionTry < int(self.get("badNetworkReconnect")) and not self.__connected:
            self.__connected = True if not up.upcheck.ping(self.__pingDest) == None else False
            self.__connectionTry += 1
        if self.__connectionTry >= int(self.get("badNetworkReconnect")):
            sys.exit()
        self.__readServerConfig()

    # Read local config file
    def __readLocalConfig(self):
        with open("C:\\Program Files\\PhilleConnect\\pcconfig.jkm", "r") as f:
            for line in f:
                if not line.startswith("#") and "=" in line:
                    element = line.split("=", 1)
                    self.__variables[element[0].strip()] = element[1].strip()

    # Read server config
    def __readServerConfig(self):
        params = {"usage": "config", "globalpw": self.__variables["global"]}
        getter = request.request(self.__variables["server"], params, False)
        serverconfig = json.loads(getter.post())
        for element in serverconfig.values():
            self.__variables[element[0].strip()] = element[1].strip()

    # Get config parameter
    def get(self, name):
        return self.__variables[name]
