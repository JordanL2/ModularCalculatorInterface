#!/usr/bin/python3

from modularcalculator.objects.exceptions import CalculatingException, CalculatorException
from modularcalculator.services.syntaxhighlighter import *
from modularcalculatorinterface.services.calculatormanager import *

from PyQt6.QtCore import QTimer

from queue import Empty
import multiprocessing
from time import sleep


class SyntaxService():

    POLL_MS = 10

    def __init__(self, entry):
        self.entry = entry
        self.interface = entry.interface
        self.config = entry.interface.config
        self.proc = None
        self.queueIn = multiprocessing.Queue()
        self.queueOut = multiprocessing.Queue()
        self.readTimer = QTimer(self.interface)
        self.readTimer.start(SyntaxService.POLL_MS)
        self.readTimer.timeout.connect(self.readFromProc)

    def restartProc(self):
        self.stopProc()
        self.proc = multiprocessing.Process(
            target=SyntaxService.processListen,
            args=[self.queueIn, self.queueOut, self.config.main],
            daemon=True)
        self.proc.start()

    def stopProc(self):
        if self.proc is not None:
            self.queueIn.put({'quit': True})
            self.proc = None

    def sendToProc(self, expr, before, uuid):
        self.queueIn.put({
            'expr': expr,
            'before': before,
            'uuid': uuid,
        })

    def readFromProc(self):
        while True:
            try:
                result = self.queueOut.get(block=False)
                self.entry.doSyntaxHighlighting(result['statements'], result['before'], [], result['uuid'])
            except Empty:
                break

    def processListen(queueIn, queueOut, config):
        calculator = CalculatorManager.createCalculator(config)
        highlighter = SyntaxHighlighter()

        while True:
            messages = []
            while True:
                try:
                    message = queueIn.get(block=False)
                    messages.append(message)
                except Empty:
                    break
            if len(messages) > 0:
                if len([m for m in messages if 'quit' in m]) > 0:
                    break

                message = messages[-1]
                expr = message['expr']
                before = message['before']
                uuid = message['uuid']
                statements = SyntaxService.doSyntaxParsing(calculator, highlighter, expr, False)
                queueOut.put({
                    'statements': statements,
                    'before': before,
                    'uuid': uuid,
                })
            else:
                sleep(SyntaxService.POLL_MS / 1000)

    def doSyntaxParsing(calculator, highlighter, expr, parseOnly):
        try:
            calculator.vars = {}
            response = calculator.calculate(expr, {'parse_only': parseOnly})
            statements = [Statement(r.items) for r in response.results]
        except CalculatingException as err:
            statements = [Statement(r.items) for r in err.response.results]
            statements += [Statement(s) for s in err.statements[len(err.response.results):]]
            i = err.find_pos(expr)
            statements.append(Statement([ErrorItem(expr[i:])]))
        except CalculatorException as err:
            statements = [Statement(ErrorItem(expr))]

        statements = SyntaxService.compactStatements(statements)

        for statement in statements:
            statement.flatten(highlighter)
            statement.generateText()

        return statements

    def compactStatements(statements):
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
                firstNewLine = [i for i, item in enumerate(statement.items) if i > lastFunctionalItem and item.text == "\n"]
                if len(firstNewLine) > 0:
                    firstNewLine = min(firstNewLine)
                    nonEmptyItems = [i for i, item in enumerate(statement.items) if i > firstNewLine and not item.functional() and item.text.strip() != '']
                    if len(nonEmptyItems) > 0:
                        firstNonEmptyItem = min(nonEmptyItems)
                        compactedStatements[si + 1].items = statement.items[firstNonEmptyItem:] + compactedStatements[si + 1].items
                        statement.items = statement.items[0:firstNonEmptyItem]

        return compactedStatements


class ErrorItem(Item):

    def __init__(self,  text):
        super().__init__(text)

    def isop(self):
        return False

    def desc(self):
        return 'error'


class Statement():

    def __init__(self, items):
        self.items = items
        self.flatItems = None
        self.text = None
        self.length = None
        self.html = None

    def flatten(self, highlighter):
        highlightStatement = highlighter.highlight_statements([self.items])[0]
        self.flatItems = highlightStatement
        self.items = None

    def generateText(self):
        self.text = ''.join([i[1] for i in self.flatItems])
        self.length = len(self.text)
        return self.text, self.length

    def generateHtml(self, htmlservice):
        statementHtml = ''
        for item in self.flatItems:
            style = item[0]
            text = item[1]
            statementHtml += htmlservice.makeSpan(htmlservice.htmlSafe(text), style)
        self.html = statementHtml
        return self.html

    def nonEmptyItems(self):
        return [i for i, item in enumerate(self.items) if i.text.strip() != '']

    def functionalItems(self):
        return [i for i, item in enumerate(self.items) if item.functional() and not item.text.strip() == '']

    def hasFunctionalItems(self):
        return len(self.functionalItems()) > 0
