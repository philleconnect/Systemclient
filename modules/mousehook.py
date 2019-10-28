#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - mouse hook worker
# © 2019 Johannes Kreutz.

# Include dependencies
from ctypes import WinDLL, CFUNCTYPE, POINTER, c_int, c_int32, c_long, Structure
from ctypes.wintypes import DWORD, BOOL, HHOOK, WPARAM, LPARAM, LPMSG
import atexit
import threading

# Hook event data type
class MSLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("x", c_long),
        ("y", c_long),
        ('data', c_int32),
        ('reserved', c_int32),
        ("flags", DWORD),
        ("time", c_int),
    ]

# Constants
NULL = c_int(0)
WH_MOUSE_LL = c_int(14)

# Use Win32 system DLLs
kernel32 = WinDLL('kernel32', use_last_error=True)
user32 = WinDLL('user32', use_last_error = True)

# C-Type functions
SetWindowsHookEx = user32.SetWindowsHookExA
SetWindowsHookEx.restype = HHOOK

CallNextHookEx = user32.CallNextHookEx
CallNextHookEx.restype = c_int

UnhookWindowsHookEx = user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = [HHOOK]
UnhookWindowsHookEx.restype = BOOL

GetMessage = user32.GetMessageW
GetMessage.argtypes = [LPMSG, c_int, c_int, c_int]
GetMessage.restype = BOOL

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = [LPMSG]
TranslateMessage.restype = BOOL

DispatchMessage = user32.DispatchMessageA
DispatchMessage.argtypes = [LPMSG]

LowLevelMouseProc = CFUNCTYPE(c_int, WPARAM, LPARAM, POINTER(MSLLHOOKSTRUCT))

# Class definition
class mouseHook(threading.Thread):
    # Initialization
    def __init__(self):
        threading.Thread.__init__(self)

    # Thread runner
    def run(self):
        # Set lock state and strict mode to disabled
        self.__locked = False
        # Hook up mouse events
        mouseCallback = LowLevelMouseProc(self.__llHandle)
        self.__hookId = SetWindowsHookEx(WH_MOUSE_LL, mouseCallback, NULL, NULL)
        # Automatically remove the hook when python interpreter exits
        atexit.register(UnhookWindowsHookEx, self.__hookId)
        # React to system messages
        msg = LPMSG()
        while not GetMessage(msg, NULL, NULL, NULL):
            TranslateMessage(msg)
            DispatchMessage(msg)

    # Low level Handler
    def __llHandle(self, nCode, wParam, lParam):
        # Call next hook if lock is disabled
        if self.__locked:
            return 1
        else:
            return CallNextHookEx(NULL, nCode, wParam, lParam)

    # Lock
    def lock(self):
        self.__locked = True

    # Unlock
    def unlock(self):
        self.__locked = False
