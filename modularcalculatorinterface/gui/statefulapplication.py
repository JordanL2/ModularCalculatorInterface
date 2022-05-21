#!/usr/bin/python3

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow

import pickle


class StatefulApplication(QMainWindow):

    def __init__(self):
        super().__init__()
        self.settings = QSettings('ModularCalculator', 'ModularCalculator')

    def closeEvent(self, e):
        self.storeAllState()

    def restoreAllState(self):
        pass

    def storeAllState(self):
        pass

    def fetchState(self, name):
        try:
            return self.settings.value(name, "").encode("utf-8")
        except Exception:
            return self.settings.value(name, "")

    def storeState(self, name, value):
        self.settings.setValue(name, value)

    def fetchStateText(self, name, default=None):
        if self.fetchState(name) is None:
            return default
        return self.fetchState(name).decode('utf-8')

    def storeStateText(self, name, value):
        self.storeState(name, value)

    def fetchStateNumber(self, name, default=None):
        if self.fetchState(name) is None:
            return None
        num = self.fetchState(name).decode('utf-8')
        if num == "":
            return default
        else:
            return int(num)

    def storeStateNumber(self, name, value):
        self.storeState(name, value)

    def fetchStateBoolean(self, name, default=None):
        boolean = self.fetchState(name).decode('utf-8')
        if boolean == 'true':
            return True
        elif boolean == 'false':
            return False
        else:
            return default

    def storeStateBoolean(self, name, value):
        self.storeState(name, value)

    def fetchStateArray(self, name):
        try:
            return pickle.loads(self.fetchState(name))
        except Exception:
            return []

    def storeStateArray(self, name, value):
        self.storeState(name, pickle.dumps(value))

    def fetchStateMap(self, name):
        try:
            return pickle.loads(self.fetchState(name))
        except Exception:
            return {}

    def storeStateMap(self, name, value):
        self.storeState(name, pickle.dumps(value))
