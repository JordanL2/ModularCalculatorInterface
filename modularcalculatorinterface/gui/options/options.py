#!/usr/bin/python3

from modularcalculatorinterface.gui.options.appearance import *
from modularcalculatorinterface.gui.options.calculator import *
from modularcalculatorinterface.gui.options.common import *
from modularcalculatorinterface.gui.options.display import *
from modularcalculatorinterface.gui.options.entry import *
from modularcalculatorinterface.gui.options.features import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QListWidgetItem, QListWidget, QWidget


class OptionsDialog(QDialog):

    def __init__(self, interface):
        super().__init__(interface)

        self.interface = interface
        self.config = self.interface.config

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.initMenu()
        self.activeTab = None
        self.selectTab(self.optionMenu.item(0))
        self.setLayout(self.grid)

        self.setWindowTitle('Options')
        self.setModal(True)
        self.setVisible(True)

    def sizeHint(self):
        return limitToScreen(900, 700)

    def initMenu(self):
        self.optionMenu = QListWidget(self)

        item = QListWidgetItem("Appearance", self.optionMenu)
        item.setData(Qt.UserRole, "appearance")

        item = QListWidgetItem("Input", self.optionMenu)
        item.setData(Qt.UserRole, "entry")

        item = QListWidgetItem("Output", self.optionMenu)
        item.setData(Qt.UserRole, "display")

        item = QListWidgetItem("Calculator", self.optionMenu)
        item.setData(Qt.UserRole, "calculator")

        item = QListWidgetItem("Features", self.optionMenu)
        item.setData(Qt.UserRole, "features")

        menuWidget = QWidget(self)
        menuGrid = QGridLayout()
        menuGrid.addWidget(self.optionMenu, 0, 0, 1, 1)
        menuWidget.setLayout(menuGrid)
        menuWidget.setFixedWidth(self.optionMenu.sizeHintForColumn(0) + 20)

        self.optionMenu.itemClicked.connect(self.selectTab)
        self.grid.addWidget(menuWidget, 0, 0, 1, 1)

    def selectTab(self, item):
        tab = item.data(Qt.UserRole)
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

    def closeEvent(self, e):
        self.interface.applyConfig()
        super().closeEvent(e)
