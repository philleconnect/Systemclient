#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - shutdown host
# © 2019 Johannes Kreutz.

# Include dependencies
from subprocess import Popen

# Class definition
class shutdown:
    @staticmethod
    def now():
        p = Popen(["cmd.exe", "/C", "shutdown", "/s", "/f", "/t", "0"])
