#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - server request
# © 2019 Johannes Kreutz.

# Include dependencies
import urllib3
import requests
import sys

# Include modules
import modules.essentials as ess

# Class definition
class request:
    # Initialization
    def __init__(self, url, params, verify):
        urllib3.disable_warnings()
        self.__url = "https://" + url + "/client.php"
        self.__params = params
        self.__verify = verify
        essentialParams = {"machine": ess.essentials.getMac(), "ip": ess.essentials.getIp(), "os": ess.essentials.getOS()}
        self.__params.update(essentialParams)

    # Run post request
    def post(self):
        response = requests.post(self.__url, data = self.__params, verify = self.__verify).text
        if response == "!":
            print("Konfigurationsfehler. Programm wird beendet.")
            sys.exit()
        elif response == "nomachine":
            print("Rechner nicht registriert. Programm wird beendet.")
            sys.exit()
        elif not response == "":
            return response
        else:
            print("Keine Verbindung zum Server. Programm wird beendet.")
            sys.exit()
