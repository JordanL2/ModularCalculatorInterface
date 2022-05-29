#!/usr/bin/python3

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

    def setTheme(self, theme):
        self.config.main['appearance']['theme'] = theme
        self.config.saveMainConfig()
        self.initStyling()
        self.interface.tabmanager.forceRefreshAllTabs()
        self.interface.entry.refresh()
        self.interface.display.refresh()

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

    def createStatementsHtml(self, statements, errorExpr, lineHighlighting=False):
        splitStatements = []
        for items in statements:
            funcItems = [i for i, item in enumerate(items) if item.functional() and not item.text.strip() == '']
            if len(funcItems) == 0:
                splitStatements.append(items)
            else:
                nonEmptyItems = [i for i, item in enumerate(items) if not item.text.strip() == '']
                firstNonEmptyItem = min(nonEmptyItems)
                if firstNonEmptyItem > 0:
                    splitStatements.append(items[0:firstNonEmptyItem])
                splitStatements.append(items[firstNonEmptyItem:])

        compactedStatements = []
        foundFunctional = False
        for items in splitStatements:
            functional = len(functional_items(items)) > 0
            isEmpty = len([i for i in items if i.text.strip() != '']) == 0
            if not isEmpty and foundFunctional:
                foundFunctional = False
                compactedStatements.append([])
            if len(compactedStatements) == 0:
                compactedStatements.append([])
            compactedStatements[-1].extend(items)
            if functional:
                foundFunctional = True

        newhtml = self.css

        highlightStatements = self.highlighter.highlight_statements(compactedStatements)
        alternate = True
        p = 0
        highlightPositions = []
        for highlightItems in highlightStatements:
            alternate = not alternate
            p0 = p

            for item in highlightItems:
                style = item[0]
                text = item[1]
                newhtml += self.makeSpan(self.htmlSafe(text), style)
                p += len(text)

            if alternate and lineHighlighting:
                highlightPositions.append((p0, p))

        if errorExpr != '':
            newhtml += self.makeSpan(self.htmlSafe(errorExpr), 'error')

        return newhtml, highlightPositions

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
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < options['max_denominator']:
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
        except ParsingException:
            return expr
        html, _ = self.createStatementsHtml(statements, '', False)
        return html

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
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < options['max_denominator']:
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
