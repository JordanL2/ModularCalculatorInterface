#!/usr/bin/python3

from modularcalculator.objects.exceptions import CalculatingException, CalculatorException
from modularcalculatorinterface.services.calculatormanager import *
from modularcalculatorinterface.services.htmlservice import Statement, ErrorItem

from PyQt5.QtCore import QTimer

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
        state = None
        if len(before) > 0:
            state = before[-1].state
        self.queueIn.put({
            'expr': expr,
            'state': state,
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
                state = message['state']
                before = message['before']
                uuid = message['uuid']
                statements = SyntaxService.doSyntaxParsing(calculator, expr, False, state)
                queueOut.put({
                    'statements': statements,
                    'before': before,
                    'uuid': uuid,
                })
            else:
                sleep(SyntaxService.POLL_MS / 1000)

    def doSyntaxParsing(calculator, expr, parseOnly, state=None):
        try:
            if state is None:
                calculator.vars = {}
            else:
                calculator.vars = state.copy()
            response = calculator.calculate(expr, {'parse_only': parseOnly, 'include_state': True})
            statements = [Statement(r.items, r.state) for r in response.results]
        except CalculatingException as err:
            statements = [Statement(r.items, r.state) for r in err.response.results]
            statements += [Statement(s) for s in err.statements[len(err.response.results):]]
            i = err.find_pos(expr)
            statements.append(Statement([ErrorItem(expr[i:])]))
        except CalculatorException as err:
            statements = [Statement(ErrorItem(expr))]

        return statements
