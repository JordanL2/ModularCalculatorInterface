#!/usr/bin/python3

from modularcalculatorinterface.gui.interface import ModularCalculatorInterface

from PyQt5.QtWidgets import QApplication

import sys


def main():
    clear = False
    if len(sys.argv) >= 2 and sys.argv[1] == '--clear':
        print("Will not restore state due to --clear flag")
        clear = True
    app = QApplication(sys.argv)
    calc = ModularCalculatorInterface(clear)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
