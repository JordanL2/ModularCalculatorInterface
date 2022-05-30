#!/usr/bin/python3

from modularcalculatorinterface.gui.display import *
from modularcalculatorinterface.gui.entry import *
from modularcalculatorinterface.gui.menu import *
from modularcalculatorinterface.gui.statefulapplication import *
from modularcalculatorinterface.services.calculatormanager import *
from modularcalculatorinterface.services.filemanager import *
from modularcalculatorinterface.services.htmlservice import *
from modularcalculatorinterface.services.tabmanager import *

from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtGui import QKeySequence, QIcon, QGuiApplication
from PyQt5.QtWidgets import QWidget, QGridLayout, QSplitter, QFileDialog, QShortcut, QMessageBox, QScrollArea, QSizePolicy

import os.path
import traceback


class ModularCalculatorInterface(StatefulApplication):

    def __init__(self, flags, config):
        super().__init__()

        self.config = config

        self.setIcon()
        QGuiApplication.setDesktopFileName('io.github.jordanl2.ModularCalculator')

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.htmlService = HtmlService(self)
        self.initUI()

        self.calculatormanager = CalculatorManager(self)
        self.filemanager = FileManager(self)
        self.tabmanager = TabManager(self)
        self.filemanager.tabmanager = self.tabmanager
        self.menu = CalculatorMenu(self)
        self.calculatormanager.updateInsertOptions()

        self.stateHashes = {}
        if not flags['clear']:
            self.restoreAllState()
        else:
            self.initEmptyState()
        self.saveStateTimer = QTimer(self)
        self.saveStateTimer.start(15000)
        self.saveStateTimer.timeout.connect(self.storeAllState)

        self.initShortcuts()

        self.entry.setFocus()
        self.tabmanager.forceRefreshAllTabs()
        self.entry.refresh()
        self.show()

    def setIcon(self):
        places = [
            '/usr/share/icons/hicolor/256x256/apps/io.github.jordanl2.ModularCalculator.png',
            '/app/share/icons/hicolor/256x256/apps/io.github.jordanl2.ModularCalculator.png',
            'icons/256x256.png'
            ]
        for place in places:
            if os.path.isfile(place):
                self.setWindowIcon(QIcon(place))
                return

    def initUI(self):
        self.tabbar = MiddleClickCloseableTabBar(self)

        self.entry = CalculatorEntry(self)

        self.displayScroll = QScrollArea()
        self.display = CalculatorDisplay(self)

        self.displayScroll.setWidgetResizable(True)
        self.displayScroll.setWidget(self.display)
        self.displayScroll.widget().setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)
        scrollBar = self.displayScroll.verticalScrollBar()
        scrollBar.rangeChanged.connect(lambda: scrollBar.setValue(scrollBar.maximum()))

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.makeSection(self.entry, 'Input'))
        self.splitter.addWidget(self.makeSection(self.displayScroll, 'Output'))

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.addWidget(self.tabbar, 0, 0, 1, 1)
        layout.addWidget(self.splitter, 1, 0, 1, 1)

        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

    def makeSection(self, widget, labelText):
        label = QLabel(labelText)
        label.setAlignment(Qt.AlignHCenter)
        font = QFontDatabase.systemFont(QFontDatabase.TitleFont)
        font.setBold(True)
        label.setFont(font)
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(widget, 1, 0, 1, 1)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def initShortcuts(self):
        previousTab = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_PageUp), self)
        previousTab.activated.connect(self.tabmanager.previousTab)
        nextTab = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_PageDown), self)
        nextTab.activated.connect(self.tabmanager.nextTab)


    def initEmptyState(self):
        self.tabmanager.initEmptyState()

    def restoreAllState(self):
        try:
            self.restoreGeometry(self.fetchState("mainWindowGeometry"))
            self.restoreState(self.fetchState("mainWindowState"))
            self.splitter.restoreState(self.fetchState("splitterSizes"))

            self.tabmanager.restoreState(self.fetchStateMap("tabManager"))
        except Exception as e:
            print("Exception when trying to restore state")
            print(traceback.format_exc())

    def storeAllState(self):
        mainWindowGeometry = self.saveGeometry()
        mainWindowGeometryHash = hash(mainWindowGeometry)
        if 'mainWindowGeometry' not in self.stateHashes or mainWindowGeometryHash != self.stateHashes['mainWindowGeometry']:
            self.stateHashes['mainWindowGeometry'] = mainWindowGeometryHash
            self.storeState("mainWindowGeometry", mainWindowGeometry)

        mainWindowState = self.saveState()
        mainWindowStateHash = hash(mainWindowState)
        if 'mainWindowState' not in self.stateHashes or mainWindowStateHash != self.stateHashes['mainWindowState']:
            self.stateHashes['mainWindowState'] = mainWindowStateHash
            self.storeState("mainWindowState", mainWindowState)

        splitterSizes = self.splitter.saveState()
        splitterSizesHash = hash(splitterSizes)
        if 'splitterSizes' not in self.stateHashes or splitterSizesHash != self.stateHashes['splitterSizes']:
            self.stateHashes['splitterSizes'] = splitterSizesHash
            self.storeState("splitterSizes", splitterSizes)

        tabManager = self.tabmanager.saveState()
        tabManagerHash = self.mapHash(tabManager)
        if 'tabManager' not in self.stateHashes or tabManagerHash != self.stateHashes['tabManager']:
            self.stateHashes['tabManager'] = tabManagerHash
            self.storeStateMap("tabManager", tabManager)


    def getOpenFileName(self, title, filterFiles):
        filePath, _ =  QFileDialog.getOpenFileName(self, title, "", filterFiles)
        return filePath

    def getSaveFileName(self, title, filterFiles):
        filePath, _ =  QFileDialog.getSaveFileName(self, title, "", filterFiles)
        return filePath

    def questionYesNoCancel(self, title, question):
        response = QMessageBox.question(self, title, question, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        if response == QMessageBox.Yes:
            return True
        elif response == QMessageBox.No:
            return False
        return None


    def applyConfig(self):
        self.calculatormanager.initCalculator()
        self.tabmanager.forceRefreshAllTabs()
        self.htmlService.initStyling()
        self.entry.refresh()
        self.display.refresh()
        self.config.saveMainConfig()
