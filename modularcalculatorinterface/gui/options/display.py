#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from inspect import signature, Parameter


class DisplayTab(OptionsTab):

    def initTab(self):
        layout = FixedFormLayout()

        layout.addRow("Font", OptionComboBox(self, self.config.main['display'], 'font', self.parent.fixedWidthFonts))

        self.addSpacerItem(layout)
        layout.addRow("Question font size", OptionComboBox(self, self.config.main['display'], 'question_fontsize_pt', self.parent.fontSizes, cast=int))
        layout.addRow("Question font bold", OptionCheckbox(self, self.config.main['display'], 'question_bold'))

        self.addSpacerItem(layout)
        layout.addRow("Answer font size", OptionComboBox(self, self.config.main['display'], 'answer_fontsize_pt', self.parent.fontSizes, cast=int))
        layout.addRow("Answer font bold", OptionCheckbox(self, self.config.main['display'], 'answer_bold'))

        self.addSpacerItem(layout)
        layout.addRow("Fraction font size", OptionComboBox(self, self.config.main['display'], 'fraction_fontsize_pt', self.parent.fontSizes, cast=int))
        layout.addRow("Fraction small font size", OptionComboBox(self, self.config.main['display'], 'fraction_small_fontsize_pt', self.parent.fontSizes, cast=int))
        layout.addRow("Fraction font bold", OptionCheckbox(self, self.config.main['display'], 'fraction_bold'))
        layout.addRow("Fraction max denominator digits", OptionSpinBox(self, self.config.main['display'], 'max_denominator_digits', 1, 50))

        self.addSpacerItem(layout)
        numberTypes = []
        for numberType in self.interface.calculatormanager.calculator.number_types:
            if hasattr(numberType, 'convert_to'):
                numberTypes.append(numberType)
        numberTypes = sorted(numberTypes, key=lambda c: c.desc().lower())
        numberFormats = ['Default'] + [c.desc() for c in numberTypes]
        numberFormatIds = ['Default'] + [c.name() for c in numberTypes]
        layout.addRow("Number format", OptionComboBox(self, self.config.main['display'], 'number_format', numberFormats, ids=numberFormatIds))

        layout.addRow("Units in short form", OptionCheckbox(self, self.config.main['display'], 'short_units'))

        self.setLayout(layout)
