#!/usr/bin/python3

from modularcalculatorinterface.gui.display import *
from modularcalculatorinterface.gui.entry import *
from modularcalculatorinterface.gui.menu import *
from modularcalculatorinterface.gui.statefulapplication import *
from modularcalculatorinterface.gui.whatsnew import *
from modularcalculatorinterface.services.calculatormanager import *
from modularcalculatorinterface.services.filemanager import *
from modularcalculatorinterface.services.htmlservice import *
from modularcalculatorinterface.services.tabmanager import *

from PyQt6.QtCore import Qt, QThreadPool, QTimer, QSize
from PyQt6.QtGui import QKeySequence, QIcon, QGuiApplication, QFontDatabase, QFontInfo, QShortcut
from PyQt6.QtWidgets import QWidget, QGridLayout, QSplitter, QFileDialog, QMessageBox, QScrollArea, QSizePolicy, QToolBar

import os.path
import sys
import traceback


class ModularCalculatorInterface(StatefulApplication):

    def __init__(self, args, config):
        super().__init__()

        self.config = config

        self.setIcon()
        QGuiApplication.setDesktopFileName('io.github.jordanl2.ModularCalculator')

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.htmlservice = HtmlService(self)
        self.initUI()

        self.calculatormanager = CalculatorManager(self)
        self.filemanager = FileManager(self)
        self.tabmanager = TabManager(self)
        self.filemanager.tabmanager = self.tabmanager
        self.menu = CalculatorMenu(self)
        self.calculatormanager.updateInsertOptions()

        # Attempt to restore state, if exception then try clear state
        if not args.clear:
            restoreStates = [True, False]
        else:
            restoreStates = [False]
        for restoreState in restoreStates:
            try:
                self.stateHashes = {}
                if restoreState:
                    self.restoreAllState()
                else:
                    self.initEmptyState()
                self.tabmanager.forceRefreshAllTabs()
                self.entry.refresh()
                break
            except Exception as e:
                if not restoreState:
                    raise e
                else:
                    self.printError()
                    self.printError("Error occurred when restoring state. Will try starting with a clean state...")

        self.initShortcuts()
        self.entry.setFocus()
        self.show()
        self.display.layout.doResize(force=True)

        self.saveStateTimer = QTimer(self)
        self.saveStateTimer.start(15000)
        self.saveStateTimer.timeout.connect(self.storeAllState)

        # Hack for Qt6 to make tabbar appear on start
        self.tabbar.addTab("")
        self.tabbar.removeTab(self.tabbar.count() - 1)

        self.displayWhatsNew()

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
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(20, 20))

        self.tabbarWidget = TabBarWithPlus(self)
        self.tabbar = self.tabbarWidget.tabbar

        self.entry = CalculatorEntry(self)

        self.displayScroll = QScrollArea()
        self.display = CalculatorDisplay(self)

        self.displayScroll.setWidgetResizable(True)
        self.displayScroll.setWidget(self.display)
        self.displayScroll.widget().setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Maximum)
        scrollBar = self.displayScroll.verticalScrollBar()
        scrollBar.rangeChanged.connect(lambda: scrollBar.setValue(scrollBar.maximum()))

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.makeSection(self.entry, 'Input'))
        self.splitter.addWidget(self.makeSection(self.displayScroll, 'Output'))

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar, 0, 0, 1, 1)
        layout.setRowStretch(0, 0)
        layout.addWidget(self.tabbarWidget, 1, 0, 1, 1)
        layout.setRowStretch(1, 0)
        layout.addWidget(self.splitter, 2, 0, 1, 1)
        layout.setRowStretch(2, 1)

        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

    def makeSection(self, widget, labelText):
        label = QLabel(labelText)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.TitleFont)
        font.setBold(True)
        label.setFont(font)
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(widget, 1, 0, 1, 1)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def initShortcuts(self):
        previousTab = QShortcut(QKeySequence("Ctrl+PgUp"), self)
        previousTab.activated.connect(self.tabmanager.previousTab)
        nextTab = QShortcut(QKeySequence("Ctrl+PgDown"), self)
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
            self.printError("Exception when trying to restore state")
            self.printError()

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
        response = QMessageBox.question(self,
            title,
            question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)
        if response == QMessageBox.StandardButton.Yes:
            return True
        elif response == QMessageBox.StandardButton.No:
            return False
        return None


    def applyConfig(self):
        self.calculatormanager.initCalculator()
        self.entry.syntaxservice.restartProc()
        self.tabmanager.forceRefreshAllTabs()
        self.htmlservice.initStyling()
        self.entry.refresh()
        self.display.refresh()
        self.menu.refresh()
        self.config.saveMainConfig()


    def displayWhatsNew(self):
        newVersions = self.config.upgradesDone
        if len(newVersions) > 0:
            WhatsNewDialog(self, newVersions[-1])

    def getDefaultFixedFont(self):
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setFixedPitch(True)
        fontInfo = QFontInfo(font)
        return fontInfo.family()

    def printError(self, e=None):
        if e is None:
            print(traceback.format_exc(), file=sys.stderr)
        else:
            print(str(e), file=sys.stderr)
