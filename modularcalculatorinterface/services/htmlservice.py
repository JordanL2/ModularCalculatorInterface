#!/usr/bin/python3

from modularcalculator.objects.units import *
from modularcalculator.services.syntaxhighlighter import *

import html


class HtmlService():

    def __init__(self, interface):
        self.interface = interface
        self.highlighter = SyntaxHighlighter()
        self.setTheme()
        self.initStyling()

    def setTheme(self):
        self.syntax = {
            'Light': {
                'error': "color: '#bc0000'",
                'default': "color: '#bc0000'",
                'literal': "color: '#097e00'",
                'unit': "color: '#805f00'",
                'unitsystem': "color: '#805f00'",
                'op': "color: '#0c0c0c'",
                'terminator': "color: '#0c0c0c'",
                'inner_expr_start': "color: '#0c0c0c'",
                'inner_expr_end': "color: '#0c0c0c'",
                'function_name': "color: '#00297f'",
                'function_start': "color: '#0c0c0c'",
                'function_param': "color: '#0c0c0c'",
                'function_end': "color: '#0c0c0c'",
                'ext_function_name': "color: '#00297f'",
                'variable': "color: '#480081'",
                'constant': "color: '#812500'",
                'comment': "color: '#007d80'",
            },
            'Dark': {
                'error': "color: '#cd0d0d'",
                'default': "color: '#cd2727'",
                'literal': "color: '#3ae42d'",
                'unit': "color: '#d7a40e'",
                'unitsystem': "color: '#d7a40e'",
                'op': "color: '#f2f2f2'",
                'terminator': "color: '#f2f2f2'",
                'inner_expr_start': "color: '#f2f2f2'",
                'inner_expr_end': "color: '#f2f2f2'",
                'function_name': "color: '#3577ff'",
                'function_start': "color: '#f2f2f2'",
                'function_param': "color: '#f2f2f2'",
                'function_end': "color: '#f2f2f2'",
                'ext_function_name': "color: '#3577ff'",
                'variable': "color: '#a839ff'",
                'constant': "color: '#ff6629'",
                'comment': "color: '#2ee5e9'",
            },
        }
        value = (self.interface.palette().base().color().value())
        if value < 128:
            self.theme = 'Dark'
        else:
            self.theme = 'Light'

    def initStyling(self):
        self.css = "<style>"
        for itemtype, css in self.syntax[self.theme].items():
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
            answerText = '['
            answerText += ', '.join([self.createAnswerText(r.value, r.unit, options) for r in row.answer])
            answerText += ']'
        else:
            answerText = self.createAnswerText(row.answer, row.unit, options)

        fractionText = None
        if row.fraction is not None and row.fraction[1] != 0 and row.fraction[2] < options['max_denominator']:
            fractionText = self.createFractionText(row.fraction, row.unit, options)

        return (answerText, fractionText)

    def createAnswerText(self, answer, unit, options):
        if isinstance(answer, UnitPowerList):
            if self.options['shortunits'] and answer.has_symbols():
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
        if options['shortunits'] and unit.has_symbols():
            unit_parts = unit.symbol(False)
        else:
            unit_parts = unit.get_name(answer, False)
            unit_parts = [(' ', 'space')] + unit_parts
        return ''.join([u[0] for u in unit_parts])

    def createQuestionHtml(self, expr, options):
        statements, _, _ = self.interface.calculatormanager.calculator.parse(expr, {})
        html, _ = self.createStatementsHtml(statements, '', False)
        return html

    def createAnswerFractionHtml(self, row, options):
        answerHtml = self.css
        if type(row.answer) == list:
            answerHtml += '['
            answerHtml += ', '.join([self.createAnswerHtml(r.value, r.unit, options) for r in row.answer])
            answerHtml += ']'
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
            if self.options['shortunits'] and answer.has_symbols():
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
            fractionHtml += self.makeSpan("{} ".format(fraction[0]), "literal")
            fractionHtml += self.makeSpan("{}/{}".format(abs(fraction[1]), fraction[2]), "literal", "font-size: 14px")
        else:
            fractionHtml += self.makeSpan("{}/{}".format(fraction[1], fraction[2]), "literal")
        if unit is not None:
            unit = self.createUnitHtml(Number(fraction[0] + fraction[1] / fraction[2]), unit, options)
            fractionHtml += unit
        return fractionHtml

    def createUnitHtml(self, answer, unit, options):
        if options['shortunits'] and unit.has_symbols():
            unit_parts = unit.symbol(False)
        else:
            unit_parts = unit.get_name(answer, False)
            unit_parts = [(' ', 'space')] + unit_parts
        return ''.join([self.makeSpan(self.htmlSafe(u[0]), u[1]) for u in unit_parts])
