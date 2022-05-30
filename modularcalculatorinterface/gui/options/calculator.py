#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtWidgets import QFormLayout


class CalculatorTab(OptionsTab):

    def initTab(self):
        layout = QFormLayout()

        layout.addRow("Precision", OptionSpinBox(self, self.config.main['execution'], 'precision', 1, 50))
        layout.addRow("Simplify units", OptionCheckbox(self, self.config.main['execution'], 'simplify_units'))

        unitNormaliser = self.interface.calculatormanager.calculator.unit_normaliser
        unitSystems = ([unitNormaliser.systems[s].name for s in unitNormaliser.systems_preference if s in unitNormaliser.systems]
                + [unitNormaliser.systems[s].name for s in unitNormaliser.systems if s not in unitNormaliser.systems_preference])

        layout.addRow("Unit system preference", OptionSortableList(
                                            self,
                                            self.config.main['execution'], 'unit_system_preference',
                                            unitSystems,
                                            self.castUnitSystems))

        self.setLayout(layout)

    def castUnitSystems(self, systemNames):
        unitNormaliser = self.interface.calculatormanager.calculator.unit_normaliser
        return [s for n in systemNames for s in
                [s for s in unitNormaliser.systems if unitNormaliser.systems[s].name == n]
               ]
