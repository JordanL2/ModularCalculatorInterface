#!/usr/bin/python3

from modularcalculator.modularcalculator import *
from modularcalculatorinterface.guiwidgets import ExpandedListWidget
from modularcalculatorinterface.guitools import *

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QGridLayout, QLabel, QPushButton, QLineEdit


class FeatureOptionsDialog(QDialog):
    
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.calculatormanager = self.parent.calculatormanager

        layout = QVBoxLayout()

        layout.addWidget(QLabel('Click a feature below to edit its available options.'))

        self.featureList = ExpandedListWidget(self, True, True)
        features = [f for f in self.calculatormanager.calculator.feature_list.values() if f.id() in self.calculatormanager.calculator.feature_options and f.id() in self.calculatormanager.calculator.installed_features]
        for feature in sorted(features, key=lambda f : f.title()):
            item = QListWidgetItem(feature.title(), self.featureList)
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(Qt.UserRole, feature.id())
        self.featureList.itemClicked.connect(self.openFeature)
        layout.addWidget(self.featureList)

        self.setLayout(layout)
        self.setWindowTitle('Feature Options')
        self.setVisible(True)

    def openFeature(self, item):
        featureId = item.data(Qt.UserRole)
        ConfigureFeatureDialog(self, featureId)

    def sizeHint(self):
        size = super().sizeHint()
        relSize = screenRelativeSize(0.2, 0.8)
        if size.height() < relSize.height():
            relSize.setHeight(size.height())
        return size


class ConfigureFeatureDialog(QDialog):

    def __init__(self, parent, featureId):
        super().__init__(parent)

        self.parent = parent
        self.calculator = self.parent.calculatormanager.calculator
        self.feature = self.calculator.feature_list[featureId]
        self.featureOptions = self.calculator.feature_options[featureId]

        grid = QGridLayout()

        maxI = 0
        self.fieldEditBoxes = {}
        for i, fieldAndValue in enumerate(self.featureOptions.items()):
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

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        grid.addWidget(button, maxI, 0, 1, 3)

        self.setLayout(grid)
        self.setFixedHeight(self.sizeHint().height())
        self.setWindowTitle("{} Options".format(self.feature.title()))
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

    def ok(self):
        for field, lineEdit in self.fieldEditBoxes.items():
            value = lineEdit.text()
            self.featureOptions[field] = self.decode(value)
        self.parent.parent.entry.refresh()
        self.close()

    def sizeHint(self):
        size = super().sizeHint()
        size.setWidth(QApplication.desktop().screenGeometry().width() * 0.3)
        return size
