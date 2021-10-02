#!/usr/bin/python3

from modularcalculatorinterface.calculatormanager import *
from modularcalculatorinterface.display import *
from modularcalculatorinterface.featureconfig import *
from modularcalculatorinterface.featureoptions import *
from modularcalculatorinterface.filemanager import *
from modularcalculatorinterface.guiwidgets import *
from modularcalculatorinterface.statefulapplication import *
from modularcalculatorinterface.tabmanager import *
from modularcalculatorinterface.textedit import *
from modularcalculatorinterface.tools import *

from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtGui import QKeySequence, QCursor, QPalette, QIcon, QGuiApplication
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QSplitter, QAction, QFileDialog, QToolTip, QShortcut, QMessageBox, QScrollArea, QSizePolicy

import os.path
import string
import sys
import traceback


class ModularCalculatorInterface(StatefulApplication):

    def __init__(self, clear):
        super().__init__()

        self.setIcon()
        QGuiApplication.setDesktopFileName('io.github.jordanl2.ModularCalculator')

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.initUI()

        self.calculatormanager = CalculatorManager(self)
        self.filemanager = FileManager(self)
        self.tabmanager = TabManager(self)
        self.filemanager.tabmanager = self.tabmanager

        self.initMenu()

        self.stateHashes = {}
        if not clear:
            self.restoreAllState()
        else:
            self.initEmptyState()
        self.saveStateTimer = QTimer(self)
        self.saveStateTimer.start(15000)
        self.saveStateTimer.timeout.connect(self.storeAllState)

        self.calculatormanager.updateInsertOptions()
        self.initShortcuts()

        self.entry.setFocus()
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

        self.entry = CalculatorTextEdit(self)

        self.display = CalculatorDisplay(self)
        self.displayScroll = QScrollArea()
        self.displayScroll.setBackgroundRole(self.display.colours[0])
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

    def initMenu(self):
        menubar = self.menuBar()
        
        self.fileMenu = menubar.addMenu('File')
        
        fileNew = QAction('New Tab', self)
        fileNew.triggered.connect(self.tabmanager.addTab)
        fileNew.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        self.fileMenu.addAction(fileNew)
        
        fileClose = QAction('Close Tab', self)
        fileClose.triggered.connect(self.tabmanager.closeCurrentTab)
        fileClose.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_W))
        self.fileMenu.addAction(fileClose)

        fileOpen = QAction('Open', self)
        fileOpen.triggered.connect(self.filemanager.open)
        fileOpen.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.fileMenu.addAction(fileOpen)
        
        self.fileSave = QAction('Save', self)
        self.fileSave.triggered.connect(self.filemanager.save)
        self.fileSave.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.fileMenu.addAction(self.fileSave)
        
        fileSaveAs = QAction('Save As...', self)
        fileSaveAs.triggered.connect(self.filemanager.saveAs)
        fileSaveAs.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S))
        self.fileMenu.addAction(fileSaveAs)

        viewMenu = menubar.addMenu('View')

        self.viewShortUnits = QAction('Units in Short Form', self, checkable=True)
        self.viewShortUnits.triggered.connect(self.calculatormanager.setShortUnits)
        viewMenu.addAction(self.viewShortUnits)

        self.viewSyntaxParsingAutoExecutes = QAction('Show Execution Errors', self, checkable=True)
        self.viewSyntaxParsingAutoExecutes.triggered.connect(self.calculatormanager.setAutoExecute)
        viewMenu.addAction(self.viewSyntaxParsingAutoExecutes)

        self.viewLineHighlighting = QAction('Line Highlighting', self, checkable=True)
        self.viewLineHighlighting.triggered.connect(self.entry.setLineHighlighting)
        viewMenu.addAction(self.viewLineHighlighting)

        self.viewClearOutput = QAction('Clear Output', self)
        self.viewClearOutput.triggered.connect(self.display.clear)
        self.viewClearOutput.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        viewMenu.addAction(self.viewClearOutput)

        actionMenu = menubar.addMenu('Insert')
        
        self.insertConstantAction = QAction('Constant', self)
        self.insertConstantAction.triggered.connect(self.insertConstant)
        self.insertConstantAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_C))
        actionMenu.addAction(self.insertConstantAction)
        
        self.insertDateAction = QAction('Date && Time', self)
        self.insertDateAction.triggered.connect(self.insertDate)
        self.insertDateAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_D))
        actionMenu.addAction(self.insertDateAction)
        
        self.insertUnitAction = QAction('Unit', self)
        self.insertUnitAction.triggered.connect(self.insertUnit)
        self.insertUnitAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_U))
        actionMenu.addAction(self.insertUnitAction)
        
        self.insertUnitSystemAction = QAction('Unit System', self)
        self.insertUnitSystemAction.triggered.connect(self.insertUnitSystem)
        self.insertUnitSystemAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Y))
        actionMenu.addAction(self.insertUnitSystemAction)
        
        self.insertOperatorAction = QAction('Operator', self)
        self.insertOperatorAction.triggered.connect(self.insertOperator)
        self.insertOperatorAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O))
        actionMenu.addAction(self.insertOperatorAction)
        
        self.insertFunctionAction = QAction('Function', self)
        self.insertFunctionAction.triggered.connect(self.insertFunction)
        self.insertFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F))
        actionMenu.addAction(self.insertFunctionAction)
        
        self.insertUserDefinedFunctionAction = QAction('User-Defined Function', self)
        self.insertUserDefinedFunctionAction.triggered.connect(self.insertUserDefinedFunction)
        self.insertUserDefinedFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_E))
        actionMenu.addAction(self.insertUserDefinedFunctionAction)

        optionsMenu = menubar.addMenu('Options')
        
        self.precisionSpinBox = MenuSpinBox(self, 'Precision', 1, 50)
        self.precisionSpinBox.spinbox.valueChanged.connect(self.calculatormanager.setPrecision)
        optionsMenu.addAction(self.precisionSpinBox)

        self.optionsSimplifyUnits = QAction('Simplify Units', self, checkable=True)
        self.optionsSimplifyUnits.triggered.connect(self.calculatormanager.setUnitSimplification)
        optionsMenu.addAction(self.optionsSimplifyUnits)

        self.optionsUnitSystemPreference = QAction('Unit System Preference', self)
        self.optionsUnitSystemPreference.triggered.connect(self.openUnitSystemPreference)
        optionsMenu.addAction(self.optionsUnitSystemPreference)

        self.optionsFeatureConfig = QAction('Install/Remove Features', self)
        self.optionsFeatureConfig.triggered.connect(self.openFeatureConfig)
        optionsMenu.addAction(self.optionsFeatureConfig)

        self.optionsFeatureOptions = QAction('Feature Options', self)
        self.optionsFeatureOptions.triggered.connect(self.openFeatureOptions)
        optionsMenu.addAction(self.optionsFeatureOptions)

        self.executeAction = QAction('Execute', self)
        self.executeAction.triggered.connect(self.calculatormanager.calc)
        self.executeAction.hovered.connect(self.showExecuteToolTip)
        menubar.addAction(self.executeAction)
        self.executeAction.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_Enter), QKeySequence(Qt.CTRL + Qt.Key_Return)])

    def showExecuteToolTip(self):
        QToolTip.showText(QCursor.pos(), "Ctrl+Enter", self)

    def initShortcuts(self):
        previousTab = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_PageUp), self)
        previousTab.activated.connect(self.tabmanager.previousTab)
        nextTab = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_PageDown), self)
        nextTab.activated.connect(self.tabmanager.nextTab)


    def initEmptyState(self):
        self.calculatormanager.initEmptyState()
        self.tabmanager.initEmptyState()

    def restoreAllState(self):
        try:
            self.restoreGeometry(self.fetchState("mainWindowGeometry"))
            self.restoreState(self.fetchState("mainWindowState"))
            self.splitter.restoreState(self.fetchState("splitterSizes"))

            self.calculatormanager.restoreState(self.fetchStateMap("calculatorManager"))

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

        calculatorManager = self.calculatormanager.saveState()
        calculatorManagerHash = maphash(calculatorManager)
        if 'calculatorManager' not in self.stateHashes or calculatorManagerHash != self.stateHashes['calculatorManager']:
            self.stateHashes['calculatorManager'] = calculatorManagerHash
            self.storeStateMap("calculatorManager", calculatorManager)

        tabManager = self.tabmanager.saveState()
        tabManagerHash = maphash(tabManager)
        if 'tabManager' not in self.stateHashes or tabManagerHash != self.stateHashes['tabManager']:
            self.stateHashes['tabManager'] = tabManagerHash
            self.storeStateMap("tabManager", tabManager)

    def insertConstant(self):
        constants = sorted(self.calculatormanager.calculator.constants.keys(), key=str)
        SelectionDialog(self, 'Insert Constant', 'Select constant to insert', constants, self.selectConstant)

    def selectConstant(self, constant):
        self.entry.insert(constant)

    def insertDate(self):
        DatePicker(self, 'Select Date & Time', self.selectDate)

    def selectDate(self, date, time):
        self.entry.insert("'{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}'".format(date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second()))

    def getAllFunctions(self, condition=None):
        funcs = {}
        descriptions = {}
        for func, funcInfo in self.calculatormanager.calculator.funcs.items():
            if condition is None or condition(funcInfo):
                category = funcInfo.category
                if category not in funcs:
                    funcs[category] = []
                funcs[category].append(func)
                descriptions[func] = "{}\n{}({})".format(funcInfo.description, func, ', '.join(funcInfo.syntax))
        return funcs, descriptions

    def insertFunction(self):
        funcs, descriptions = self.getAllFunctions()
        CategorisedSelectionDialog(self, 'Insert Function', 'Select function to insert', funcs, descriptions, self.selectFunction)

    def selectFunction(self, func):
        funcInfo = self.calculatormanager.calculator.funcs[func]
        self.entry.insert("{}({})".format(func, ', '.join(funcInfo.syntax)))

    def insertUserDefinedFunction(self):
        if 'structure.externalfunctions' not in self.calculatormanager.calculator.installed_features:
            QMessageBox.critical(self, "ERROR", "User Defined Functions feature not enabled.")
        else:
            filePath, _ = QFileDialog.getOpenFileName(self, "Select user-defined function file", "", "All Files (*)")
            if filePath:
                funcname = os.path.basename(filePath)
                whitelist = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '_')
                funcname = ''.join(c for c in funcname if c in whitelist)
                if funcname == '':
                    funcname = 'userDefinedFunction'
                if funcname[0] in string.digits:
                    funcname = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][int(funcname[0])] + funcname[1:]
                terminator = self.calculatormanager.calculator.feature_options['structure.terminator']['Symbol']
                quote = self.calculatormanager.calculator.feature_options['strings.strings']['Symbol']
                whitespace = ' '
                if 'nonfunctional.space' not in self.calculatormanager.calculator.installed_features:
                    whitespace = ''
                self.entry.insert("{}{}={}{}{}{}{}".format(funcname, whitespace, whitespace, quote, filePath, quote, terminator))

    def insertOperator(self):
        operators = {}
        descriptions = {}
        for op, opInfo in self.calculatormanager.calculator.ops_list.items():
            if not opInfo.hidden:
                category = opInfo.category
                if category not in operators:
                    operators[category] = []
                operators[category].append(op)
                descriptions[op] = "{}\n{}".format(opInfo.description, ' '.join(opInfo.syntax))
        CategorisedSelectionDialog(self, 'Insert Operator', 'Select operator to insert', operators, descriptions, self.selectOperator)

    def selectOperator(self, operator):
        self.entry.insert(operator)

    def insertUnit(self):
        units = {}
        descriptions = {}
        for dimension in self.calculatormanager.calculator.unit_normaliser.units:
            dimensionTitle = self.calculatormanager.calculator.unit_normaliser.dimensions[dimension]
            units[dimensionTitle] = []
            for unit in self.calculatormanager.calculator.unit_normaliser.units[dimension]:
                unitName = unit.singular()
                units[dimensionTitle].append(unitName)
                altnames = []
                for name in unit.names() + unit.symbols():
                    if name not in altnames and name != unitName:
                        altnames.append(name)
                altnames = ', '.join(altnames)
                if unit.systems is None or len(unit.systems) == 0:
                    unitsystem = 'No unit system'
                else:
                    unitsystem = self.calculatormanager.calculator.unit_normaliser.systems[self.calculatormanager.calculator.unit_normaliser.get_preferred_system(unit.systems)].name
                descriptions[unitName] = "{}.\nAlternative names: {}".format(unitsystem, altnames)
        CategorisedSelectionDialog(self, 'Insert Unit', 'Select unit to insert', units, descriptions, self.selectUnit)

    def selectUnit(self, unit):
        self.entry.insert(unit)

    def insertUnitSystem(self):
        systems = dict([(s, v.name) for s, v in sorted(self.calculatormanager.calculator.unit_normaliser.systems.items(), key=lambda x: x[1].name.lower())])
        SelectionDialog(self, 'Insert Unit System', 'Select unit system to insert', systems, self.selectUnitSystem)

    def selectUnitSystem(self, operator):
        self.entry.insert(operator)

    def openUnitSystemPreference(self):
        SortableListDialog(self, 
            'Unit System Preference', 
            'Order unit systems by preference, most prefered at top', 
            [self.calculatormanager.calculator.unit_normaliser.systems[s].name for s in self.calculatormanager.calculator.unit_normaliser.systems_preference if s in self.calculatormanager.calculator.unit_normaliser.systems]
            + [self.calculatormanager.calculator.unit_normaliser.systems[s].name for s in self.calculatormanager.calculator.unit_normaliser.systems if s not in self.calculatormanager.calculator.unit_normaliser.systems_preference], 
            self.calculatormanager.updateUnitSystemPreference)

    def openFeatureConfig(self):
        FeatureConfigDialog(self)

    def openFeatureOptions(self):
        FeatureOptionsDialog(self)


def main():
    clear = False
    if len(sys.argv) >= 2 and sys.argv[1] == '--clear':
        print("Will not restore state due to --clear flag")
        clear = True
    app = QApplication(sys.argv)
    calc = ModularCalculatorInterface(clear)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
