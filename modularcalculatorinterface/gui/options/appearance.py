#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *

from PyQt5.QtWidgets import QFormLayout


class AppearanceTab(OptionsTab):

    def initTab(self):
        layout = QFormLayout()

        themes = sorted([t['name'] for t in self.config.themes.values()])
        layout.addRow("Theme", OptionComboBox(self, self.config.main['appearance'], 'theme', themes))

        buttonStyles = ['IconAndText', 'Icon', 'Text']
        buttonStylesText = ['Icon and text', 'Icon only', 'Text only']
        layout.addRow("Toolbar button style", OptionComboBox(self, self.config.main['appearance'], 'button_style', buttonStylesText, ids=buttonStyles))

        self.setLayout(layout)
