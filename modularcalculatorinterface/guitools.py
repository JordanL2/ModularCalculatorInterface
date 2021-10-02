#!/usr/bin/python3

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication

import html


def htmlSafe(text):
    text_escape = html.escape(str(text))
    text_escape = text_escape.replace(' ', '&nbsp;')
    text_escape = text_escape.replace("\n", '<br/>')

    return text_escape

def screenRelativeSize(width, height):
    size = QSize()
    size.setWidth(QApplication.desktop().screenGeometry().width() * width)
    size.setHeight(QApplication.desktop().screenGeometry().height() * height)
    return size

def makeSpan(text, style):
    return "<span class='{0}'>{1}</span>".format(style, text)
