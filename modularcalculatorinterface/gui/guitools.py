#!/usr/bin/python3

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication


def screenRelativeSize(width, height):
    size = QSize()
    size.setWidth(int(round(QApplication.desktop().screenGeometry().width() * width)))
    size.setHeight(int(round(QApplication.desktop().screenGeometry().height() * height)))
    return size
