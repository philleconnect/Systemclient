#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - keyboard hook worker
# © 2019 Johannes Kreutz.

# Include dependencies
from ctypes import WinDLL, CFUNCTYPE, POINTER, c_int, c_uint, Structure
from ctypes.wintypes import DWORD, BOOL, HHOOK, LPCWSTR, WPARAM, LPARAM, HMODULE, LPMSG, HINSTANCE, HWND
import atexit
import threading

# C-Type definitions
ULONG_PTR = POINTER(DWORD)

# Hook event data type
class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vk_code", DWORD),
        ("scan_code", DWORD),
        ("flags", DWORD),
        ("time", c_int),
        ("dwExtraInfo", ULONG_PTR)
    ]

# Constants
NULL = DWORD(0)
WH_KEYBOARD_LL = c_int(13)
ALTKEY = 32
CTRLKEY = 0
WINKEYHELPER = 1
VK_F4 = 0x73
VK_ESCAPE = 0x1B
VK_LWIN = 0x5B
VK_RWIN = 0x5C

# Use Win32 system DLLs
kernel32 = WinDLL('kernel32', use_last_error=True)
user32 = WinDLL('user32', use_last_error = True)

# C-Type functions
LowLevelKeyboardProc = CFUNCTYPE(c_int, WPARAM, LPARAM, POINTER(KBDLLHOOKSTRUCT))

SetWindowsHookEx = user32.SetWindowsHookExW
SetWindowsHookEx.argtypes = [c_int, LowLevelKeyboardProc, HINSTANCE , DWORD]
SetWindowsHookEx.restype = HHOOK

GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.restype = HMODULE
GetModuleHandleW.argtypes = [LPCWSTR]

CallNextHookEx = user32.CallNextHookEx
CallNextHookEx.restype = c_int

UnhookWindowsHookEx = user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = [HHOOK]
UnhookWindowsHookEx.restype = BOOL

GetMessage = user32.GetMessageW
GetMessage.argtypes = [LPMSG, HWND, c_uint, c_uint]
GetMessage.restype = BOOL

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = [LPMSG]
TranslateMessage.restype = BOOL

DispatchMessage = user32.DispatchMessageA
DispatchMessage.argtypes = [LPMSG]

# Class definition
class keyboardHook(threading.Thread):
    # Initialization
    def __init__(self):
        threading.Thread.__init__(self)

    # Thread runner
    def run(self):
        # Set lock state and strict mode to disabled
        self.__locked = False
        self.__strictMode = False
        # Hook up keyup and keydown events
        keyboardCallback = LowLevelKeyboardProc(self.__llHandle)
        handle = GetModuleHandleW(None)
        self.__hookId = SetWindowsHookEx(WH_KEYBOARD_LL, keyboardCallback, handle, NULL)
        # Automatically remove the hook when python interpreter exits
        atexit.register(UnhookWindowsHookEx, self.__hookId)
        # React to system messages
        msg = LPMSG()
        while not GetMessage(msg, 0, 0, 0):
            TranslateMessage(msg)
            DispatchMessage(msg)


    # Low level Handler
    def __llHandle(self, nCode, wParam, lParam):
        #event = KeyboardEvent(event_types[wParam], lParam[0], lParam[1], lParam[2] == 32, lParam[3])
        # Call next hook if lock is disabled
        if self.__locked:
            if self.__strictMode:
                return 1
            else:
                if lParam.contents.vk_code == VK_F4 and lParam.contents.flags == ALTKEY: # Alt + F4
                    return 1
                elif lParam.contents.vk_code == VK_ESCAPE and lParam.contents.flags == ALTKEY: # Alt + Esc
                    return 1
                elif lParam.contents.vk_code == VK_ESCAPE and lParam.contents.flags == CTRLKEY: # Ctrl + Esc
                    return 1
                elif lParam.contents.vk_code == VK_LWIN and lParam.contents.flags == WINKEYHELPER: # WinL
                    return 1
                elif lParam.contents.vk_code == VK_RWIN and lParam.contents.flags == WINKEYHELPER: # WinR
                    return 1
                elif lParam.contents.flags == ALTKEY: # Alt
                    return 1
                else:
                    return CallNextHookEx(None, nCode, wParam, lParam)
        else:
            return CallNextHookEx(None, nCode, wParam, lParam)

    # Lock
    def lock(self):
        self.__locked = True

    # Unlock
    def unlock(self):
        self.__locked = False

    # Enable strict mode
    def enableStrict(self):
        self.__strictMode = True

    # Disable strict mode
    def disableStrict(self):
        self.__strictMode = False
