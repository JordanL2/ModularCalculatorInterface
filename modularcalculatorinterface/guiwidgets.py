#!/usr/bin/python3

from modularcalculatorinterface.guitools import *

from PyQt5.QtCore import Qt, QStringListModel, QSize
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidgetAction, QSpinBox, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QListView, QDialog, QAbstractItemView, QPushButton, QCalendarWidget, QTimeEdit, QComboBox, QTabBar


class SelectionDialog(QDialog):

    def __init__(self, parent, title, label, items, okFunction):
        super().__init__(parent)

        self.okFunction = okFunction

        layout = QVBoxLayout()

        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)

        self.list = QListWidget(self)
        if isinstance(items, list):
            for itemText in items:
                item = QListWidgetItem(itemText, self.list)
                item.setData(Qt.UserRole, itemText)
        elif isinstance(items, dict):
            for itemId, itemText in items.items():
                item = QListWidgetItem(itemText, self.list)
                item.setData(Qt.UserRole, itemId)
        else:
            raise Exception("Invalid type of items")
        layout.addWidget(self.list)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setVisible(True)

    def ok(self):
        self.okFunction(self.list.currentItem().data(Qt.UserRole))
        self.close()

    def sizeHint(self):
        return screenRelativeSize(0.3, 0.5)


class CategorisedSelectionDialog(QDialog):

    def __init__(self, parent, title, label, items, descriptions, okFunction):
        super().__init__(parent)

        self.okFunction = okFunction

        self.items = items
        self.descriptions = descriptions

        layout = QVBoxLayout()

        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)

        self.category = QComboBox(self)
        self.category.addItems(sorted(self.items.keys(), key=str))
        layout.addWidget(self.category)

        self.list = QListWidget(self)
        layout.addWidget(self.list)
        self.setList()
        self.category.currentTextChanged.connect(self.setList)
        self.list.currentTextChanged.connect(self.showDescription)

        self.itemDescription = QLabel(" \n ")
        if len(descriptions) > 0:
            layout.addWidget(self.itemDescription)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setVisible(True)

    def setList(self):
        listItems = sorted(self.items[self.category.currentText()], key=lambda u: str(u).lower())
        self.list.clear()
        self.list.addItems(listItems)

    def showDescription(self):
        if self.currentItem() is not None and self.currentItem() in self.descriptions:
            self.itemDescription.setText(self.descriptions[self.currentItem()])
        else:
            self.itemDescription.setText(" \n ")

    def currentItem(self):
        if self.list.currentItem() is None:
            return None
        return self.list.currentItem().text()

    def ok(self):
        if self.list.currentItem() is not None:
            self.okFunction(self.currentItem())
            self.close()

    def sizeHint(self):
        return screenRelativeSize(0.3, 0.5)


class SortableListModel(QStringListModel):

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        return super().flags(index)


class SortableListView(QListView):

    def sizeHint(self):
        return QSize(self.width(), self.sizeHintForRow(0) * self.model().rowCount() + 10)


class SortableListDialog(QDialog):

    def __init__(self, parent, title, label, items, okFunction):
        super().__init__(parent)

        self.okFunction = okFunction

        layout = QVBoxLayout()

        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)

        self.stringModel = SortableListModel()
        self.stringModel.setStringList(items)

        listView = SortableListView(self)
        listView.setModel(self.stringModel)
        listView.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(listView)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setVisible(True)

    def ok(self):
        self.okFunction(self.stringModel.stringList())
        self.close()


class MenuSpinBox(QWidgetAction):

    def __init__(self, parent, label, minimum, maximum):
        super().__init__(parent)
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(minimum)
        self.spinbox.setMaximum(maximum)
        labelWidget = QLabel(label)
        layout = QHBoxLayout()
        layout.addWidget(labelWidget)
        layout.addWidget(self.spinbox)
        widget = QWidget()
        widget.setLayout(layout)
        self.setDefaultWidget(widget)


class DatePicker(QDialog):

    def __init__(self, parent, title, okFunction):
        super().__init__(parent)

        self.okFunction = okFunction

        layout = QVBoxLayout()

        self.datePicker = QCalendarWidget(self)
        layout.addWidget(self.datePicker)

        self.timePicker = QTimeEdit(self)
        self.timePicker.setDisplayFormat('hh:mm:ss')
        layout.addWidget(self.timePicker)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setVisible(True)

    def ok(self):
        self.okFunction(self.datePicker.selectedDate(), self.timePicker.time())
        self.close()


class ExpandedListWidget(QListWidget):

    def __init__(self, parent, maxWidth, maxHeight):
        super().__init__(parent)

        self.maxWidth = maxWidth
        self.maxHeight = maxHeight

    def sizeHint(self):
        size = super().sizeHint()
        if self.maxWidth:
            size.setWidth(self.sizeHintForColumn(0) + 10)
        if self.maxHeight:
            size.setHeight(self.sizeHintForRow(0) * self.count() + 10)
        return size


class MiddleClickCloseableTabBar(QTabBar):

    def __init__(self, parent):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MidButton:
            self.tabCloseRequested.emit(self.tabAt(event.pos()))
        else:
            super().mouseReleaseEvent(event)
