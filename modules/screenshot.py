#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - screenshot creator
# © 2019 Johannes Kreutz.

# Include dependencies
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QBuffer, QByteArray, QIODevice

# Class definition
class screenshot:
    # Create screenshot and return jpeg stream
    @staticmethod
    def create():
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, 0, 0, -1, -1)
        # Save QPixmap
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.WriteOnly)
        screenshot.save(buffer, "JPG", 10)
        return byteArray.toBase64().data().decode("utf-8")
