#!/usr/bin/python3

from modularcalculator.objects.items import OperandResult
from modularcalculator.objects.units import UnitPowerList
from modularcalculatorinterface.display import CalculatorDisplayAnswer, CalculatorDisplayError

import json


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
				'err': obj.err.message,
				'i': obj.i,
				'question': obj.question,
			}
		if isinstance(obj, OperandResult):
			return {
				'value': str(obj.value),
				'unit': str(obj.unit),
			}
		if isinstance(obj, UnitPowerList):
			return {
				'value': obj.singular(True, True),
			}
		return json.JSONEncoder.default(self, obj)
 

def defaultState(state, defaults):
	for k, v in defaults.items():
		if k not in state:
			state[k] = v

def maphash(mapToHash):
	string = json.dumps(mapToHash, cls=SetEncoder, sort_keys=True)
	return hash(string)
