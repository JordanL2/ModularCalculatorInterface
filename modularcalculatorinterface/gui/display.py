#!/usr/bin/python3

from modularcalculatorinterface.gui.guiwidgets import *
from modularcalculatorinterface.services.htmlservice import *

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPalette, QFont, QTextOption
from PyQt5.QtWidgets import QTextEdit, QWidget, QGridLayout, QVBoxLayout, QSizePolicy, QSpacerItem, QFrame

import math


class CalculatorDisplay(QWidget):

    def __init__(self, interface):
        super().__init__()
        self.layout = DisplayLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.interface = interface
        self.config = self.interface.config
        self.htmlservice = interface.htmlservice

        self.initStyling()

        self.initOutput()

    def initStyling(self):
        self.colours = self.htmlservice.background
        displayScrollPalette = self.interface.displayScroll.palette()
        displayScrollPalette.setColor(QPalette.Base, self.colours[0])
        self.interface.displayScroll.setPalette(displayScrollPalette)

    def initOutput(self):
        self.rawOutput = []

    def clear(self):
        self.initOutput()
        self.refresh()

    def addAnswer(self, question, answer, fraction, unit):
        self.rawOutput.append(CalculatorDisplayAnswer(question, answer, fraction, unit))

    def addError(self, err, i, question):
        self.rawOutput.append(CalculatorDisplayError(err, i, question))

    def refresh(self):
        self.initStyling()
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
            questionHtml = self.htmlservice.createQuestionHtml(question, self.config.main['display'])
            (answerHtml, fractionHtml) = self.htmlservice.createAnswerFractionHtml(row, self.config.main['display'])
            (answerText, fractionText) = self.htmlservice.createAnswerFractionText(row, self.config.main['display'])

        elif isinstance(row, CalculatorDisplayError):
            questionHtml = self.htmlservice.createQuestionErrorHtml(row)
            answerHtml = self.htmlservice.createErrorHtml(row.err.message)
            answerText = None
            fractionHtml = None
            fractionText = None

        else:
            raise Exception("Unrecognised type in renderAnswer: {}".format(type(row)))

        return self.makeQuestionWidget(questionHtml, n), self.makeAnswerWidget(answerHtml, answerText, fractionHtml, fractionText, n)

    def makeFont(self, size, bold):
        font = QFont(self.config.main['display']['font'])
        font.setPointSize(size)
        font.setBold(bold)
        return font

    def makeQuestionWidget(self, questionHtml, n):
        questionWidget = DisplayLabel(questionHtml, n, self)
        questionWidget.setFont(self.makeFont(self.config.main['display']['question_fontsize_pt'], self.config.main['display']['question_bold']))
        return questionWidget

    def makeAnswerWidget(self, answerHtml, answerText, fractionHtml, fractionText, n):
        answerWidget = DisplayLabel(answerHtml, n, self, CalculatorDisplay.insertAnswer, answerText)

        answerWidget.setFont(self.makeFont(self.config.main['display']['answer_fontsize_pt'], self.config.main['display']['answer_bold']))

        if fractionHtml is not None:
            fractionWidget = DisplayLabel(fractionHtml, n, self, CalculatorDisplay.insertAnswer, fractionText)
            fractionWidget.setFont(self.makeFont(self.config.main['display']['fraction_fontsize_pt'], self.config.main['display']['fraction_bold']))

            return DisplayAnswerFractionLabel(answerWidget, fractionWidget)

        return answerWidget

    def insertAnswer(self, widget, e):
        self.interface.entry.insert(widget.insertText)
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

    def __init__(self, question, answer, fraction, unit):
        self.question = question
        self.answer = answer
        self.fraction = fraction
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

            pairHeight = int(math.ceil(min(max(height0, height1), self.maxHeight)))
            pair[0].setFixedHeight(pairHeight)
            pair[1].setFixedHeight(pairHeight)


class DisplayAnswerFractionLabel(QWidget):

    def __init__(self, answerLabel, fractionLabel):
        super().__init__()
        self.answerLabel = answerLabel
        self.fractionLabel = fractionLabel

        self.layout = QVBoxLayout()
        self.layout.addWidget(answerLabel)
        self.layout.addWidget(fractionLabel)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def optimumHeight(self):
        return self.answerLabel.optimumHeight() + self.fractionLabel.optimumHeight()

    def setFixedHeight(self, height):
        self.answerLabel.setFixedHeight(int(math.ceil(self.answerLabel.optimumHeight())))
        self.fractionLabel.setFixedHeight(int(math.ceil(height - self.answerLabel.optimumHeight())))

    def setVerticalScrollBarPolicy(self, policy):
        self.answerLabel.setVerticalScrollBarPolicy(policy)


class DisplayLabel(QTextEdit):

    def __init__(self, html, n, display, middleClickFunction=None, insertText=None):
        super().__init__()
        self.setHtml(html)
        self.display = display

        self.middleClickFunction = middleClickFunction
        self.insertText = insertText

        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        backgroundColor = display.colours[n % 2]
        palette = self.palette()
        palette.setColor(QPalette.Base, backgroundColor)
        self.setPalette(palette)

        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)

        self.cachedOptimumHeight = None

    def mouseReleaseEvent(self, e):
        if self.middleClickFunction is not None and e.button() == Qt.MiddleButton:
            self.middleClickFunction(self.display, self, e)
        else:
            super().mouseReleaseEvent(e)

    def optimumHeight(self):
        #TODO figure out why we need the -8 magic number
        lineWidth = self.contentsRect().width() - 8

        if self.cachedOptimumHeight is not None and self.cachedOptimumHeight[0] == lineWidth:
            return self.cachedOptimumHeight[1]

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

        self.cachedOptimumHeight = (lineWidth, height + verticalMargin)

        return height + verticalMargin
