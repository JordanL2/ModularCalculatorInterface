#!/usr/bin/python3

from modularcalculatorinterface.gui.options.common import *


class EntryTab(OptionsTab):

    def initTab(self):
        layout = FixedFormLayout()

        layout.addRow("Font", OptionComboBox(self, self.config.main['entry'], 'font', self.parent.fixedWidthFonts))
        layout.addRow("Font size", OptionComboBox(self, self.config.main['entry'], 'fontsize_pt', self.parent.fontSizes, cast=int))
        layout.addRow("Font bold", OptionCheckbox(self, self.config.main['entry'], 'bold'))

        self.addSpacerItem(layout)
        layout.addRow("Show execution errors", OptionCheckbox(self, self.config.main['entry'], 'show_execution_errors'))
        layout.addRow("Line highlighting", OptionCheckbox(self, self.config.main['entry'], 'view_line_highlighting'))

        self.addSpacerItem(layout)
        self.autoExecute = OptionCheckbox(self, self.config.main['entry'], 'autoexecute')
        layout.addRow("Auto-execute", self.autoExecute)
        self.autoExecuteDelay = OptionSpinBox(self, self.config.main['entry'], 'autoexecute_timeout', 0, 60)
        layout.addRow("Auto-execute delay", self.autoExecuteDelay)
        if self.autoExecute.checkBox.checkState() == Qt.CheckState.Unchecked:
            self.autoExecuteDelay.setDisabled(True)
        self.autoExecute.checkBox.stateChanged.connect(self.onAutoExecuteStateChanged)

        self.setLayout(layout)

    def onAutoExecuteStateChanged(self, state):
        self.autoExecuteDelay.setDisabled(self.autoExecute.checkBox.checkState() == Qt.CheckState.Unchecked)
