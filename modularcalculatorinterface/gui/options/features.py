#!/usr/bin/python3

from modularcalculator.modularcalculator import *
from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QGridLayout, QListWidgetItem, QListWidget, QComboBox, QPushButton, QFileDialog, QMessageBox, QScrollArea, QCheckBox, QSizePolicy, QDialog, QLineEdit

from functools import partial


class FeaturesTab(OptionsTab):

    def initTab(self):
        self.calculatormanager = self.interface.calculatormanager

        self.importedFeatures = []
        if 'features' in self.config.main and 'external' in self.config.main['features']:
            self.importedFeatures = self.config.main['features']['external']
        self.featureOptions = self.calculatormanager.calculator.feature_options
        self.calculator = self.buildCalculator(self.calculatormanager.calculator.installed_features)

        grid = QGridLayout()

        self.presetList = QComboBox(self)
        self.presetList.addItem('- Presets -')
        self.presetList.addItem('Select All')
        self.presetList.addItem('Select None')
        self.presetList.addItems(self.calculator.preset_list.keys())
        self.presetList.currentTextChanged.connect(self.selectPreset)
        grid.addWidget(self.presetList, 0, 0, 1, 2)

        self.featureList = FeatureList(self)
        scrollableWidgetList = ScrollableWidgetList(self.featureList)
        self.featureList.scrollableWidgetList = scrollableWidgetList
        grid.addWidget(scrollableWidgetList, 1, 0, 1, 2)
        grid.setRowStretch(1, 1)

        importedFileLabel = QLabel("External Feature Files")
        importedFileLabelFont = QFontDatabase.systemFont(QFontDatabase.TitleFont)
        importedFileLabelFont.setBold(True)
        importedFileLabel.setFont(importedFileLabelFont)
        importedFileLabel.setAlignment(Qt.AlignHCenter)
        grid.addWidget(importedFileLabel, 2, 0, 1, 2)

        addFileButton = QPushButton("Add", self)
        addFileButton.clicked.connect(self.addFile)
        grid.addWidget(addFileButton, 3, 0, 1, 1)
        removeFileButton = QPushButton("Remove", self)
        removeFileButton.clicked.connect(self.removeFile)
        grid.addWidget(removeFileButton, 3, 1, 1, 1)

        self.importedFileList = QListWidget(self)
        self.refreshImportedFiles()
        grid.addWidget(self.importedFileList, 4, 0, 1, 2)

        self.setLayout(grid)
        self.featureList.refresh()

        self.applyTimer = None

    def refreshImportedFiles(self):
        self.importedFileList.clear()
        self.importedFileList.addItems(self.importedFeatures)

    def refreshAvailableFeatures(self):
        self.calculator = self.buildCalculator()
        self.featureList.refresh()

    def selectPreset(self, text):
        toSelect = None
        if text == 'Select All':
            toSelect = self.featureList.selected().keys()
        elif text == 'Select None':
            toSelect = []
        elif text in self.calculator.preset_list:
            toSelect = self.calculator.preset_list[text]
        if toSelect is not None:
            for featureId in self.featureList.selected().keys():
                self.featureList.setChecked(featureId, featureId in toSelect)
        self.presetList.setCurrentIndex(0)

    def addFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select Feature File", "", "All Files (*)")
        if filePath:
            self.importedFeatures.append(filePath)
            self.refreshImportedFiles()
            self.refreshAvailableFeatures()

    def removeFile(self):
        for selectedItem in self.importedFileList.selectedItems():
            self.importedFeatures.remove(selectedItem.text())
        self.refreshImportedFiles()
        self.refreshAvailableFeatures()

    def buildCalculator(self, selectedFeatures=None):
        calculator = ModularCalculator()
        calculator.enable_units()
        for importedFeature in self.importedFeatures:
            calculator.import_feature_file(importedFeature)

        if selectedFeatures is None:
            selectedFeatures = []
            for featureId, selected in self.featureList.selected().items():
                if selected:
                    selectedFeatures.append(featureId)
        selectedFeatures = [f for f in selectedFeatures if f in calculator.feature_list]

        calculator.install_features(selectedFeatures, False)

        calculator.feature_options = self.featureOptions

        return calculator

    def applyLater(self):
        if self.applyTimer is not None:
            self.applyTimer.stop()
        self.applyTimer = QTimer(self)
        self.applyTimer.setSingleShot(True)
        self.applyTimer.start(0)
        self.applyTimer.timeout.connect(self.apply)

    def apply(self):
        calculator = self.buildCalculator()
        try:
            self.calculatormanager.setInstalledFeatures(calculator, self.importedFeatures)
            self.calculator = calculator
        except Exception:
            errorMessage = QMessageBox(self.interface)
            errorMessage.setText("Could not instantiate calculator with selected features")
            errorMessage.exec()
            print(traceback.format_exc())

    def applyFeatureOptions(self, featureId, featureOptions):
        self.featureOptions[featureId] = featureOptions
        self.calculator = self.buildCalculator()
        self.calculatormanager.setFeatureOptions(featureId, featureOptions)


class ScrollableWidgetList(QScrollArea):

    def __init__(self, widget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(widget)
        self.widget().setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)
        scrollBar = self.verticalScrollBar()


class WidgetList(QWidget):

    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self.grid = QGridLayout()
        self.setLayout(self.grid)

    def addHeader(self, header):
        i = self.grid.rowCount()
        widget = QLabel(header)
        font = QFontDatabase.systemFont(QFontDatabase.TitleFont)
        font.setBold(True)
        widget.setFont(font)
        self.grid.addWidget(widget, i, 0, 1, self.columns)

    def addSpacer(self):
        i = self.grid.rowCount()
        widget = QLabel("")
        self.grid.addWidget(widget, i, 0, 1, self.columns)

    def addRow(self, widgets):
        i = self.grid.rowCount()
        for w, widget in enumerate(widgets):
            self.grid.addWidget(widget, i, w, 1, 1)

    def clear(self):
        self.clearLayout(self.grid)

    def clearLayout(self, layout):
        while True:
            item = layout.takeAt(0)
            if item is None:
                break
            if item.widget() is not None:
                widget = item.widget()
                widget.deleteLater()
            if item.layout() is not None:
                childLayout = item.layout()
                self.clearLayout(childLayout)


class FeatureList(WidgetList):

    def __init__(self, parent):
        super().__init__(4)
        self.parent = parent
        self.scrollableWidgetList = None
        self.checkBoxes = {}
        self.configButtons = {}

    def clear(self):
        super().clear()
        self.checkBoxes = {}
        self.configButtons = {}

    def refresh(self):
        self.clear()

        featuresWithConfigIds = []
        featuresByCategory = {}
        for featureId, feature in self.parent.calculator.feature_list.items():
            featureCategory = feature.category()
            if featureCategory not in featuresByCategory:
                featuresByCategory[featureCategory] = []
            featuresByCategory[featureCategory].append(feature)
            if feature.default_options() is not None:
                featuresWithConfigIds.append(featureId)

        selectedFeatures = self.parent.calculator.installed_features
        for featureCategory, features in sorted(featuresByCategory.items(), key=lambda c: c[0].lower()):
            self.addHeader(featureCategory)
            for feature in sorted(features, key=lambda f : f.title().lower()):
                featureId = feature.id()
                featureInstalled = featureId in selectedFeatures and not issubclass(feature, MetaFeature)
                featureHasConfig = featureId in featuresWithConfigIds
                self.addRow(featureId, featureInstalled, feature.title(), feature.desc(), featureHasConfig)

            self.addSpacer()

    def addRow(self, featureId, checked, name, description, hasConfig):
        widgets = []

        checkBox = QCheckBox(self)
        checkBox.setCheckState(checked * 2)
        checkBox.stateChanged.connect(partial(self.checked, featureId, checkBox))
        self.checkBoxes[featureId] = checkBox
        widgets.append(checkBox)

        nameWidget = QLabel(name)
        widgets.append(nameWidget)

        descriptionWidget = QLabel(description)
        widgets.append(descriptionWidget)

        configButton = QPushButton(QIcon.fromTheme("preferences-other"), None, self)
        nameWidget.setMinimumHeight(configButton.sizeHint().height())
        if hasConfig:
            configButton.clicked.connect(partial(self.configPressed, featureId))
            configButton.setVisible(checked)
            self.configButtons[featureId] = configButton
            widgets.append(configButton)
        else:
            configButton.deleteLater()
            widgets.append(QLabel(""))

        super().addRow(widgets)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 1)
        self.grid.setColumnStretch(3, 0)

    def checked(self, featureId, checkBox):
        if featureId in self.configButtons:
            self.configButtons[featureId].setVisible(checkBox.isChecked())
        self.checkDependencies(featureId)

    def setChecked(self, featureId, checked):
        self.checkBoxes[featureId].blockSignals(True)
        self.checkBoxes[featureId].setCheckState(checked * 2)
        self.checkBoxes[featureId].blockSignals(False)
        if featureId in self.configButtons:
            self.configButtons[featureId].setVisible(checked)
        self.checkDependencies(featureId)

    def checkDependencies(self, featureId):
        selected = self.selected(featureId)
        feature = self.parent.calculator.feature_list[featureId]
        if selected:
            if issubclass(feature, MetaFeature):
                for subfeatureId in feature.subfeatures():
                    if not self.selected(subfeatureId):
                        self.setChecked(subfeatureId, True)
                self.setChecked(featureId, False)
            else:
                for dependencyFeatureId in feature.dependencies():
                    if not self.selected(dependencyFeatureId):
                        self.setChecked(dependencyFeatureId, True)
        else:
            for checkFeatureId, checkFeature in self.parent.calculator.feature_list.items():
                if featureId in checkFeature.dependencies():
                    if self.selected(checkFeatureId):
                        self.setChecked(checkFeatureId, False)
        self.parent.applyLater()

    def selected(self, featureId=None):
        if featureId is not None:
            return self.checkBoxes[featureId].isChecked()
        status = {}
        for featureId, checkBox in self.checkBoxes.items():
            status[featureId] = checkBox.isChecked()
        return status

    def configPressed(self, featureId):
        ConfigureFeatureDialog(self.parent, self.parent.calculatormanager, self.parent.calculator, featureId)


class ConfigureFeatureDialog(QDialog):

    def __init__(self, parent, calculatormanager, calculator, featureId):
        super().__init__(parent)

        self.parent = parent
        self.calculatormanager = calculatormanager
        self.calculator = calculator
        self.feature = self.calculator.feature_list[featureId]

        grid = QGridLayout()

        maxI = 0
        self.fieldEditBoxes = {}
        for i, fieldAndValue in enumerate(self.calculator.feature_options[featureId].items()):
            fieldName = fieldAndValue[0]
            fieldValue = self.encode(fieldAndValue[1])
            lineEdit = QLineEdit(fieldValue, self)
            self.fieldEditBoxes[fieldName] = lineEdit
            grid.addWidget(QLabel(fieldName), i, 0, 1, 1)
            grid.addWidget(QLabel(   ), i, 1, 1, 1)
            grid.addWidget(lineEdit, i, 2, 1, 1)
            maxI = i
        maxI += 1

        button = QPushButton("Reset", self)
        button.clicked.connect(self.reset)
        grid.addWidget(button, maxI, 0, 1, 3)
        maxI += 1

        self.setLayout(grid)
        self.setFixedHeight(self.sizeHint().height())
        self.setWindowTitle("{} Options".format(self.feature.title()))
        self.setModal(True)
        self.setVisible(True)

    def encode(self, value):
        value = value.replace("\\", "\\\\")
        value = value.replace("\n", r'\n')
        value = value.replace("\t", r'\t')
        return value

    def decode(self, value):
        newchars = []
        skipNext = False
        for i in range(0, len(value)):
            if skipNext:
                skipNext = False
                continue
            c = value[i]
            if c == "\\" and i < len(value) - 1:
                skipNext = True
                cc = value[i + 1]
                if cc == 'n':
                    newchars.append("\n")
                elif cc == 't':
                    newchars.append("\t")
                elif cc == "\\":
                    newchars.append(c)
                else:
                    newchars.append(c)
                    newchars.append(cc)
            else:
                newchars.append(c)
        newvalue = ''.join(newchars)
        return newvalue

    def reset(self):
        for field, value in self.calculator.feature_list[self.feature.id()].default_options().items():
            self.fieldEditBoxes[field].setText(self.encode(value))

    def closeEvent(self, e):
        fields = {}
        for field, lineEdit in self.fieldEditBoxes.items():
            value = lineEdit.text()
            fields[field] = self.decode(value)
        self.parent.applyFeatureOptions(self.feature.id(), fields)
        super().closeEvent(e)
