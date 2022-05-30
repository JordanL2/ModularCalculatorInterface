#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtWidgets import QFormLayout


class DisplayTab(OptionsTab):

    def initTab(self):
        layout = QFormLayout()

        layout.addRow("Font", OptionComboBox(self, self.config.main['display'], 'font', getFixedWidthFonts()))

        self.addSpacerItem(layout)
        layout.addRow("Question font size", OptionComboBox(self, self.config.main['display'], 'question_fontsize_pt', getFontSizes(), int))
        layout.addRow("Question font bold", OptionCheckbox(self, self.config.main['display'], 'question_bold'))

        self.addSpacerItem(layout)
        layout.addRow("Answer font size", OptionComboBox(self, self.config.main['display'], 'answer_fontsize_pt', getFontSizes(), int))
        layout.addRow("Answer font bold", OptionCheckbox(self, self.config.main['display'], 'answer_bold'))

        self.addSpacerItem(layout)
        layout.addRow("Fraction font size", OptionComboBox(self, self.config.main['display'], 'fraction_fontsize_pt', getFontSizes(), int))
        layout.addRow("Fraction small font size", OptionComboBox(self, self.config.main['display'], 'fraction_small_fontsize_pt', getFontSizes(), int))
        layout.addRow("Fraction font bold", OptionCheckbox(self, self.config.main['display'], 'fraction_bold'))
        layout.addRow("Fraction maximum denominator digits", OptionSpinBox(self, self.config.main['display'], 'max_denominator_digits', 1, 50))

        self.addSpacerItem(layout)
        layout.addRow("Units in short form", OptionCheckbox(self, self.config.main['display'], 'short_units'))

        self.setLayout(layout)
