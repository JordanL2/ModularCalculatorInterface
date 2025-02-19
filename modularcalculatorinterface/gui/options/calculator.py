#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *


class CalculatorTab(OptionsTab):

    def initTab(self):
        layout = FixedFormLayout()

        layout.addRow("Max number size before decimal point", OptionSpinBox(self, self.config.main['execution'], 'number_size', 1, 500))
        layout.addRow("Max number of decimal places", OptionSpinBox(self, self.config.main['execution'], 'precision', 0, 500))

        roundingOptions = ['Towards Infinity', 'Away from zero', 'To nearest, ties going away from zero', 'To nearest, ties going towards zero', 'Towards zero', 'Towards -Infinity']
        roundingOptionIds = ['ROUND_CEILING', 'ROUND_UP', 'ROUND_HALF_UP', 'ROUND_HALF_DOWN', 'ROUND_DOWN', 'ROUND_FLOOR']
        layout.addRow("Rounding", OptionComboBox(self, self.config.main['execution'], 'rounding', roundingOptions, ids=roundingOptionIds))

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
