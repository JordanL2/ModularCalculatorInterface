#!/usr/bin/python3

from modularcalculator.objects.api import *
from modularcalculator.services.syntaxhighlighter import *
from modularcalculatorinterface.guitools import *

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable
from PyQt5.QtWidgets import QTextEdit, QAction
from PyQt5.QtGui import QFontDatabase, QTextCursor, QTextCharFormat, QGuiApplication, QTextFormat, QKeySequence

import time
import uuid


class CalculatorTextEdit(QTextEdit):

    def __init__(self, interface):
        super().__init__()

        self.calculator = None

        editFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        editFont.setBold(True)
        editFont.setPointSize(editFont.pointSize() + 2)
        self.setFont(editFont)

        self.interface = interface
        self.highlighter = SyntaxHighlighter()
        self.setTheme()
        self.initStyling()
        self.oldText = None

        self.autoExecute = True

        self.cached_response = None

        self.tabSpaces = 4
        self.lineHighlighting = True

        self.undoStack = CalculatorUndoStack(self)

    def setCalculator(self, calculator):
        self.calculator = calculator

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
            self.doSyntaxHighlighting(CalculatorTextEdit.doSyntaxParsing(self.calculator, expr_truncated, response.copy(), later_results, i, ii, self.last_uuid, True))

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

        if result['uuid'] != self.last_uuid:
            return

        if not result['parse_only']:
            self.cached_response = response

        statements = [r.items for r in response.results] + error_statements
        errorExpr = expr[ii:]
        newhtml, highlightPositions = self.makeHtml(statements, errorExpr)
        self.updateHtml(newhtml)

        extraSelections = []
        for pos in highlightPositions:
            selection = QTextEdit.ExtraSelection()

            selection.cursor = QTextCursor(self.document())
            selection.cursor.setPosition(pos[0])
            selection.cursor.setPosition(pos[1], QTextCursor.KeepAnchor)

            background = QGuiApplication.palette().alternateBase().color()
            selection.format.setBackground(background)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

        self.interface.filemanager.setCurrentFileAndModified(self.interface.filemanager.currentFile(), self.isModified())

    def makeHtml(self, statements, errorExpr):
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
                newhtml += makeSpan(htmlSafe(text), style)
                p += len(text)

            if alternate and self.lineHighlighting:
                highlightPositions.append((p0, p))

        if errorExpr != '':
            newhtml += makeSpan(htmlSafe(errorExpr), 'error')

        return newhtml, highlightPositions

    def refresh(self):
        self.initStyling()
        self.checkSyntax(True)

    def updateHtml(self, html):
        cursorpos = self.textCursor().position()
        sliderpos = self.verticalScrollBar().sliderPosition()
        self.setHtml(self.css + html)
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

    def setLineHighlighting(self, lineHighlighting, refresh=True):
        self.lineHighlighting = lineHighlighting
        self.interface.viewLineHighlighting.setChecked(lineHighlighting)
        if refresh:
            self.refresh()

    def isModified(self):
        return self.getContents() != self.original

    def saveState(self):
        return {
            'text': self.getContents(),
            'original': self.original,
            'cursorSelectionStart': self.textCursor().selectionStart(),
            'cursorSelectionEnd': self.textCursor().selectionEnd(),
            'sliderPosition': self.verticalScrollBar().sliderPosition(),
            'history': self.undoStack.history,
            'historyPos': self.undoStack.historyPos,
            'lineHighlighting': self.lineHighlighting,
        }

    def restoreState(self, state):
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
                raise 'history is in state but historyPos isn\'t'
        else:
            self.undoStack.history = []
            self.undoStack.historyPos = 0

        if 'lineHighlighting' in state:
            self.setLineHighlighting(state['lineHighlighting'], False)
        else:
            self.setLineHighlighting(True, False)

        self.undoStack.stateChanged(force=True)

        self.cached_response = None
        self.oldText = None

        self.refresh()


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

        self.signals.result.emit(CalculatorTextEdit.doSyntaxParsing(self.calculator, self.expr, self.response, [], self.i, self.ii, self.uuid, False))
