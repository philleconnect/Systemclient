#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - lockscreen
# © 2019 Johannes Kreutz.

# Include dependencies
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, QMetaObject
import sys
import threading

# Class definition
class lockscreen(QWidget):
    # Initialization
    def __init__(self):
        super().__init__()
        self.close()
        self.__title = "Der PC wurde durch die Lehrkraft gesperrt."
        self.__label = QLabel(self)
        self.__initUI()
        self.__initLabel()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setCursor(Qt.BlankCursor)

    def __initUI(self):
        self.setWindowTitle(self.__title)
        self.setGeometry(10, 40, 955, 240)
        # Set background to black
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.hide()

    def __initLabel(self):
        self.__label.setText('<span style="color:red">' + self.__title + '</span>')
        self.__label.setAlignment(Qt.AlignLeft)
        self.__label.move(8, 8)
        self.__label.setFont(QFont("Arial", 30, QFont.Normal))

    # Show window
    @pyqtSlot()
    def showGui(self):
        self.showFullScreen()

    # Hide window
    @pyqtSlot()
    def hideGui(self):
        self.hide()

    # Focus window
    @pyqtSlot()
    def focus(self):
        self.raise_()
        self.activateWindow()
