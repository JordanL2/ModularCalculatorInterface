#!/usr/bin/python3

from modularcalculator.objects.items import *
from modularcalculator.objects.units import *
from modularcalculator.services.syntaxhighlighter import *

from PyQt5.QtGui import QColor, QPalette, QGuiApplication

import html


class HtmlService():

    def __init__(self, interface):
        self.interface = interface
        self.config = self.interface.config
        self.highlighter = SyntaxHighlighter()
        self.loadConfig()
        self.initStyling()

    def loadConfig(self):
        self.syntax = {}
        for themeFile, theme in self.interface.config.themes.items():
            self.syntax[theme['name']] = theme['style']

    def initStyling(self):
        self.background = [
            QGuiApplication.palette().color(QPalette.Base),
            QGuiApplication.palette().color(QPalette.AlternateBase),
        ]
        self.css = "<style>"
        for itemtype, css in self.syntax[self.config.main['appearance']['theme']].items():
            if itemtype == 'background':
                self.background[0] = QColor(css)
            elif itemtype == 'background_alt':
                self.background[1] = QColor(css)
            else:
                self.css += "span.{0} {{ {1} }}".format(itemtype, css)
        self.css += '</style>'

    def htmlSafe(self, text):
        text_escape = html.escape(str(text))
        text_escape = text_escape.replace(' ', '&nbsp;')
        text_escape = text_escape.replace("\n", '<br/>')

        return text_escape

    def makeSpan(self, text, clas=None, style=None):
        return "<span{0}{1}>{2}</span>".format(
            (" class=\"{}\"".format(clas) if clas is not None else ''),
            (" style=\"{}\"".format(style) if style is not None else ''),
            text)

    def compactStatements(self, statements):
        if len(statements) < 2:
            return statements

        compactedStatements = []

        # Combine any statements with no functional items into the previous
        # (unless first, then combine into next)
        combinePrevious = False
        for si, statement in enumerate(statements):
            if combinePrevious:
                statement.items = statements[si - 1].items + statement.items
                combinePrevious = False
            if not statement.hasFunctionalItems():
                if len(compactedStatements) > 0:
                    compactedStatements[-1].items.extend(statement.items)
                else:
                    combinePrevious = True
            else:
                compactedStatements.append(statement)
        if combinePrevious:
            compactedStatements.append(statements[-1])

        # Move any comments at the bottom of a statement into the next statement
        for si, statement in enumerate(compactedStatements):
            if si < len(compactedStatements) - 1:
                lastFunctionalItem = max(statement.functionalItems())
                nonEmptyItems = [i for i, item in enumerate(statement.items) if i > lastFunctionalItem and not item.functional() and item.text.strip() != '']
                if len(nonEmptyItems) > 0:
                    firstNonEmptyItem = min(nonEmptyItems)
                    compactedStatements[si + 1].items = statement.items[firstNonEmptyItem:] + compactedStatements[si + 1].items
                    statement.items = statement.items[0:firstNonEmptyItem]

        return compactedStatements

    def createStatementsHtml(self, statements):
        newhtml = ""

        for statement in statements:
            if statement.text is None:
                statement.generateText()
            if statement.html is None:
                statement.generateHtml(self)
            newhtml += statement.html

        return newhtml

    def createAnswerFractionText(self, row, options):
        if type(row.answer) == list:
            answerText = self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Open']
            answerText += (
                self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Param'] + ' '
            ).join([self.createAnswerText(r.value, r.unit, options) for r in row.answer])
            answerText += self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Close']
        else:
            answerText = self.createAnswerText(row.answer, row.unit, options)

        fractionText = None
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < 10**options['max_denominator_digits']:
            fractionText = self.createFractionText(row.fraction, row.unit, options)

        return (answerText, fractionText)

    def createAnswerText(self, answer, unit, options):
        if isinstance(answer, UnitPowerList):
            if options['short_units'] and answer.has_symbols():
                unit_parts = answer.symbol(False)
            else:
                unit_parts = answer.singular(False, False)
            answerText = ''.join([u[0] for u in unit_parts])
        else:
            answerText = str(answer)
        if unit is not None:
            unit = self.createUnitText(self.interface.calculatormanager.calculator.number(answer)[0], unit, options)
            answerText += unit
        return answerText

    def createFractionText(self, fraction, unit, options):
        if fraction[0] != 0:
            fractionText = "{} + {} / {}".format(fraction[0], fraction[1], fraction[2])
        else:
            fractionText = "{} / {}".format(fraction[1], fraction[2])
        if unit is not None:
            unit = self.createUnitText(Number(fraction[0] + fraction[1] / fraction[2]), unit, options)
            fractionText = "({}){}".format(fractionText, unit)
        return fractionText

    def createUnitText(self, answer, unit, options):
        if options['short_units'] and unit.has_symbols():
            unit_parts = unit.symbol(False)
        else:
            unit_parts = unit.get_name(answer, False)
            unit_parts = [(' ', 'space')] + unit_parts
        return ''.join([u[0] for u in unit_parts])

    def createQuestionHtml(self, expr, options):
        try:
            statements, _, _ = self.interface.calculatormanager.calculator.parse(expr, {})
            statements = [Statement(s) for s in statements]
        except ParsingException:
            return expr
        html = self.createStatementsHtml(statements)
        return self.css + html

    def createAnswerFractionHtml(self, row, options):
        answerHtml = self.css
        if type(row.answer) == list:
            answerHtml += self.makeSpan(
                self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Open'],
                'array_start')
            answerHtml += "{}{}".format(
                    self.makeSpan(
                        self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Param'],
                        'array_param'),
                    self.makeSpan(' ', 'space')
                ).join([self.createAnswerHtml(r.value, r.unit, options) for r in row.answer])
            answerHtml += self.makeSpan(
                self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Close'],
                'array_end')
        else:
            answerHtml += self.createAnswerHtml(row.answer, row.unit, options)

        fractionHtml = None
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < 10**options['max_denominator_digits']:
            fractionHtml = self.css
            fractionHtml += self.createFractionHtml(row.fraction, row.unit, options)

        return (answerHtml, fractionHtml)

    def createAnswerHtml(self, answer, unit, options):
        answerHtml = None
        if isinstance(answer, UnitPowerList):
            if options['short_units'] and answer.has_symbols():
                unit_parts = answer.symbol(False)
            else:
                unit_parts = answer.singular(False, False)
            answerHtml = ''.join([self.makeSpan(self.htmlSafe(u[0]), u[1]) for u in unit_parts])
        else:
            answerHtml = self.makeSpan(self.htmlSafe(answer), 'literal')
        if unit is not None:
            unit = self.createUnitHtml(self.interface.calculatormanager.calculator.number(answer)[0], unit, options)
            answerHtml += unit
        return answerHtml

    def createFractionHtml(self, fraction, unit, options):
        fractionHtml = self.css
        if fraction[0] != 0:
            fractionStyle = "font-size: {}pt".format(options['fraction_small_fontsize_pt'])
            fractionHtml += self.makeSpan("{}".format(fraction[0]), "literal")
            fractionHtml += self.makeSpan(' ', "space")
            fractionHtml += self.makeSpan(abs(fraction[1]), 'literal', fractionStyle)
            fractionHtml += self.makeSpan('/', 'op', fractionStyle)
            fractionHtml += self.makeSpan(abs(fraction[2]), 'literal', fractionStyle)
        else:
            fractionHtml += self.makeSpan(abs(fraction[1]), 'literal')
            fractionHtml += self.makeSpan('/', 'op')
            fractionHtml += self.makeSpan(abs(fraction[2]), 'literal')
        if unit is not None:
            unit = self.createUnitHtml(Number(fraction[0] + fraction[1] / fraction[2]), unit, options)
            fractionHtml += unit
        return fractionHtml

    def createUnitHtml(self, answer, unit, options):
        if options['short_units'] and unit.has_symbols():
            unit_parts = unit.symbol(False)
        else:
            unit_parts = unit.get_name(answer, False)
            unit_parts = [(' ', 'space')] + unit_parts
        return ''.join([self.makeSpan(self.htmlSafe(u[0]), u[1]) for u in unit_parts])

    def createErrorHtml(self, error):
        return self.css + self.makeSpan(self.htmlSafe(error), 'error')

    def createQuestionErrorHtml(self, row):
        questionStatements = [row.err.statements[-1].copy()]
        questionStatements[0].append(ErrorItem(row.question[row.i:]))
        questionStatements = [Statement(s) for s in questionStatements]
        questionHtml = self.createStatementsHtml(questionStatements)
        return self.css + questionHtml


class ErrorItem(Item):

    def __init__(self,  text):
        super().__init__(text)

    def isop(self):
        return False

    def desc(self):
        return 'error'

    def copy(self, classtype=None):
        copy = super().copy(classtype or self.__class__)
        copy.op = self.op
        return copy


class Statement():

    def __init__(self, items, state=None):
        self.items = items
        self.state = state
        self.text = None
        self.length = None
        self.html = None

    def generateText(self):
        self.text = ''.join([i.text for i in self.items])
        self.length = len(self.text)
        return self.text, self.length

    def generateHtml(self, htmlservice):
        highlightStatement = htmlservice.highlighter.highlight_statements([self.items])[0]
        statementHtml = ''
        for item in highlightStatement:
            style = item[0]
            text = item[1]
            statementHtml += htmlservice.makeSpan(htmlservice.htmlSafe(text), style)
        self.html = statementHtml
        return self.html

    def nonEmptyItems(self):
        return [i for i, item in enumerate(self.items) if i.text.strip() != '']

    def isEmpty(self):
        return len(self.nonEmptyItems()) > 0

    def functionalItems(self):
        return [i for i, item in enumerate(self.items) if item.functional() and not item.text.strip() == '']

    def hasFunctionalItems(self):
        return len(self.functionalItems()) > 0
