#!/usr/bin/python3

from modularcalculator.objects.api import *
from modularcalculator.objects.exceptions import *

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable
from PyQt5.QtWidgets import QTextEdit, QAction
from PyQt5.QtGui import QFont, QFontDatabase, QTextCursor, QTextFormat, QKeySequence, QPalette

import time
import uuid


class CalculatorEntry(QTextEdit):

    def __init__(self, interface):
        super().__init__()

        self.interface = interface
        self.calculator = None

        self.defaultConfig()
        self.loadConfig()
        self.htmlService = interface.htmlService
        self.initStyling()

        self.oldText = None

        self.autoExecute = True

        self.cached_response = None

        self.tabSpaces = 4

        self.undoStack = CalculatorUndoStack(self)

    def defaultConfig(self):
        defaultFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        defaultFontSize = defaultFont.pointSize()
        self.options = {
            'font': defaultFont.family(),
            'fontsize_pt': defaultFontSize + 2,
            'bold': True,
        }

    def loadConfig(self):
        config = self.interface.config.main
        if config is not None:
            if 'entry' in config:
                config = config['entry']
                if config is not None:
                    for o in self.options.keys():
                        if o in config:
                            self.options[o] = config[o]

    def initStyling(self):
        editFont = QFont(self.options['font'])
        editFont.setPointSize(self.options['fontsize_pt'])
        editFont.setBold(self.options['bold'])
        self.setFont(editFont)

        self.colours = self.htmlService.background
        palette = self.palette()
        palette.setColor(QPalette.Base, self.colours[0])
        self.setPalette(palette)

    def setCalculator(self, calculator):
        self.calculator = calculator

    def keyPressEvent(self, e):
        self.undoStack.keyPressed()
        if e.key() == Qt.Key_Tab:
            spaces = self.tabSpaces - (self.textCursor().columnNumber() % self.tabSpaces)
            self.insert(' ' * spaces)
        elif e.key() == Qt.Key_Z and e.modifiers() & Qt.CTRL and not e.modifiers() & Qt.SHIFT:
            self.undo()
        elif e.key() == Qt.Key_Z and e.modifiers() & Qt.CTRL and e.modifiers() & Qt.SHIFT:
            self.redo()
        else:
            super().keyPressEvent(e)
        self.checkSyntax()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.checkSyntax()

    def contextMenuEvent(self, e):
        menu = self.createStandardContextMenu()

        self.undoAction = QAction('Undo', self)
        self.undoAction.triggered.connect(self.undo)
        self.undoAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z))
        self.undoAction.setEnabled(self.undoStack.canUndo())
        oldUndoAction = menu.actions()[0]
        menu.insertAction(oldUndoAction, self.undoAction)
        menu.removeAction(oldUndoAction)

        self.redoAction = QAction('Redo', self)
        self.redoAction.triggered.connect(self.redo)
        self.redoAction.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z))
        self.redoAction.setEnabled(self.undoStack.canRedo())
        oldRedoAction = menu.actions()[1]
        menu.insertAction(oldRedoAction, self.redoAction)
        menu.removeAction(oldRedoAction)

        menu.exec(e.globalPos())

    def checkSyntax(self, force=False, undo=False):
        if self.calculator is not None and (force or undo or self.oldText is None or self.oldText != self.getContents()):
            expr = self.getContents()

            if not undo and (self.oldText is None or self.oldText != self.getContents()):
                self.undoStack.push(expr)

            if len(expr) > 0 and expr[-1] != "\n":
                expr += "\n"

            response = CalculatorResponse()
            i = 0
            ii = None
            expr_truncated = expr
            later_results = []
            if self.cached_response is not None and not force:
                for result in self.cached_response.results:
                    if expr[i:].startswith(result.expression):
                        response.results.append(result)
                        i += len(result.expression)
                    else:
                        break
                if len(response.results) > 0 and len(response.results) == len(self.cached_response.results):
                    i -= len(response.results[-1].expression)
                    del response.results[-1]

                if len(response.results) + 3 < len(self.cached_response.results):
                    later_results = self.cached_response.results[len(response.results) + 3:]
                    later_results_length = 0
                    for l in later_results:
                        later_results_length += len(l.expression)
                    expr_truncated = expr[0:len(expr) - later_results_length]

            self.last_uuid = uuid.uuid4()
            self.doSyntaxHighlighting(CalculatorEntry.doSyntaxParsing(self.calculator, expr_truncated, response.copy(), later_results, i, ii, self.last_uuid, True))

            if self.autoExecute:
                worker = SyntaxHighlighterWorker(self.calculator, expr, response, i, ii, self.last_uuid)
                worker.signals.result.connect(self.doSyntaxHighlighting)
                worker.setAutoDelete(True)
                self.interface.threadpool.clear()
                self.interface.threadpool.start(worker)

        self.oldText = self.getContents()

    def doSyntaxParsing(calculator, expr, response, later_results, i, ii, uuid, parse_only):
        error_statements = []

        try:
            if len(response.results) > 0:
                calculator.vars = response.results[-1].state.copy()
            else:
                calculator.vars = {}
            calcResponse = calculator.calculate(expr[i:], {'parse_only': parse_only, 'include_state': True})
            response.results.extend(calcResponse.results)
            response.results.extend(later_results)
            ii = len(expr)
        except CalculatingException as err:
            response.results.extend(err.response.results)
            error_statements = err.statements[len(err.response.results):]
            err.statements = [r.items for r in response.results] + error_statements
            ii = err.find_pos(expr)
        except CalculatorException as err:
            ii = i

        return({
            'expr': expr,
            'response': response,
            'error_statements': error_statements,
            'ii': ii,
            'uuid': uuid,
            'parse_only': parse_only,
            })

    def doSyntaxHighlighting(self, result):
        expr = result['expr']
        response = result['response']
        error_statements = result['error_statements']
        ii = result['ii']

        if self.last_uuid is None or result['uuid'] != self.last_uuid:
            return

        if not result['parse_only']:
            self.cached_response = response

        statements = [r.items for r in response.results] + error_statements
        errorExpr = expr[ii:]
        newhtml, self.highlightPositions = self.htmlService.createStatementsHtml(statements, errorExpr, self.interface.lineHighlighting)
        self.updateHtml(newhtml)
        self.addLineHighlights()

        self.interface.filemanager.setCurrentFileAndModified(self.interface.filemanager.currentFile(), self.isModified())

    def addLineHighlights(self):
        extraSelections = []
        for pos in self.highlightPositions:
            selection = QTextEdit.ExtraSelection()

            selection.cursor = QTextCursor(self.document())
            selection.cursor.setPosition(pos[0])
            selection.cursor.setPosition(pos[1], QTextCursor.KeepAnchor)

            background = self.colours[1]
            selection.format.setBackground(background)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def refresh(self):
        self.initStyling()
        self.checkSyntax(True)

    def updateHtml(self, html):
        cursorpos = self.textCursor().position()
        sliderpos = self.verticalScrollBar().sliderPosition()
        self.setHtml(html)
        cursor = self.textCursor()
        cursor.setPosition(cursorpos)
        self.setTextCursor(cursor)
        self.verticalScrollBar().setSliderPosition(sliderpos)

    def insert(self, text):
        self.insertPlainText(text)
        self.checkSyntax()

    def getContents(self):
        return self.toPlainText()

    def setContents(self, text, undo=False):
        self.setPlainText(text)
        self.checkSyntax(False, undo)

    def undo(self):
        self.undoStack.undo()

    def redo(self):
        self.undoStack.redo()

    def clearContents(self):
        self.setContents("\n")

    def setOriginal(self, original=None):
        if original is None:
            original = self.getContents()
        self.original = original

    def isModified(self):
        return self.getContents() != self.original

    def saveState(self):
        return {
            'html': self.toHtml(),
            'text': self.getContents(),
            'original': self.original,
            'cursorSelectionStart': self.textCursor().selectionStart(),
            'cursorSelectionEnd': self.textCursor().selectionEnd(),
            'sliderPosition': self.verticalScrollBar().sliderPosition(),
            'history': self.undoStack.history,
            'historyPos': self.undoStack.historyPos,
            'highlightPositions': self.highlightPositions,
        }

    def restoreState(self, state, refresh=True):
        self.last_uuid = None
        if 'html' in state:
            self.setHtml(state['html'])
            if 'highlightPositions' in state:
                self.highlightPositions = state['highlightPositions']
                self.addLineHighlights()
        else:
            refresh = True
            if 'text' in state:
                self.setPlainText(state['text'])
            else:
                self.setPlainText('')
        if 'original' in state:
            self.setOriginal(state['original'])
        else:
            self.setOriginal()

        if 'cursorSelectionStart' in state:
            cursor = self.textCursor()
            cursor.setPosition(state['cursorSelectionStart'], QTextCursor.MoveAnchor)
            if 'cursorSelectionEnd' in state:
                cursor.setPosition(state['cursorSelectionEnd'], QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)

        if 'sliderPosition' in state:
            self.verticalScrollBar().setSliderPosition(state['sliderPosition'])

        if 'history' in state:
            self.undoStack.history = state['history']
            if 'historyPos' in state:
                self.undoStack.historyPos = state['historyPos']
            else:
                raise Exception('history is in state but historyPos isn\'t')
        else:
            self.undoStack.history = []
            self.undoStack.historyPos = 0

        self.undoStack.stateChanged(force=True)

        self.cached_response = None
        self.oldText = None

        if refresh:
            self.refresh()
        else:
            self.oldText = self.getContents()


class CalculatorUndoStack(QObject):

    canUndoChanged = pyqtSignal(bool)
    canRedoChanged = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.history = []
        self.historyPos = 0
        self.historySize = 1000

        self.lastCanUndo = None
        self.lastCanRedo = None
        self.stateChanged()

    def canUndo(self):
        return self.historyPos > 1

    def canRedo(self):
        return self.historyPos < len(self.history)

    def stateChanged(self, force=False):
        self.checkCanUndo(force)
        self.checkCanRedo(force)

    def checkCanUndo(self, force=False):
        newCanUndo = self.canUndo()
        if newCanUndo != self.lastCanUndo or force:
            self.canUndoChanged.emit(newCanUndo)
        self.lastCanUndo = newCanUndo

    def checkCanRedo(self, force=False):
        newCanRedo = self.canRedo()
        if newCanRedo != self.lastCanRedo or force:
            self.canRedoChanged.emit(newCanRedo)
        self.lastCanRedo = newCanRedo

    def undo(self):
        if self.canUndo():
            self.parent.cached_response = None

            sliderpos = self.parent.verticalScrollBar().sliderPosition()

            self.historyPos -= 1
            (expr, cursorpos) = self.history[self.historyPos - 1]
            if self.historyPos > 1:
                self.parent.oldText = self.history[self.historyPos - 2]
            else:
                self.parent.oldText = None
            self.parent.setContents(expr, True)

            if cursorpos is not None:
                cursor = self.parent.textCursor()
                cursor.setPosition(cursorpos)
                self.parent.setTextCursor(cursor)
            self.parent.verticalScrollBar().setSliderPosition(sliderpos)

            self.stateChanged()

    def redo(self):
        if self.canRedo():
            self.parent.cached_response = None

            sliderpos = self.parent.verticalScrollBar().sliderPosition()

            self.historyPos += 1
            (expr, cursorpos) = self.history[self.historyPos - 1]
            self.parent.oldText = self.history[self.historyPos - 2]
            self.parent.setContents(expr, True)

            if cursorpos is not None:
                cursor = self.parent.textCursor()
                cursor.setPosition(cursorpos)
                self.parent.setTextCursor(cursor)
            self.parent.verticalScrollBar().setSliderPosition(sliderpos)

            self.stateChanged()

    def push(self, expr):
        if self.historyPos == 0 or expr != self.history[self.historyPos - 1][0]:
            if self.historyPos < len(self.history):
                del self.history[self.historyPos:]
            self.history.append([expr, None])
            if len(self.history) > self.historySize:
                self.history.pop(0)
            self.historyPos = len(self.history)

            self.stateChanged()

    def keyPressed(self):
        if len(self.history) > 0:
            self.history[self.historyPos - 1][1] = self.parent.textCursor().position()

    def clearHistory(self):
        self.history = [self.history[-1]]
        self.historyPos = 1


class SyntaxHighlighterSignals(QObject):

    result = pyqtSignal(dict)


class SyntaxHighlighterWorker(QRunnable):

    def __init__(self, calculator, expr, response, i, ii, uuid):
        super(SyntaxHighlighterWorker, self).__init__()

        self.signals = SyntaxHighlighterSignals()

        self.calculator = calculator
        self.expr = expr
        self.response = response
        self.i = i
        self.ii = ii
        self.uuid = uuid

    @pyqtSlot()
    def run(self):
        self.calculator.update_engine_prec()

        self.signals.result.emit(CalculatorEntry.doSyntaxParsing(self.calculator, self.expr, self.response, [], self.i, self.ii, self.uuid, False))
