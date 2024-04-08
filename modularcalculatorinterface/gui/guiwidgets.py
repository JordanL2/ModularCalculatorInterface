#!/usr/bin/python3

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QGuiApplication
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QVBoxLayout, \
                            QDialog, QPushButton, QCalendarWidget, QTimeEdit, QComboBox, QTabBar, \
                            QWidget, QGridLayout, QLineEdit


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
                item.setData(Qt.ItemDataRole.UserRole, itemText)
        elif isinstance(items, dict):
            for itemId, itemText in items.items():
                item = QListWidgetItem(itemText, self.list)
                item.setData(Qt.ItemDataRole.UserRole, itemId)
        else:
            raise Exception("Invalid type of items")
        self.list.itemDoubleClicked.connect(self.ok)
        layout.addWidget(self.list)

        button = QPushButton("OK", self)
        button.clicked.connect(self.ok)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(400, 400))
        self.setVisible(True)

    def ok(self):
        self.okFunction(self.list.currentItem().data(Qt.ItemDataRole.UserRole))
        self.close()


class CategorisedSelectionDialog(QDialog):

    def __init__(self, parent, title, items, descriptions, okFunction):
        super().__init__(parent)

        self.okFunction = okFunction

        self.items = items
        self.descriptions = descriptions

        layout = QVBoxLayout()

        self.category = QComboBox(self)
        self.items['All'] = [vv for v in self.items.values() for vv in v]
        self.category.addItems(['All'])
        self.category.addItems(sorted([k for k in self.items.keys() if k != 'All'], key=str))
        layout.addWidget(self.category)

        self.search = QLineEdit()
        self.search.textChanged.connect(self.setList)
        layout.addWidget(self.search)

        self.list = QListWidget(self)
        self.list.itemDoubleClicked.connect(self.ok)
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
        self.setMinimumSize(QSize(1000, 700))
        self.setVisible(True)
        self.search.setFocus(Qt.FocusReason.PopupFocusReason)

    def setList(self):
        listItems = sorted(self.items[self.category.currentText()], key=lambda u: str(u).lower())
        searchText = self.search.text()
        if searchText != '':
            listItems = [l for l in listItems if searchText in l]
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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Down and self.search.hasFocus():
            self.list.setFocus(Qt.FocusReason.OtherFocusReason)
            self.list.setCurrentRow(0)
        elif e.key() == Qt.Key.Key_Up and self.list.hasFocus() and self.list.currentRow() == 0:
            self.search.setFocus(Qt.FocusReason.OtherFocusReason)
        else:
            super().keyPressEvent(e)


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


class TabBarWithPlus(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.tabbar = MiddleClickCloseableTabBar(self)
        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(5, 0, 5, 5)
        layout.addWidget(self.tabbar, 0, 0, 1, 1)
        layout.setColumnStretch(0, 1)

        self.fileNew = NewTabButton('+', self.tabbar)
        self.fileNew.setToolTip('New (Ctrl+N)')
        self.fileNew.setShortcut(QKeySequence("Ctrl+n"))
        layout.addWidget(self.fileNew, 0, 1, 1, 1)
        layout.setColumnStretch(1, 0)

        self.setLayout(layout)


class NewTabButton(QPushButton):

    def __init__(self, text, tabbar):
        super().__init__(text)
        self.tabbar = tabbar


class MiddleClickCloseableTabBar(QTabBar):

    def __init__(self, parent):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.tabCloseRequested.emit(self.tabAt(event.pos()))
        else:
            super().mouseReleaseEvent(event)
