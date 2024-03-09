#!/usr/bin/python3

from modularcalculatorinterface.gui.options.appearance import *
from modularcalculatorinterface.gui.options.calculator import *
from modularcalculatorinterface.gui.options.common import *
from modularcalculatorinterface.gui.options.display import *
from modularcalculatorinterface.gui.options.entry import *
from modularcalculatorinterface.gui.options.features import *

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QGridLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont, QFontDatabase


def getFixedWidthFonts():
    fonts = []
    for f in QFontDatabase.families():
        font = QFont(f)
        font.setFixedPitch(True)
        if font.exactMatch():
            fonts.append(f)
    return fonts

def getFontSizes():
    return [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            22, 24, 26, 28, 32, 48, 64, 72, 80, 96, 128]


class OptionTab(QPushButton):

    def __init__(self, optionsDialog, text, name):
        super().__init__(text)
        self.optionsDialog = optionsDialog
        self.name = name
        self.clicked.connect(self.doClick)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def doClick(self):
        self.optionsDialog.selectTab(self.name)


class OptionsDialog(QDialog):

    def __init__(self, interface):
        super().__init__(interface)

        self.interface = interface
        self.config = self.interface.config

        self.fixedWidthFonts = getFixedWidthFonts()
        self.fontSizes = getFontSizes()

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.buttons = {}
        self.initMenu()
        self.activeTab = None
        self.selectTab("appearance")
        self.setLayout(self.grid)

        self.setWindowTitle('Options')
        self.setModal(True)
        self.setVisible(True)

    def sizeHint(self):
        return QSize(1000, 700)

    def initMenu(self):
        menuWidget = QWidget(self)
        self.menuGrid = QGridLayout()
        self.addTab("Appearance", "appearance")
        self.addTab("Input", "entry")
        self.addTab("Output", "display")
        self.addTab("Calculator", "calculator")
        self.addTab("Features", "features")
        self.menuGrid.setRowStretch(self.menuGrid.rowCount(), 1)
        menuWidget.setLayout(self.menuGrid)
        menuWidget.setFixedWidth(self.menuGrid.sizeHint().width() + 20)

        self.grid.addWidget(menuWidget, 0, 0, 1, 1)

    def addTab(self, title, name):
        tabButton = OptionTab(self, title, name)
        self.buttons[name] = tabButton
        i = self.menuGrid.rowCount()
        self.menuGrid.addWidget(tabButton, i, 0, 1, 1)
        self.menuGrid.setRowStretch(i, 0)

    def selectTab(self, tab):
        if tab == "appearance":
            newTab = AppearanceTab(self)
        elif tab == "entry":
            newTab = EntryTab(self)
        elif tab == "display":
            newTab = DisplayTab(self)
        elif tab == "calculator":
            newTab = CalculatorTab(self)
        elif tab == "features":
            newTab = FeaturesTab(self)
        if self.activeTab is not None:
            self.grid.replaceWidget(self.activeTab, newTab)
            self.activeTab.setParent(None)
            self.activeTab.deleteLater()
            self.activeTab = newTab
        else:
            self.activeTab = newTab
            self.grid.addWidget(self.activeTab, 0, 1, 1, 1)
        for name in self.buttons:
            button = self.buttons[name]
            if tab == name:
                button.setChecked(True)
            else:
                button.setChecked(False)

    def closeEvent(self, e):
        self.interface.applyConfig()
        super().closeEvent(e)

    def reject(self):
        self.interface.applyConfig()
        super().reject()

