#!/usr/bin/python3

from modularcalculatorinterface.gui.about import *
from modularcalculatorinterface.gui.display import CalculatorDisplayAnswer, CalculatorDisplayError
from modularcalculatorinterface.gui.guiwidgets import *
from modularcalculatorinterface.gui.options.options import *

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QKeySequence, QDesktopServices, QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QToolButton, QMenu

import csv
import os.path
import string


class CalculatorMenu():

    def __init__(self, interface):
        self.interface = interface
        self.config = self.interface.config
        self.initMenu()
        self.refresh()

    def initMenu(self):
        self.toolbar = self.interface.toolbar

        self.fileOpen = QAction(QIcon.fromTheme('document-open'), 'Open', self.interface)
        self.fileOpen.setToolTip('Open (Ctrl+O)')
        self.fileOpen.triggered.connect(self.interface.filemanager.open)
        self.fileOpen.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.toolbar.addAction(self.fileOpen)

        self.fileSave = QAction(QIcon.fromTheme('document-save'), 'Save', self.interface)
        self.fileSave.setToolTip('Save (Ctrl+S)')
        self.fileSave.triggered.connect(self.interface.filemanager.save)
        self.fileSave.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.toolbar.addAction(self.fileSave)

        self.fileSaveAs = QAction(QIcon.fromTheme('document-save-as'), 'Save As', self.interface)
        self.fileSaveAs.setToolTip('Save As (Ctrl+Shift+S)')
        self.fileSaveAs.triggered.connect(self.interface.filemanager.saveAs)
        self.fileSaveAs.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S))
        self.toolbar.addAction(self.fileSaveAs)

        self.toolbar.addSeparator()


        self.insertButton = QToolButton(self.interface)
        self.insertButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.insertButton.setIcon(QIcon.fromTheme('insert-text'))
        self.insertButton.setText('Insert')
        self.insertButton.setToolTip('Insert')
        self.insertButton.setPopupMode(QToolButton.InstantPopup)
        self.insertMenu = QMenu(self.insertButton)
        self.insertButton.setMenu(self.insertMenu)
        self.toolbar.addWidget(self.insertButton)

        self.insertConstantAction = QAction('Constant', self.interface)
        self.insertConstantAction.triggered.connect(self.insertConstant)
        self.insertConstantAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_C))
        self.insertMenu.addAction(self.insertConstantAction)

        self.insertDateAction = QAction('Date && Time', self.interface)
        self.insertDateAction.triggered.connect(self.insertDate)
        self.insertDateAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_D))
        self.insertMenu.addAction(self.insertDateAction)

        self.insertUnitAction = QAction('Unit', self.interface)
        self.insertUnitAction.triggered.connect(self.insertUnit)
        self.insertUnitAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_U))
        self.insertMenu.addAction(self.insertUnitAction)

        self.insertUnitSystemAction = QAction('Unit System', self.interface)
        self.insertUnitSystemAction.triggered.connect(self.insertUnitSystem)
        self.insertUnitSystemAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Y))
        self.insertMenu.addAction(self.insertUnitSystemAction)

        self.insertOperatorAction = QAction('Operator', self.interface)
        self.insertOperatorAction.triggered.connect(self.insertOperator)
        self.insertOperatorAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O))
        self.insertMenu.addAction(self.insertOperatorAction)

        self.insertFunctionAction = QAction('Function', self.interface)
        self.insertFunctionAction.triggered.connect(self.insertFunction)
        self.insertFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F))
        self.insertMenu.addAction(self.insertFunctionAction)

        self.insertUserDefinedFunctionAction = QAction('User-Defined Function', self.interface)
        self.insertUserDefinedFunctionAction.triggered.connect(self.insertUserDefinedFunction)
        self.insertUserDefinedFunctionAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_E))
        self.insertMenu.addAction(self.insertUserDefinedFunctionAction)


        self.executeAction = QAction(QIcon.fromTheme('media-playback-start'), 'Execute', self.interface)
        self.executeAction.setToolTip('Execute (Ctrl+Enter)')
        self.executeAction.triggered.connect(self.interface.calculatormanager.calc)
        self.toolbar.addAction(self.executeAction)
        self.executeAction.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_Enter), QKeySequence(Qt.CTRL + Qt.Key_Return)])

        self.viewClearOutput = QAction(QIcon.fromTheme('edit-clear'), 'Clear Output', self.interface)
        self.viewClearOutput.setToolTip('Clear Output (Ctrl+L)')
        self.viewClearOutput.triggered.connect(self.interface.display.clear)
        self.viewClearOutput.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        self.toolbar.addAction(self.viewClearOutput)

        self.exportResults = QAction(QIcon.fromTheme('x-office-spreadsheet'), 'Export Results', self.interface)
        self.exportResults.setToolTip('Export Results (Ctrl+E)')
        self.exportResults.triggered.connect(self.doExportResults)
        self.exportResults.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_E))
        self.toolbar.addAction(self.exportResults)

        self.toolbar.addSeparator()


        self.viewOptions = QAction(QIcon.fromTheme('preferences-other'), 'Options', self.interface)
        self.viewOptions.setToolTip('Options')
        self.viewOptions.triggered.connect(self.openOptions)
        self.toolbar.addAction(self.viewOptions)


        self.helpButton = QToolButton(self.interface)
        self.helpButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.helpButton.setIcon(QIcon.fromTheme('help-about'))
        self.helpButton.setText('Help')
        self.helpButton.setToolTip('Help')
        self.helpButton.setPopupMode(QToolButton.InstantPopup)
        self.helpMenu = QMenu(self.helpButton)
        self.helpButton.setMenu(self.helpMenu)
        self.toolbar.addWidget(self.helpButton)

        self.helpHelpAction = QAction('Calculator Reference', self.interface)
        self.helpHelpAction.triggered.connect(self.openHelp)
        self.helpMenu.addAction(self.helpHelpAction)

        self.helpAboutAction = QAction('About', self.interface)
        self.helpAboutAction.triggered.connect(self.openHelpAbout)
        self.helpMenu.addAction(self.helpAboutAction)

    def refresh(self):
        buttonConfig = self.config.main['appearance']['button_style']
        if buttonConfig == 'IconAndText':
            style = Qt.ToolButtonTextBesideIcon
        if buttonConfig == 'Icon':
            style = Qt.ToolButtonIconOnly
        if buttonConfig == 'Text':
            style = Qt.ToolButtonTextOnly
        self.toolbar.setToolButtonStyle(style)
        self.insertButton.setToolButtonStyle(style)
        self.helpButton.setToolButtonStyle(style)


    def openOptions(self):
        OptionsDialog(self.interface)

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

    def doExportResults(self):
        filename = self.interface.getSaveFileName("Export Results as CSV", "Text CSV files (*.csv)")
        if filename is not None and filename != '':
            with open(filename, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for row in self.interface.display.rawOutput:
                    if isinstance(row, CalculatorDisplayAnswer):
                        thisRow = [row.question.strip()]
                        options = self.config.main['display']
                        thisRow.append(self.interface.htmlservice.createAnswerListText(row.answer, None, options))
                        if row.unit is not None:
                            thisRow.append(self.interface.htmlservice.createUnitText(row.answer, row.unit, options).strip())
                    elif isinstance(row, CalculatorDisplayError):
                        thisRow = [self.interface.htmlservice.createQuestionErrorText(row)]
                        thisRow.append(row.err)
                    writer.writerow(thisRow)

    def openHelp(self):
        QDesktopServices.openUrl(QUrl('https://github.com/JordanL2/ModularCalculator/wiki'))

    def openHelpAbout(self):
        AboutDialog(self.interface)
