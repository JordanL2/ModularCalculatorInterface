#!/usr/bin/python3

from modularcalculatorinterface.guitools import *
from modularcalculatorinterface.guiwidgets import *
from modularcalculator.objects.units import *

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QFontDatabase, QPalette, QTextOption, QGuiApplication
from PyQt5.QtWidgets import QTextEdit, QWidget, QGridLayout, QSizePolicy, QSpacerItem, QFrame

import math


class CalculatorDisplay(QWidget):

    def __init__(self, interface):
        super().__init__()
        self.layout = DisplayLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.interface = interface
        self.options = {}
        self.defaultStyling()
        self.initOutput()

    def defaultStyling(self):
        self.colours = [ QPalette.Base, QPalette.AlternateBase ]

    def initOutput(self):
        self.rawOutput = []

    def clear(self):
        self.initOutput()
        self.refresh()

    def addAnswer(self, question, answer, unit):
        self.rawOutput.append(CalculatorDisplayAnswer(question, answer, unit))

    def addError(self, err, i, question):
        self.rawOutput.append(CalculatorDisplayError(err, i, question))

    def refresh(self):
        self.layout.reset()

        for n, row in enumerate(self.rawOutput):
            questionWidget, answerWidget = self.renderAnswer(row, n)
            self.layout.addPair(n, questionWidget, answerWidget)

        verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer, len(self.rawOutput), 0, 1, 2, Qt.AlignTop)

        self.layout.update()

    def renderAnswer(self, row, n):
        if isinstance(row, CalculatorDisplayAnswer):
            question = row.question.strip()
            questionHtml = self.questionHtml(question)

            if type(row.answer) == list:
                answerHtml = '['
                answerHtml += ', '.join([self.renderAnswerRow(r.value, r.unit) for r in row.answer])
                answerHtml += ']'
            else:
                answerHtml = self.renderAnswerRow(row.answer, row.unit)

        elif isinstance(row, CalculatorDisplayError):
            questionHtml, _ = self.interface.entry.makeHtml([row.err.statements[-1]], row.question[row.i:])
            answerHtml = makeSpan(htmlSafe(row.err.message), 'error')

        else:
            raise Exception("Unrecognised type in renderAnswer: {}".format(type(row)))

        return self.makeQuestionWidget(questionHtml, n), self.makeAnswerWidget(answerHtml, n)

    def renderAnswerRow(self, answer, unit):
        answer_rendered = None
        if isinstance(answer, UnitPowerList):
            if self.options['shortunits'] and answer.has_symbols():
                unit_parts = answer.symbol(False)
            else:
                unit_parts = answer.singular(False, False)
            answer_rendered = ''.join([makeSpan(htmlSafe(u[0]), u[1]) for u in unit_parts])
        else:
            answer_rendered = makeSpan(htmlSafe(answer), 'literal')
        if unit is not None:
            if self.options['shortunits'] and unit.has_symbols():
                unit_parts = unit.symbol(False)
            else:
                answer_number = self.interface.calculatormanager.calculator.number(answer)[0]
                unit_parts = unit.get_name(answer_number, False)
                unit_parts = [(' ', 'space')] + unit_parts
            unit = ''.join([makeSpan(htmlSafe(u[0]), u[1]) for u in unit_parts])
        else:
            unit = ''
        return self.interface.entry.css + answer_rendered + unit

    def makeQuestionWidget(self, questionHtml, n):
        questionWidget = DisplayLabel(questionHtml, n, self)
        questionFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        questionWidget.setFont(questionFont)
        return questionWidget

    def makeAnswerWidget(self, answerHtml, n):
        answerWidget = DisplayLabel(answerHtml, n, self, CalculatorDisplay.insertAnswer)
        answerFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        answerFont.setPointSize(answerFont.pointSize() + 4)
        answerFont.setBold(True)
        answerWidget.setFont(answerFont)
        return answerWidget

    def questionHtml(self, expr):
        statements, _, _ = self.interface.calculatormanager.calculator.parse(expr, {})
        html, _ = self.interface.entry.makeHtml(statements, '')
        return html

    def insertAnswer(self, widget, e):
        self.interface.entry.insert(widget.toPlainText())
        self.interface.entry.setFocus()

    def restoreState(self, state):
        if isinstance(state, dict):
            if 'rawOutput' in state.keys():
                self.rawOutput = state['rawOutput']
        self.refresh()

    def saveState(self):
        return {'rawOutput': self.rawOutput}

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.layout is not None:
            self.layout.doResize()

class CalculatorDisplayAnswer():

    def __init__(self, question, answer, unit):
        self.question = question
        self.answer = answer
        self.unit = unit


class CalculatorDisplayError():

    def __init__(self, err, i, question):
        self.err = err
        self.i = i
        self.question = question


class DisplayLayout(QGridLayout):

    def __init__(self):
        super().__init__()
        self.displayWidgets = []
        self.maxHeight = 500

    def reset(self):
        self.displayWidgets = []
        self.clearLayout(self)

    def clearLayout(self, layout):
        while True:
            item = layout.takeAt(0)
            if item is None:
                break
            if item.widget() is not None:
                widget = item.widget()
                widget.deleteLater()
            if item.layout() is not None:
                childLayout = item.layout()
                self.clearLayout(childLayout)

    def addPair(self, n, questionWidget, answerWidget):
        self.displayWidgets.append((questionWidget, answerWidget))
        self.addWidget(questionWidget, n, 0, 1, 1)
        self.addWidget(answerWidget, n, 1, 1, 1)

    def doResize(self):
        for pair in self.displayWidgets:
            height0 = pair[0].optimumHeight()
            if height0 >= self.maxHeight:
                pair[0].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            else:
                pair[0].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            height1 = pair[1].optimumHeight()
            if height1 >= self.maxHeight:
                pair[1].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            else:
                pair[1].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            pairHeight = min(max(height0, height1), self.maxHeight)
            pair[0].setFixedHeight(pairHeight)
            pair[1].setFixedHeight(pairHeight)


class DisplayLabel(QTextEdit):

    def __init__(self, html, n, display, middleClickFunction=None):
        super().__init__()
        self.setHtml(html)
        self.display = display
        self.middleClickFunction = middleClickFunction

        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        colorRole = display.colours[n % len(display.colours)]
        backgroundColor = QGuiApplication.palette().color(colorRole)
        palette = self.palette()
        palette.setColor(QPalette.Base, backgroundColor)
        self.setPalette(palette)

        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)

    def mouseReleaseEvent(self, e):
        if self.middleClickFunction is not None and e.button() == Qt.MiddleButton:
            self.middleClickFunction(self.display, self, e)
        else:
            super().mouseReleaseEvent(e)

    def optimumHeight(self):
        #TODO figure out why we need the -8 magic number
        lineWidth = self.contentsRect().width() - 8

        textLayout = self.document().firstBlock().layout()
        textLayout.beginLayout()

        height = 0
        while (True):
            line = textLayout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(lineWidth)
            if not line.leadingIncluded():
                height += line.leading()
            line.setPosition(QPointF(0, height))
            height += line.height()
        textLayout.endLayout()
        
        #TODO should this be generated from the font?
        verticalMargin = 10

        return height + verticalMargin
