#!/usr/bin/python3

from modularcalculatorinterface.gui.about import *
from modularcalculatorinterface.gui.featureconfig import *
from modularcalculatorinterface.gui.featureoptions import *
from modularcalculatorinterface.gui.guiwidgets import *

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QKeySequence, QCursor, QDesktopServices
from PyQt5.QtWidgets import QAction, QFileDialog, QToolTip

from functools import partial
import os.path
import string


class CalculatorMenu():

    def __init__(self, interface):
        self.interface = interface
        self.initMenu()

    def initMenu(self):
        menubar = self.interface.menuBar()

        self.fileMenu = menubar.addMenu('File')

        fileNew = QAction('New Tab', self.interface)
        fileNew.triggered.connect(self.interface.tabmanager.addTab)
        fileNew.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        self.fileMenu.addAction(fileNew)

        fileClose = QAction('Close Tab', self.interface)
        fileClose.triggered.connect(self.interface.tabmanager.closeCurrentTab)
        fileClose.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_W))
        self.fileMenu.addAction(fileClose)

        fileOpen = QAction('Open', self.interface)
        fileOpen.triggered.connect(self.interface.filemanager.open)
        fileOpen.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.fileMenu.addAction(fileOpen)

        self.fileSave = QAction('Save', self.interface)
        self.fileSave.triggered.connect(self.interface.filemanager.save)
        self.fileSave.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.fileMenu.addAction(self.fileSave)

        fileSaveAs = QAction('Save As...', self.interface)
        fileSaveAs.triggered.connect(self.interface.filemanager.saveAs)
        fileSaveAs.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S))
        self.fileMenu.addAction(fileSaveAs)

        viewMenu = menubar.addMenu('View')

        self.viewShortUnits = QAction('Units in Short Form', self.interface, checkable=True)
        self.viewShortUnits.triggered.connect(self.interface.calculatormanager.setShortUnits)
        viewMenu.addAction(self.viewShortUnits)

        self.viewSyntaxParsingAutoExecutes = QAction('Show Execution Errors', self.interface, checkable=True)
        self.viewSyntaxParsingAutoExecutes.triggered.connect(self.interface.calculatormanager.setAutoExecute)
        viewMenu.addAction(self.viewSyntaxParsingAutoExecutes)

        self.viewLineHighlighting = QAction('Line Highlighting', self.interface, checkable=True)
        self.viewLineHighlighting.triggered.connect(self.setLineHighlighting)
        viewMenu.addAction(self.viewLineHighlighting)

        self.viewThemesMenu = viewMenu.addMenu('Themes')
        self.viewThemesActions = {}
        for theme in sorted(self.interface.htmlService.syntax.keys()):
            themeAction = QAction(theme, self.interface, checkable=True)
            if theme == self.interface.htmlService.theme:
                themeAction.setChecked(True)
            themeAction.triggered.connect(partial(self.setTheme, theme))
            self.viewThemesActions[theme] = themeAction
            self.viewThemesMenu.addAction(themeAction)

        self.viewClearOutput = QAction('Clear Output', self.interface)
        self.viewClearOutput.triggered.connect(self.interface.display.clear)
        self.viewClearOutput.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        viewMenu.addAction(self.viewClearOutput)


        actionMenu = menubar.addMenu('Insert')

        self.insertConstantAction = QAction('Constant', self.interface)
        self.insertConstantAction.triggered.connect(self.insertConstant)
        self.insertConstantAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_C))
        actionMenu.addAction(self.insertConstantAction)

        self.insertDateAction = QAction('Date && Time', self.interface)
        self.insertDateAction.triggered.connect(self.insertDate)
        self.insertDateAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_D))
        actionMenu.addAction(self.insertDateAction)

        self.insertUnitAction = QAction('Unit', self.interface)
        self.insertUnitAction.triggered.connect(self.insertUnit)
        self.insertUnitAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_U))
        actionMenu.addAction(self.insertUnitAction)

        self.insertUnitSystemAction = QAction('Unit System', self.interface)
        self.insertUnitSystemAction.triggered.connect(self.insertUnitSystem)
        self.insertUnitSystemAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Y))
        actionMenu.addAction(self.insertUnitSystemAction)

        self.insertOperatorAction = QAction('Operator', self.interface)
        self.insertOperatorAction.triggered.connect(self.insertOperator)
        self.insertOperatorAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O))
        actionMenu.addAction(self.insertOperatorAction)

        self.insertFunctionAction = QAction('Function', self.interface)
        self.insertFunctionAction.triggered.connect(self.insertFunction)
        self.insertFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F))
        actionMenu.addAction(self.insertFunctionAction)

        self.insertUserDefinedFunctionAction = QAction('User-Defined Function', self.interface)
        self.insertUserDefinedFunctionAction.triggered.connect(self.insertUserDefinedFunction)
        self.insertUserDefinedFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_E))
        actionMenu.addAction(self.insertUserDefinedFunctionAction)

        optionsMenu = menubar.addMenu('Options')

        self.precisionSpinBox = MenuSpinBox(self.interface, 'Precision', 1, 50)
        self.precisionSpinBox.spinbox.valueChanged.connect(self.interface.calculatormanager.setPrecision)
        optionsMenu.addAction(self.precisionSpinBox)

        self.optionsSimplifyUnits = QAction('Simplify Units', self.interface, checkable=True)
        self.optionsSimplifyUnits.triggered.connect(self.interface.calculatormanager.setUnitSimplification)
        optionsMenu.addAction(self.optionsSimplifyUnits)

        self.optionsUnitSystemPreference = QAction('Unit System Preference', self.interface)
        self.optionsUnitSystemPreference.triggered.connect(self.openUnitSystemPreference)
        optionsMenu.addAction(self.optionsUnitSystemPreference)

        self.optionsFeatureConfig = QAction('Install/Remove Features', self.interface)
        self.optionsFeatureConfig.triggered.connect(self.openFeatureConfig)
        optionsMenu.addAction(self.optionsFeatureConfig)

        self.optionsFeatureOptions = QAction('Feature Options', self.interface)
        self.optionsFeatureOptions.triggered.connect(self.openFeatureOptions)
        optionsMenu.addAction(self.optionsFeatureOptions)

        helpMenu = menubar.addMenu('Help')

        self.helpHelpAction = QAction('Calculator Reference', self.interface)
        self.helpHelpAction.triggered.connect(self.openHelp)
        helpMenu.addAction(self.helpHelpAction)

        self.helpAboutAction = QAction('About', self.interface)
        self.helpAboutAction.triggered.connect(self.openHelpAbout)
        helpMenu.addAction(self.helpAboutAction)

        self.executeAction = QAction('Execute', self.interface)
        self.executeAction.triggered.connect(self.interface.calculatormanager.calc)
        self.executeAction.hovered.connect(self.showExecuteToolTip)
        menubar.addAction(self.executeAction)
        self.executeAction.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_Enter), QKeySequence(Qt.CTRL + Qt.Key_Return)])

    def showExecuteToolTip(self):
        QToolTip.showText(QCursor.pos(), "Ctrl+Enter", self.interface)

    def setLineHighlighting(self, lineHighlighting, refresh=True):
        self.interface.lineHighlighting = lineHighlighting
        self.viewLineHighlighting.setChecked(lineHighlighting)
        if refresh:
            self.interface.tabmanager.forceRefreshAllTabs()
            self.interface.entry.refresh()

    def setTheme(self, theme):
        self.interface.htmlService.setTheme(theme)
        for themeActionTheme, themeAction in self.viewThemesActions.items():
            themeAction.setChecked(theme == themeActionTheme)

    def insertConstant(self):
        constants = sorted(self.interface.calculatormanager.calculator.constants.keys(), key=str)
        SelectionDialog(self.interface, 'Insert Constant', 'Select constant to insert', constants, self.selectConstant)

    def selectConstant(self, constant):
        self.interface.entry.insert(constant)

    def insertDate(self):
        DatePicker(self.interface, 'Select Date & Time', self.selectDate)

    def selectDate(self, date, time):
        self.interface.entry.insert("'{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}'".format(date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second()))

    def getAllFunctions(self, condition=None):
        funcs = {}
        descriptions = {}
        for func, funcInfo in self.interface.calculatormanager.calculator.funcs.items():
            if condition is None or condition(funcInfo):
                category = funcInfo.category
                if category not in funcs:
                    funcs[category] = []
                funcs[category].append(func)
                descriptions[func] = "{}\n{}({})".format(funcInfo.description, func, ', '.join(funcInfo.syntax))
        return funcs, descriptions

    def insertFunction(self):
        funcs, descriptions = self.getAllFunctions()
        CategorisedSelectionDialog(self.interface, 'Insert Function', 'Select function to insert', funcs, descriptions, self.selectFunction)

    def selectFunction(self, func):
        funcInfo = self.interface.calculatormanager.calculator.funcs[func]
        self.interface.entry.insert("{}({})".format(func, ', '.join(funcInfo.syntax)))

    def insertUserDefinedFunction(self):
        if 'structure.externalfunctions' not in self.interface.calculatormanager.calculator.installed_features:
            QMessageBox.critical(self.interface, "ERROR", "User Defined Functions feature not enabled.")
        else:
            filePath, _ = QFileDialog.getOpenFileName(self.interface, "Select user-defined function file", "", "All Files (*)")
            if filePath:
                funcname = os.path.basename(filePath)
                whitelist = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '_')
                funcname = ''.join(c for c in funcname if c in whitelist)
                if funcname == '':
                    funcname = 'userDefinedFunction'
                if funcname[0] in string.digits:
                    funcname = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][int(funcname[0])] + funcname[1:]
                terminator = self.interface.calculatormanager.calculator.feature_options['structure.terminator']['Symbol']
                quote = self.interface.calculatormanager.calculator.feature_options['strings.strings']['Symbol']
                whitespace = ' '
                if 'nonfunctional.space' not in self.interface.calculatormanager.calculator.installed_features:
                    whitespace = ''
                self.interface.entry.insert("{}{}={}{}{}{}{}".format(funcname, whitespace, whitespace, quote, filePath, quote, terminator))

    def insertOperator(self):
        operators = {}
        descriptions = {}
        for op, opInfo in self.interface.calculatormanager.calculator.ops_list.items():
            if not opInfo.hidden:
                category = opInfo.category
                if category not in operators:
                    operators[category] = []
                operators[category].append(op)
                descriptions[op] = "{}\n{}".format(opInfo.description, ' '.join(opInfo.syntax))
        CategorisedSelectionDialog(self.interface, 'Insert Operator', 'Select operator to insert', operators, descriptions, self.selectOperator)

    def selectOperator(self, operator):
        self.interface.entry.insert(operator)

    def insertUnit(self):
        units = {}
        descriptions = {}
        for dimension in self.interface.calculatormanager.calculator.unit_normaliser.units:
            dimensionTitle = self.interface.calculatormanager.calculator.unit_normaliser.dimensions[dimension]
            units[dimensionTitle] = []
            for unit in self.interface.calculatormanager.calculator.unit_normaliser.units[dimension]:
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
                    unitsystem = self.interface.calculatormanager.calculator.unit_normaliser.systems[self.interface.calculatormanager.calculator.unit_normaliser.get_preferred_system(unit.systems)].name
                descriptions[unitName] = "{}.\nAlternative names: {}".format(unitsystem, altnames)
        CategorisedSelectionDialog(self.interface, 'Insert Unit', 'Select unit to insert', units, descriptions, self.selectUnit)

    def selectUnit(self, unit):
        self.interface.entry.insert(unit)

    def insertUnitSystem(self):
        systems = dict([(s, v.name) for s, v in sorted(self.interface.calculatormanager.calculator.unit_normaliser.systems.items(), key=lambda x: x[1].name.lower())])
        SelectionDialog(self.interface, 'Insert Unit System', 'Select unit system to insert', systems, self.selectUnitSystem)

    def selectUnitSystem(self, operator):
        self.interface.entry.insert(operator)

    def openUnitSystemPreference(self):
        calculator = self.interface.calculatormanager.calculator
        SortableListDialog(self.interface,
            'Unit System Preference',
            'Order unit systems by preference, most prefered at top',
            [calculator.unit_normaliser.systems[s].name for s in calculator.unit_normaliser.systems_preference if s in calculator.unit_normaliser.systems]
            + [calculator.unit_normaliser.systems[s].name for s in calculator.unit_normaliser.systems if s not in calculator.unit_normaliser.systems_preference],
            self.interface.calculatormanager.updateUnitSystemPreference)

    def openFeatureConfig(self):
        FeatureConfigDialog(self.interface)

    def openFeatureOptions(self):
        FeatureOptionsDialog(self.interface)

    def openHelp(self):
        QDesktopServices.openUrl(QUrl('https://github.com/JordanL2/ModularCalculator/wiki'))

    def openHelpAbout(self):
        AboutDialog(self.interface)
