#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtWidgets import QFormLayout


class EntryTab(OptionsTab):

    def initTab(self):
        layout = QFormLayout()

        layout.addRow("Font", OptionComboBox(self, self.config.main['entry'], 'font', getFixedWidthFonts()))
        layout.addRow("Font size", OptionComboBox(self, self.config.main['entry'], 'fontsize_pt', getFontSizes(), int))
        layout.addRow("Font bold", OptionCheckbox(self, self.config.main['entry'], 'bold'))

        self.addSpacerItem(layout)
        layout.addRow("Show execution errors", OptionCheckbox(self, self.config.main['entry'], 'show_execution_errors'))
        layout.addRow("Line highlighting", OptionCheckbox(self, self.config.main['entry'], 'view_line_highlighting'))

        self.setLayout(layout)
