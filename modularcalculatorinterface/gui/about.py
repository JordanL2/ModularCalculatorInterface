#!/usr/bin/python3

from modularcalculatorinterface.gui.guiwidgets import FormattedLabel, UrlFormattedLabel

from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class AboutDialog(QDialog):

    def __init__(self, interface):
        super().__init__(interface)

        self.interface = interface

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.initContent()

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        self.layout.addWidget(button)

        self.setLayout(self.layout)
        self.setWindowTitle("About")
        self.setModal(True)
        self.setVisible(True)

    def initContent(self):
        # Title
        self.layout.addWidget(FormattedLabel(
            "Modular Calculator",
            20,
            True,
            Qt.AlignmentFlag.AlignHCenter,
            100, 50, 100, 50
        ))

        # Version
        version = self.interface.config.version
        self.layout.addWidget(FormattedLabel(
            "Version {} {} ({})".format('.'.join([str(v) for v in version['version']]), version['lifecycle'], version['buildtype']),
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            100, 0, 100, 0
        ))

        # Qt Version
        self.layout.addWidget(FormattedLabel(
            "Qt version {}".format(QT_VERSION_STR),
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 0
        ))

        # PyQt Version
        self.layout.addWidget(FormattedLabel(
            "PyQt version {}".format(PYQT_VERSION_STR),
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 20
        ))

        # Description
        self.layout.addWidget(FormattedLabel(
            "A powerful, scriptable, modular calculator aimed at scientific, engineering or computing work.",
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 0
        ))

        # Website URL
        self.layout.addWidget(UrlFormattedLabel(
            "github.com/JordanL2/ModularCalculatorInterface",
            "https://github.com/JordanL2/ModularCalculatorInterface",
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 0
        ))

        # Copyright + developer name
        self.layout.addWidget(FormattedLabel(
            "\u00a9 2018-2024 Jordan Leppert",
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 0
        ))

        # License
        self.layout.addWidget(UrlFormattedLabel(
            "GNU General Public Licence version 3",
            "https://www.gnu.org/licenses/gpl-3.0.html",
            10,
            False,
            Qt.AlignmentFlag.AlignHCenter,
            0, 0, 0, 50
        ))

    def ok(self):
        self.close()
