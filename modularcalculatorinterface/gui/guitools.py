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
    size.setWidth(int(round(QApplication.desktop().screenGeometry().width() * width)))
    size.setHeight(int(round(QApplication.desktop().screenGeometry().height() * height)))
    return size

def makeSpan(text, clas=None, style=None):
    return "<span{0}{1}>{2}</span>".format(
        (" class=\"{}\"".format(clas) if clas is not None else ''),
        (" style=\"{}\"".format(style) if style is not None else ''),
        text)