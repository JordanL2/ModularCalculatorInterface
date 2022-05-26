#!/usr/bin/python3

from modularcalculatorinterface.gui.guiwidgets import screenRelativeSize

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class AboutDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.initContent()

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        self.layout.addWidget(button)

        self.setLayout(self.layout)
        self.setWindowTitle("About")
        self.setVisible(True)
        self.setModal(True)

    def initContent(self):
        # Title
        self.layout.addWidget(FormattedLabel(
            "Modular Calculator",
            20,
            True,
            Qt.AlignHCenter,
            100, 50, 100, 50
        ))

        # Version
        self.layout.addWidget(FormattedLabel(
            "Version 1.3.0",
            10,
            False,
            Qt.AlignHCenter,
            100, 0, 100, 20
        ))

        # Description
        self.layout.addWidget(FormattedLabel(
            "A powerful, scriptable, modular calculator aimed at scientific, engineering or computing work.",
            10,
            False,
            Qt.AlignHCenter,
            0, 0, 0, 0
        ))

        # Website URL
        self.layout.addWidget(UrlFormattedLabel(
            "github.com/JordanL2/ModularCalculatorInterface",
            "https://github.com/JordanL2/ModularCalculatorInterface",
            10,
            False,
            Qt.AlignHCenter,
            0, 0, 0, 0
        ))

        # Copyright + developer name
        self.layout.addWidget(FormattedLabel(
            "\u00a9 2018-2022 Jordan Leppert",
            10,
            False,
            Qt.AlignHCenter,
            0, 0, 0, 50
        ))


    def ok(self):
        self.close()


class FormattedLabel(QLabel):

    def __init__(self, content, fontSize, fontBold, alignment, marginsLeft, marginsTop, marginsRight, marginsBottom):
        super().__init__(content)

        font = self.font()
        font.setPointSize(fontSize)
        font.setBold(fontBold)
        self.setFont(font)

        self.setAlignment(alignment)

        self.setContentsMargins(marginsLeft, marginsTop, marginsRight, marginsBottom)


class UrlFormattedLabel(FormattedLabel):

    def __init__(self, content, url, fontSize, fontBold, alignment, marginsLeft, marginsTop, marginsRight, marginsBottom):
        htmlContent = "<a href=\"{0}\">{1}</a>".format(url, content)
        super().__init__(htmlContent, fontSize, fontBold, alignment, marginsLeft, marginsTop, marginsRight, marginsBottom)

        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
