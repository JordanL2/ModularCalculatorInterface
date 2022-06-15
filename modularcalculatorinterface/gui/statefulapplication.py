#!/usr/bin/python3

from modularcalculator.objects.items import OperandResult
from modularcalculator.objects.number import *
from modularcalculator.objects.units import UnitPowerList
from modularcalculatorinterface.gui.display import CalculatorDisplayAnswer, CalculatorDisplayError

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow

import json
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

    def defaultState(self, state, defaults):
    	for k, v in defaults.items():
    		if k not in state:
    			state[k] = v

    def mapHash(self, mapToHash):
    	string = json.dumps(mapToHash, cls=SetEncoder, sort_keys=True)
    	return hash(string)


class SetEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, set):
			return sorted(list(obj))
		if isinstance(obj, list):
			return sorted(obj)
		if isinstance(obj, CalculatorDisplayAnswer):
			return {
				'question': obj.question,
				'answer': obj.answer,
				'unit': str(obj.unit),
			}
		if isinstance(obj, CalculatorDisplayError):
			return {
				'err': (obj.err if type(obj.err) == str else obj.err.message),
				'i': obj.i,
				'question': obj.question,
			}
		if isinstance(obj, OperandResult):
			return {
				'value': repr(obj.value),
				'unit': str(obj.unit),
			}
		if isinstance(obj, UnitPowerList):
			return {
				'value': obj.singular(True, True),
			}
		if isinstance(obj, Number):
			return {
				'str': repr(obj),
			}
		return json.JSONEncoder.default(self, obj)
