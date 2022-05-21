#!/usr/bin/python3

from modularcalculatorinterface.config import Config
from modularcalculatorinterface.gui.interface import ModularCalculatorInterface

from PyQt5.QtWidgets import QApplication

import sys


def main():
    flags = {'clear': False}
    if len(sys.argv) >= 2 and sys.argv[1] == '--clear':
        print("Will not restore state due to --clear flag")
        flags['clear'] = True
    config = Config(sys.argv)
    app = QApplication(sys.argv)
    calc = ModularCalculatorInterface(flags, config)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
