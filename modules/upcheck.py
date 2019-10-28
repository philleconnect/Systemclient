#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - ping
# © 2019 Johannes Kreutz.

# Include dependencies
from ping3 import ping

# Class definition
class upcheck:
    # Ping host
    @staticmethod
    def ping(host):
        return ping(host)
