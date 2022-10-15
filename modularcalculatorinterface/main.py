#!/usr/bin/python3

from modularcalculatorinterface.config import Config
from modularcalculatorinterface.gui.interface import ModularCalculatorInterface

from PyQt6.QtWidgets import QApplication

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(prog='modularcalculator')
    parser.add_argument('--clear', action='store_true', help='Clear the application state')
    args = parser.parse_args()

    config = Config(sys.argv)
    app = QApplication(sys.argv)
    calc = ModularCalculatorInterface(args, config)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
