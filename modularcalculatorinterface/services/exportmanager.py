#!/usr/bin/python3

from modularcalculator.objects.items import *
from modularcalculatorinterface.gui.display import CalculatorDisplayAnswer, CalculatorDisplayError

import csv


class ExportManager():

    def __init__(self, htmlservice):
        self.htmlservice = htmlservice

    def exportResults(self, filename, output, options):
        if filename is not None and filename != '':
            with open(filename, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for row in output:
                    if isinstance(row, CalculatorDisplayAnswer):
                        thisRow = []
                        rows = self.makeAnswers(row.question.strip(), row.answer, row.unit, 0, options)
                        for thisRow in rows:
                            writer.writerow(thisRow)
                    elif isinstance(row, CalculatorDisplayError):
                        thisRow = [self.htmlservice.createQuestionErrorText(row)]
                        thisRow.append(row.err)
                        writer.writerow(thisRow)

    def makeAnswers(self, question, answer, unit, indent, options):
        rows = []
        if type(answer) == list:
            for r in answer:
                rAnswer = r.value if isinstance(r, OperandResult) else r.answer
                rRows = self.makeAnswers(question, rAnswer, r.unit, indent + 1, options)
                rows.extend(rRows)
                question = ''
        else:
            row = [question]
            if indent > 1:
                for i in range(1, indent):
                    row.append('')
            row.append(self.htmlservice.htmlToText(
                self.htmlservice.createSingleAnswerHtml(answer, None, options)))
            if unit is not None:
                row.append(self.htmlservice.htmlToText(
                    self.htmlservice.createUnitHtml(answer, unit, options)))
            rows.append(row)
        return rows
