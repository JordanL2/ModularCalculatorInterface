#!/usr/bin/python3

from modularcalculator.objects.items import *
from modularcalculator.objects.units import *
from modularcalculatorinterface.services.syntaxservice import *

from PyQt6.QtGui import QColor, QPalette, QGuiApplication

import html
from html.parser import HTMLParser


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
            QGuiApplication.palette().base(),
            QGuiApplication.palette().alternateBase(),
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

    def createStatementsHtml(self, statements):
        newhtml = ""

        for statement in statements:
            if statement.flatItems is None:
                statement.flatten(self.highlighter)
            if statement.text is None:
                statement.generateText()
            if statement.html is None:
                statement.generateHtml(self)
            newhtml += statement.html

        return newhtml

    def htmlToText(self, html):
        if html is None:
            return None
        f = HTMLFilter()
        f.feed(html)
        return f.text

    def createQuestionErrorText(self, row):
        questionStatements = [row.err.statements[-1].copy()]
        questionStatements[0].append(ErrorItem(row.question[row.i:]))
        return ''.join([i.text for i in questionStatements[0]])

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
        answerHtml += self.createAnswerHtml(row, options)

        fractionHtml = None
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < 10**options['max_denominator_digits']:
            fractionHtml = self.css
            fractionHtml += self.createFractionHtml(row.fraction, row.unit, options)

        return (answerHtml, fractionHtml)

    def createAnswerHtml(self, row, options):
        answer = row.value if isinstance(row, OperandResult) else row.answer
        unit = row.unit
        answerHtml = ''
        if type(answer) == list:
            if 'arrays.arrays' not in self.interface.calculatormanager.calculator.feature_options:
                return ('', '')
            answerHtml += self.makeSpan(
                self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Open'],
                'structural')
            answerHtml += "{}{}".format(
                    self.makeSpan(
                        self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Param'],
                        'structural'),
                    self.makeSpan(' ', 'whitespace')
                ).join([self.createAnswerHtml(r, options) for r in answer])
            answerHtml += self.makeSpan(
                self.interface.calculatormanager.calculator.feature_options['arrays.arrays']['Close'],
                'structural')
        else:
            if isinstance(answer, UnitPowerList):
                if options['short_units'] and answer.has_symbols():
                    unit_parts = answer.symbol(False)
                else:
                    unit_parts = answer.singular(False, False)
                answerHtml += ''.join([self.makeSpan(self.htmlSafe(u[0]), u[1]) for u in unit_parts])
            else:
                answerFormatted = self.formatNumber(answer, options)
                answerHtml += self.makeSpan(self.htmlSafe(answerFormatted), 'literal')
            if unit is not None:
                try:
                    number = self.interface.calculatormanager.calculator.number(answer)
                except CalculatorException:
                    number = Number(1)
                unitHtml = self.createUnitHtml(number, unit, options)
                answerHtml += unitHtml
        return answerHtml

    def createFractionHtml(self, fraction, unit, options):
        fractionHtml = self.css
        if fraction[0] != 0:
            fractionStyle = "font-size: {}pt".format(options['fraction_small_fontsize_pt'])
            fractionHtml += self.makeSpan("{}".format(fraction[0]), "literal")
            fractionHtml += self.makeSpan(' ', 'whitespace')
            fractionHtml += self.makeSpan(abs(fraction[1]), 'literal', fractionStyle)
            fractionHtml += self.makeSpan('/', 'structural', fractionStyle)
            fractionHtml += self.makeSpan(abs(fraction[2]), 'literal', fractionStyle)
        else:
            fractionHtml += self.makeSpan(fraction[1], 'literal')
            fractionHtml += self.makeSpan('/', 'structural')
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
            unit_parts = [(' ', 'whitespace')] + unit_parts
        return ''.join([self.makeSpan(self.htmlSafe(u[0]), u[1]) for u in unit_parts])

    def createErrorHtml(self, error):
        return self.css + self.makeSpan(self.htmlSafe(error), 'error')

    def createQuestionErrorHtml(self, row):
        questionStatements = [row.err.statements[-1].copy()]
        questionStatements[0].append(ErrorItem(row.question[row.i:]))
        questionStatements = [Statement(s) for s in questionStatements]
        questionHtml = self.createStatementsHtml(questionStatements)
        return self.css + questionHtml

    def formatNumber(self, answer, options):
        try:
            if not isinstance(answer, Number):
                return str(answer)
            calculator = self.interface.calculatormanager.calculator
            if options['number_format'] != 'Default':
                number = calculator.number(answer)
                formatter = calculator.number_types[options['number_format']]
                if formatter is not None:
                    return formatter.convert_to(calculator, number).to_string(calculator)
                return number.to_string(calculator)
            return answer.to_string(calculator)
        except CalculatorException:
            return answer


class HTMLFilter(HTMLParser):
    text = ""
    inside_tags = 0
    ignore_tags = ['style']

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            self.inside_tags += 1

    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            self.inside_tags -= 1

    def handle_data(self, data):
        if self.inside_tags == 0:
            self.text += data
