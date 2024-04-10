#!/usr/bin/python3

from modularcalculatorinterface.gui.guiwidgets import FormattedLabel, UrlFormattedLabel

from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WhatsNewDialog(QDialog):

    def __init__(self, interface, newVersion):
        super().__init__(interface)

        self.interface = interface

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.changes = self.interface.config.whatsnew
        self.initContent(newVersion)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        self.layout.addWidget(button)

        self.setLayout(self.layout)
        self.setWindowTitle("What's New")
        self.setModal(True)
        self.setVisible(True)

    def initContent(self, newVersion):
        self.layout.addWidget(FormattedLabel(
            "Changes in {}".format(newVersion),
            14, True, Qt.AlignmentFlag.AlignHCenter,
            50, 25, 50, 25))
        for change in self.changes[newVersion]:
            self.layout.addWidget(FormattedLabel(
                "- {}".format(change),
                10, False, Qt.AlignmentFlag.AlignLeft,
                50, 0, 50, 0))
        self.layout.addWidget(UrlFormattedLabel(
            "Full Changelog", "https://github.com/JordanL2/ModularCalculatorInterface/blob/master/CHANGELOG.md",
            10, True, Qt.AlignmentFlag.AlignLeft,
            50, 0, 50, 0
            ))
        self.layout.addWidget(FormattedLabel(
            "To ensure you're using the latest features, go to Options > Features\nand choose 'Select All' in the Presets dropdown.",
            10, True, Qt.AlignmentFlag.AlignLeft,
            50, 20, 50, 30
            ))

    def ok(self):
        self.close()
