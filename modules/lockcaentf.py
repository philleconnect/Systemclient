#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - CAEntf lock unit
# © 2019 Johannes Kreutz.

# Include dependencies
import winreg

# Class definition
class lockcaentf():
    systemPoliciesPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    explorerPoliciesPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"

    # Initialization
    def __init__(self):
        return

    # Registry setter
    def __setRegValues(self, value):
        try:
            systemPolicies = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.systemPoliciesPath, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(systemPolicies, "DisableLockWorkstation", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(systemPolicies, "HideFastUserSwitching", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(systemPolicies, "DisableChangePassword", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(systemPolicies, "DisableTaskMgr", 0, winreg.REG_DWORD, value)
            winreg.CloseKey(systemPolicies)
            explorerPolicies = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.explorerPoliciesPath, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(explorerPolicies, "NoLogoff", 0, winreg.REG_DWORD, value)
            winreg.CloseKey(explorerPolicies)
            return True
        except WindowsError:
            print("Failed to lock caentf.")
            return False

    # Enable caentf lock
    def enable(self):
        return self.__setRegValues(1)

    # Disable caentf lock
    def disable(self):
        return self.__setRegValues(0)
