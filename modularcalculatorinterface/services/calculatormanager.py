#!/usr/bin/python3

from modularcalculator.modularcalculator import *
from modularcalculator.objects.exceptions import *
from modularcalculator.objects.number import *


class CalculatorManager():

    def __init__(self, interface):
        self.interface = interface
        self.config = self.interface.config
        self.entry = self.interface.entry
        self.display = self.interface.display
        self.initCalculator()

    def initCalculator(self):
        self.setCalculator(CalculatorManager.createCalculator(self.config.main))

    def createCalculator(config):
        calculator = ModularCalculator()
        calculator.enable_units()
        calculator.number_prec_set(config['execution']['precision'])
        calculator.number_set_rounding(config['execution']['rounding'])
        calculator.unit_simplification_set(config['execution']['simplify_units'])

        if 'features' in config and 'external' in config['features']:
            for featureFile in config['features']['external']:
                try:
                    calculator.import_feature_file(featureFile)
                except Exception as err:
                    print("!!! Couldn't import {} - {} !!!".format(featureFile, err))

        if 'features' in config and 'installed' in config['features']:
            calculator.install_features(config['features']['installed'], False, True)
        else:
            calculator.load_preset('Computing')

        if 'feature_options' in config:
            for featureId, featureOptions in config['feature_options'].items():
                calculator.feature_options[featureId] = featureOptions

        if 'unit_system_preference' in config['execution']:
            calculator.unit_normaliser.systems_preference = config['execution']['unit_system_preference']

        return calculator

    def setCalculator(self, calculator):
        self.calculator = calculator
        self.entry.setCalculator(self.calculator)

    def updateInsertOptions(self):
        self.interface.menu.insertConstantAction.setVisible('state.constants' in self.calculator.installed_features)
        self.interface.menu.insertDateAction.setVisible('dates.dates' in self.calculator.installed_features)
        self.interface.menu.insertUnitAction.setVisible('units.units' in self.calculator.installed_features)
        self.interface.menu.insertOperatorAction.setVisible('structure.operators' in self.calculator.installed_features)
        self.interface.menu.insertFunctionAction.setVisible('structure.functions' in self.calculator.installed_features)
        self.interface.menu.insertUserDefinedFunctionAction.setVisible('structure.externalfunctions' in self.calculator.installed_features)

    def calc(self):
        question = self.entry.getContents().rstrip()
        response = None
        err = None
        pos = None
        try:
            self.calculator.vars = {}
            response = self.calculator.calculate(question)
        except CalculatingException as theErr:
            err = theErr
            pos = err.find_pos(question)
            response = err.response
        if response is not None:
            self.display.clear()
            for i, result in enumerate(response.results):
                if result.has_result():
                    result_value = result.value
                    result_fraction = None
                    if isinstance(result.value, Number):
                        result_fraction = result_value.as_fraction()
                    self.display.addAnswer(result.expression, result_value, result_fraction, result.unit)
        if err is not None:
            self.display.addError(err, pos, question)
        self.display.refresh()

    def setInstalledFeatures(self, calculator, importedFeatures):
        if 'features' not in self.config.main:
            self.config.main['features'] = {}
        self.config.main['features']['installed'] = list(calculator.installed_features)
        self.config.main['features']['external'] = importedFeatures
        self.config.saveMainConfig()
        self.initCalculator()
        self.refresh()
        self.updateInsertOptions()

    def setFeatureOptions(self, featureId, featureOptions):
        if 'feature_options' not in self.config.main:
            self.config.main['feature_options'] = {}
        self.config.main['feature_options'][featureId] = featureOptions
        self.config.saveMainConfig()
        self.initCalculator()
        self.refresh()

    def refresh(self):
        self.interface.tabmanager.forceRefreshAllTabs()
        self.interface.entry.refresh()
        self.interface.display.refresh()
