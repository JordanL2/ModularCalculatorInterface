#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtWidgets import QFormLayout


class AppearanceTab(OptionsTab):

    def initTab(self):
        layout = QFormLayout()

        themes = [t['name'] for t in self.config.themes.values()]
        layout.addRow("Theme", OptionComboBox(self, self.config.main['appearance'], 'theme', themes))

        self.setLayout(layout)
