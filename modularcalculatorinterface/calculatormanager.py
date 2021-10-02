#!/usr/bin/python3

from modularcalculator.modularcalculator import *
from modularcalculator.objects.exceptions import *
from modularcalculatorinterface.tools import *

from PyQt5.QtWidgets import  QMessageBox


class CalculatorManager():

    def __init__(self, interface):
        self.interface = interface
        self.entry = self.interface.entry
        self.display = self.interface.display
        self.initCalculator()


    def initCalculator(self):
        calculator = ModularCalculator()
        calculator.enable_units()
        self.setCalculator(calculator)

    def setCalculator(self, calculator):
        self.calculator = calculator
        self.entry.setCalculator(self.calculator)

    def importFeature(self, filePath):
        try:
            featureIds = self.calculator.import_feature_file(filePath)
            self.importedFeatures.append(filePath)
        except Exception as err:
            return e

    def replaceCalculator(self, calculator):
        calculator.number_prec_set(self.calculator.number_prec_get())
        calculator.unit_simplification_set(self.calculator.unit_simplification_get())
        calculator.unit_normaliser.systems_preference = self.calculator.unit_normaliser.systems_preference
        for featureId, featureOptions in self.calculator.feature_options.items():
            if featureId in calculator.feature_options:
                calculator.feature_options[featureId] = featureOptions
        self.setCalculator(calculator)
        self.updateInsertOptions()

    def updateInsertOptions(self):
        self.interface.insertConstantAction.setVisible('state.constants' in self.calculator.installed_features)
        self.interface.insertDateAction.setVisible('dates.dates' in self.calculator.installed_features)
        self.interface.insertUnitAction.setVisible('units.units' in self.calculator.installed_features)
        self.interface.insertOperatorAction.setVisible('structure.operators' in self.calculator.installed_features)
        self.interface.insertFunctionAction.setVisible('structure.functions' in self.calculator.installed_features)
        self.interface.insertUserDefinedFunctionAction.setVisible('structure.externalfunctions' in self.calculator.installed_features)

    def initEmptyState(self):
        self.importedFeatures = []
        self.calculator.load_preset('Computing')
        self.setPrecision(30)
        self.setUnitSimplification(True)
        self.setAutoExecute(True, False)
        self.setShortUnits(False)

    def restoreState(self, state):
        defaultState(state, {
                "importedFeatures": [],
                "calculatorFeatures": None,
                "precision": 30,
                "simplifyUnits": True,
                "unitSystemsPreference": None,
                "calculatorFeatureOptions": {},
                "viewSyntaxParsingAutoExecutes": True,
                "viewShortUnits": False,
            })

        self.importedFeatures = state["importedFeatures"]
        foundImportedFeatures = []
        for featureFile in self.importedFeatures:
            try:
                self.calculator.import_feature_file(featureFile)
                foundImportedFeatures.append(featureFile)
            except Exception as err:
                print("!!! Couldn't import {} - {} !!!".format(featureFile, err))
        self.importedFeatures = foundImportedFeatures

        features = state["calculatorFeatures"]
        if features is not None:
            self.calculator.install_features(features, False, True)
        else:
            self.calculator.load_preset('Computing')

        self.setPrecision(state["precision"])

        self.setUnitSimplification(state["simplifyUnits"])

        unitSystems = state["unitSystemsPreference"]
        if unitSystems is not None:
            self.calculator.unit_normaliser.systems_preference = unitSystems

        featureOptions = state["calculatorFeatureOptions"]
        for featureId, featuresOptions in featureOptions.items():
            for field, value in featuresOptions.items():
                if field in self.calculator.feature_list[featureId].default_options():
                    self.calculator.feature_options[featureId][field] = value
            
        self.setAutoExecute(state["viewSyntaxParsingAutoExecutes"], False)

        self.setShortUnits(state["viewShortUnits"], False)

    def saveState(self):
        state = {}

        state["importedFeatures"] = list(set(self.importedFeatures))

        state["calculatorFeatures"] = self.calculator.installed_features
        state["precision"] = self.interface.precisionSpinBox.spinbox.value()
        state["simplifyUnits"] = self.interface.optionsSimplifyUnits.isChecked()
        state["unitSystemsPreference"] = self.calculator.unit_normaliser.systems_preference

        state["calculatorFeatureOptions"] = self.calculator.feature_options
        
        state["viewShortUnits"] = self.interface.viewShortUnits.isChecked()
        state["viewSyntaxParsingAutoExecutes"] = self.interface.viewSyntaxParsingAutoExecutes.isChecked()

        return state


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
                    result_value = self.calculator.number_to_string(result_value)
                    self.display.addAnswer(result.expression, result_value, result.unit)
        if err is not None:
            self.display.addError(err, pos, question)
        self.display.refresh()


    def setUnitSimplification(self, value):
        self.interface.optionsSimplifyUnits.setChecked(value)
        self.calculator.unit_simplification_set(value)

    def setPrecision(self, value):
        self.interface.precisionSpinBox.spinbox.setValue(value)
        self.calculator.number_prec_set(value)

    def setShortUnits(self, value, refresh=True):
        self.interface.viewShortUnits.setChecked(value)
        self.display.options['shortunits'] = value
        if refresh:
            self.display.refresh()

    def setAutoExecute(self, value, refresh=True):
        self.interface.viewSyntaxParsingAutoExecutes.setChecked(value)
        self.entry.autoExecute = value
        if refresh:
            self.entry.refresh()

    def updateUnitSystemPreference(self, systemNames):
        self.calculator.unit_normaliser.systems_preference = [s for n in systemNames for s in [s for s in self.calculator.unit_normaliser.systems if self.calculator.unit_normaliser.systems[s].name == n]]

    def commitFeatureConfig(self, calculator, importedFeatures):
        try:
            self.replaceCalculator(calculator)
            self.importedFeatures = importedFeatures
        except Exception:
            errorMessage = QMessageBox(self.interface)
            errorMessage.setText("Could not instantiate calculator with selected features")
            errorMessage.exec()
            print(traceback.format_exc())
        self.entry.refresh()
