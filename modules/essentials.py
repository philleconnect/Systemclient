#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - essential functions
# © 2019 Johannes Kreutz.

# Include dependencies
import random
import string
import platform
import socket
from subprocess import Popen, PIPE

# Class definition
class essentials:
    # Returns a random string with the given length
    @staticmethod
    def randomString(length):
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for i in range(length))

    # Operating system running on - returns "win" for windows and "linux" for linux systems
    @staticmethod
    def getOS():
        os = platform.system()
        if os == "Linux":
            return "linux"
        elif os == "Windows":
            return "win"
        else:
            return "unknown"

    # Returns the mac adress of the first ethernet card of the system
    @staticmethod
    def getMac():
        getmac = Popen(["cmd.exe", "/C getmac -fo csv"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        getmac.wait()
        lineCount= 0
        out = ""
        for line in iter(getmac.stdout.readline, ""):
            if lineCount == 1:
                out = line.strip().decode("utf-8")
                break
            lineCount += 1
        return out.split(",")[0].replace("-", ":").replace("\"", "")

    # Returns the local IPv4 adress of this system
    @staticmethod
    def getIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1)) # doesn't even have to be reachable
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    # Checks if given string is a valid ipv4 address
    @staticmethod
    def isIpv4(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False
        return True
