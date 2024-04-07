#!/usr/bin/python3

from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WhatsNewDialog(QDialog):

    def __init__(self, interface, newVersions):
        super().__init__(interface)

        self.interface = interface

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.changes = self.interface.config.whatsnew
        self.initContent(newVersions)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        self.layout.addWidget(button)

        self.setLayout(self.layout)
        self.setWindowTitle("What's New")
        self.setModal(True)
        self.setVisible(True)

    def initContent(self, newVersions):
        self.layout.addWidget(TopHeaderLabel("Changes"))
        for version in newVersions:
            self.layout.addWidget(HeaderLabel(version))
            for change in self.changes[version]:
                self.layout.addWidget(ChangeLabel("- " + change))
        self.layout.addWidget(FooterLabel("To ensure you're using the latest features, go to Options > Features\nand choose 'Select All' in the Presets dropdown."))

    def ok(self):
        self.close()


class TopHeaderLabel(QLabel):

    def __init__(self, content):
        super().__init__(content)

        font = self.font()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)

        self.setContentsMargins(50, 25, 50, 0)


class HeaderLabel(QLabel):

    def __init__(self, content):
        super().__init__(content)

        font = self.font()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)

        self.setContentsMargins(50, 20, 50, 0)


class ChangeLabel(QLabel):

    def __init__(self, content):
        super().__init__(content)

        self.setContentsMargins(50, 0, 50, 0)


class FooterLabel(QLabel):

    def __init__(self, content):
        super().__init__(content)

        font = self.font()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)

        self.setContentsMargins(50, 20, 50, 25)
