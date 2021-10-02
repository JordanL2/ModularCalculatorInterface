#!/usr/bin/python3

from modularcalculator.modularcalculator import *
from modularcalculatorinterface.guitools import *

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import  QDialog, QWidget, QPushButton, QListWidget, QListWidgetItem, QComboBox, QFileDialog, QGridLayout, QLabel


class FeatureConfigDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.calculatormanager = self.parent.calculatormanager

        self.importedFeatures = self.calculatormanager.importedFeatures
        self.calculator = self.buildCalculator(self.importedFeatures, [])
        self.selectedFeatures = self.calculatormanager.calculator.installed_features

        grid = QGridLayout()

        self.presetList = QComboBox(self)
        self.presetList.addItem('- Presets -')
        self.presetList.addItem('Select All')
        self.presetList.addItem('Select None')
        self.presetList.addItems(self.calculator.preset_list.keys())
        self.presetList.currentTextChanged.connect(self.selectPreset)
        grid.addWidget(self.presetList, 0, 0, 1, 2)

        self.featureList = QListWidget(self)
        self.refreshFeatureList()
        self.featureList.setMinimumWidth(self.featureList.sizeHintForColumn(0))
        self.featureList.itemClicked.connect(self.itemClicked)
        self.featureList.itemChanged.connect(self.itemChanged)
        grid.addWidget(self.featureList, 1, 0, 1, 2)
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

        okButton = QPushButton("OK", self)
        okButton.clicked.connect(self.ok)
        grid.addWidget(okButton, 5, 0, 1, 2)

        self.setLayout(grid)

        self.setWindowTitle('Install/Remove Features')
        self.setVisible(True)

    def refreshFeatureList(self):
        self.featureList.blockSignals(True)

        featuresByCategory = {}
        for featureId, feature in self.calculator.feature_list.items():
            featureCategory = feature.category()
            if featureCategory not in featuresByCategory:
                featuresByCategory[featureCategory] = []
            featuresByCategory[featureCategory].append(feature)
        
        self.featureItems = {}
        self.featureList.clear()
        for featureCategory, features in sorted(featuresByCategory.items(), key=lambda c: c[0].lower()):
            categoryItem = QListWidgetItem(featureCategory, self.featureList)
            categoryFont = QFontDatabase.systemFont(QFontDatabase.TitleFont)
            categoryFont.setBold(True)
            categoryItem.setFont(categoryFont)
            categoryItem.setFlags(Qt.NoItemFlags)

            for feature in sorted(features, key=lambda f : f.title().lower()):
                featureId = feature.id()
                if feature.desc() != '':
                    featureText = "{} - {}".format(feature.title(), feature.desc())
                else:
                    featureText = feature.title()
                featureInstalled = featureId in self.selectedFeatures and not issubclass(feature, MetaFeature)

                item = QListWidgetItem(featureText, self.featureList)
                item.setCheckState(featureInstalled * 2)
                item.setFlags(Qt.ItemIsEnabled)
                item.setData(Qt.UserRole, featureId)
                self.featureItems[featureId] = item

            spacerItem = QListWidgetItem('', self.featureList)
            spacerItem.setFlags(Qt.NoItemFlags)

        self.featureList.blockSignals(False)

    def refreshImportedFiles(self):
        self.importedFileList.clear()
        self.importedFileList.addItems(self.importedFeatures)

    def buildCalculator(self, importedFeatures, features):
        calculator = ModularCalculator()
        calculator.enable_units()
        for importedFeature in importedFeatures:
            calculator.import_feature_file(importedFeature)
        calculator.install_features(features, False)
        return calculator

    def ok(self):
        featuresToInstall = []
        for featureId, item in self.featureItems.items():
            if item.checkState() == Qt.Checked:
                featuresToInstall.append(featureId)
        calculator = self.buildCalculator(self.importedFeatures, featuresToInstall)
        self.calculatormanager.commitFeatureConfig(calculator, self.importedFeatures)
        self.close()

    def itemClicked(self, item):
        if item.data(Qt.UserRole) is None:
            return
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def getItemsFeature(self, item):
        featureId = item.data(Qt.UserRole)
        if featureId is not None:
            return self.calculator.feature_list[featureId]
        return None

    def itemChanged(self, item):
        feature = self.getItemsFeature(item)
        featureId = feature.id()
        if item.checkState() == Qt.Checked:
            if issubclass(feature, MetaFeature):
                for subfeatureId in feature.subfeatures():
                    subFeatureItem = self.featureItems[subfeatureId]
                    if subFeatureItem.checkState() == Qt.Unchecked:
                        subFeatureItem.setCheckState(Qt.Checked)
                item.setCheckState(Qt.Unchecked)
            else:
                for dependencyFeatureId in feature.dependencies():
                    dependencyFeatureItem = self.featureItems[dependencyFeatureId]
                    if dependencyFeatureItem.checkState() == Qt.Unchecked:
                        dependencyFeatureItem.setCheckState(Qt.Checked)
        else:
            for checkFeatureId, checkFeature in self.calculator.feature_list.items():
                if featureId in checkFeature.dependencies():
                    checkFeatureItem = self.featureItems[checkFeatureId]
                    if checkFeatureItem.checkState() == Qt.Checked:
                        checkFeatureItem.setCheckState(0)
                
    def selectPreset(self, text):
        if text == 'Select All':
            for item in self.featureItems.values():
                if item.checkState() == Qt.Unchecked:
                    item.setCheckState(Qt.Checked)
        elif text == 'Select None':
            for item in self.featureItems.values():
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
        elif text in self.calculator.preset_list:
            for item in self.featureItems.values():
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
            for featureId in self.calculator.preset_list[text]:
                item = self.featureItems[featureId]
                if item.checkState() == Qt.Unchecked:
                    item.setCheckState(Qt.Checked)
        self.presetList.setCurrentIndex(0)

    def addFile(self):
        self.setVisible(False)
        filePath, _ = QFileDialog.getOpenFileName(self, "Select Feature File", "", "All Files (*)")
        self.setVisible(True)
        if filePath:
            self.importedFeatures.append(filePath)
            self.refreshImportedFiles()
            self.refreshAvailableFeatures()

    def removeFile(self):
        for selectedItem in self.importedFileList.selectedItems():
            self.importedFeatures.remove(selectedItem.text())
        self.refreshImportedFiles()
        self.refreshAvailableFeatures()

    def refreshAvailableFeatures(self):
        self.selectedFeatures = []
        for featureId, item in self.featureItems.items():
            if item.checkState() == Qt.Checked:
                self.selectedFeatures.append(featureId)
        self.calculator = self.buildCalculator(self.importedFeatures, [])
        self.refreshFeatureList()

    def sizeHint(self):
        return screenRelativeSize(0.4, 0.6)
