#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - SMB windows workaround worker
# © 2019 Johannes Kreutz.

# Include dependencies
import socket
import os

# Include modules
import modules.essentials as ess

# Class definition
class smbfixup:
    # Execute SMB fixup
    @staticmethod
    def fixHostsFile(smbserver):
        if ess.essentials.getOS() == "win":
            ip = None
            if ess.essentials.isIpv4(smbserver):
                ip = smbserver
            else:
                ip = socket.gethostbyname(smbserver)
            files = ["C:\\Windows\\System32\\drivers\\etc\\hosts", "C:\\Windows\\System32\\drivers\\etc\\lmhosts"]
            for file in files:
                if os.path.exists(file):
                    a = False
                    b = False
                    c = False
                    d = False
                    with open(file, "r") as f:
                        lines = f.readlines()
                    for i in range(len(lines)):
                        if not "#" in lines[i]:
                            if "driveone.this" in lines[i]:
                                a = True
                                if not ip in lines[i]:
                                    lines[i] = ip + " driveone.this\n"
                            elif "drivetwo.this" in lines[i]:
                                b = True
                                if not ip in lines[i]:
                                    lines[i] = ip + " drivetwo.this\n"
                            elif "drivethree.this" in lines[i]:
                                c = True
                                if not ip in lines[i]:
                                    lines[i] = ip + " drivethree.this\n"
                            elif "groupfolders.this" in lines[i]:
                                d = True
                                if not ip in lines[i]:
                                    lines[i] = ip + " groupfolders.this\n"
                    if not a:
                        lines.append(ip + " driveone.this\n")
                    if not b:
                        lines.append(ip + " drivetwo.this\n")
                    if not c:
                        lines.append(ip + " drivethree.this\n")
                    if not d:
                        lines.append(ip + " groupfolders.this\n")
                    with open(file, "w") as f:
                        for line in lines:
                            f.write(line)
