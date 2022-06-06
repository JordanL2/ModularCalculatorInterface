#!/usr/bin/python3

from modularcalculatorinterface.gui.guiwidgets import limitToScreen

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtWidgets import QWidget, QCheckBox, QComboBox, QSpinBox, QAbstractItemView, QListView, QGridLayout, QSpacerItem
from PyQt5.QtGui import QFont, QFontDatabase


def getFixedWidthFonts():
    fonts = []
    for f in QFontDatabase().families():
        font = QFont(f)
        font.setFixedPitch(True)
        if font.exactMatch():
            fonts.append(f)
    return fonts

def getFontSizes():
    return [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            22, 24, 26, 28, 32, 48, 64, 72, 80, 96, 128]


class OptionsTab(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.interface = parent.interface
        self.config = parent.config
        self.initTab()

    def addSpacerItem(self, layout):
        layout.addItem(QSpacerItem(0, 10))


class OptionCheckbox(QWidget):

    def __init__(self, parent, config_toplevel, config_secondlevel):
        super().__init__(parent)

        self.checkBox = QCheckBox()
        grid = QGridLayout()
        grid.addWidget(self.checkBox, 0, 0)
        grid.setContentsMargins(0, 3, 0, 0)
        self.setLayout(grid)

        self.interface = parent.interface
        self.config_toplevel = config_toplevel
        self.config_secondlevel = config_secondlevel
        self.checkBox.setCheckState(self.config_toplevel[self.config_secondlevel] * 2)
        self.checkBox.stateChanged.connect(self.onStateChanged)

    def onStateChanged(self, state):
        self.config_toplevel[self.config_secondlevel] = state > 0
        self.interface.applyConfig()


class OptionComboBox(QComboBox):

    def __init__(self, parent, config_toplevel, config_secondlevel, options, ids=None, cast=None):
        super().__init__(parent)
        self.interface = parent.interface
        self.config_toplevel = config_toplevel
        self.config_secondlevel = config_secondlevel
        self.cast = cast

        self.optionMap = None
        if ids is not None:
            self.optionMap = {}

        currentValue = self.config_toplevel[self.config_secondlevel]
        selected = None
        for i, option in enumerate(options):
            if ids is not None:
                optionId = ids[i]
                self.optionMap[str(option)] = optionId
                self.addItem(str(option), optionId)
                if ids[i] == self.config_toplevel[self.config_secondlevel]:
                    selected = i
            else:
                self.addItem(str(option))
                if option == self.config_toplevel[self.config_secondlevel]:
                    selected = i
        self.setCurrentIndex(selected)

        self.currentTextChanged.connect(self.onStateChanged)

    def onStateChanged(self, option):
        if self.optionMap is not None:
            option = self.optionMap[option]
        if self.cast is not None:
            option = self.cast(option)
        self.config_toplevel[self.config_secondlevel] = option
        self.interface.applyConfig()


class OptionSpinBox(QSpinBox):

    def __init__(self, parent, config_toplevel, config_secondlevel, minimum, maximum):
        super().__init__(parent)
        self.interface = parent.interface
        self.config_toplevel = config_toplevel
        self.config_secondlevel = config_secondlevel
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(self.config_toplevel[self.config_secondlevel])
        self.valueChanged.connect(self.onStateChanged)

    def onStateChanged(self, i):
        self.config_toplevel[self.config_secondlevel] = i
        self.interface.applyConfig()


class SortableListModel(QStringListModel):

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        return super().flags(index)


class OptionSortableList(QListView):

    def __init__(self, parent, config_toplevel, config_secondlevel, items, cast=None):
        super().__init__(parent)
        self.interface = parent.interface
        self.config_toplevel = config_toplevel
        self.config_secondlevel = config_secondlevel
        self.cast = cast

        self.stringModel = SortableListModel()
        self.stringModel.setStringList(items)
        self.setModel(self.stringModel)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, e):
        super().dropEvent(e)
        stringList = self.stringModel.stringList()
        if self.cast is not None:
            stringList = self.cast(stringList)
        self.config_toplevel[self.config_secondlevel] = stringList
        self.interface.applyConfig()

    def sizeHint(self):
        return QSize(self.sizeHintForColumn(0) + 10, self.sizeHintForRow(0) * self.model().rowCount() + 10)
