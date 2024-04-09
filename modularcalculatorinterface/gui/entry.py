#!/usr/bin/python3

from modularcalculatorinterface.services.htmlservice import *
from modularcalculatorinterface.services.syntaxservice import *

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QTextFormat, QKeySequence, QPalette, QAction

import time
import uuid


class CalculatorEntry(QTextEdit):

    def __init__(self, interface):
        super().__init__()

        self.interface = interface
        self.config = self.interface.config
        if 'font' not in self.config.main['entry'] or not QFont(self.config.main['entry']['font']).exactMatch():
            self.config.main['entry']['font'] = self.interface.getDefaultFixedFont()


        self.calculator = None

        self.htmlservice = interface.htmlservice
        self.initStyling()
        self.applyConfig()

        self.oldHtml = None

        self.cachedStatements = None

        self.tabSpaces = 4

        self.undoStack = CalculatorUndoStack(self)

        self.syntaxservice = SyntaxService(self)
        self.syntaxservice.restartProc()

    def initStyling(self):
        editFont = QFont(self.config.main['entry']['font'])
        editFont.setPointSize(self.config.main['entry']['fontsize_pt'])
        editFont.setBold(self.config.main['entry']['bold'])
        self.setFont(editFont)

        self.colours = self.htmlservice.background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, self.colours[0])
        self.setPalette(palette)

    def applyConfig(self):
        if 'autoexecute' not in self.config.main['entry']:
            self.config.main['entry']['autoexecute'] = False
            self.config.main['entry']['autoexecute_timeout'] = 1
        self.autoexecute = None
        if self.config.main['entry']['autoexecute']:
            self.autoexecute = self.config.main['entry']['autoexecute_timeout']
        self.autoExecuteTimer = None

    def setCalculator(self, calculator):
        self.calculator = calculator

    def keyPressEvent(self, e):
        self.undoStack.keyPressed()
        if e.key() == Qt.Key.Key_Tab:
            spaces = self.tabSpaces - (self.textCursor().columnNumber() % self.tabSpaces)
            self.insert(' ' * spaces)
        elif e.key() == Qt.Key.Key_Z and e.modifiers() & Qt.KeyboardModifier.ControlModifier and not e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.undo()
        elif e.key() == Qt.Key.Key_Z and e.modifiers() & Qt.KeyboardModifier.ControlModifier and e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.redo()
        elif (e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return) and e.modifiers() == Qt.KeyboardModifier.NoModifier:
            text = self.toPlainText()[0: self.textCursor().position()]
            pos = text.rfind("\n")
            if pos > -1:
                line = (text[pos + 1:])
            else:
                line = text
            spaces = 0
            while spaces < len(line) and line[spaces] == ' ':
                spaces += 1
            super().keyPressEvent(e)
            self.insert(' ' * spaces)
        else:
            super().keyPressEvent(e)
        self.checkSyntax()
        if self.autoexecute is not None:
            if self.autoExecuteTimer is None:
                self.autoExecuteTimer = QTimer(self.interface)
                self.autoExecuteTimer.setSingleShot(True)
                self.autoExecuteTimer.timeout.connect(self.interface.calculatormanager.calc)
            self.autoExecuteTimer.start(self.autoexecute * 1000)


    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.checkSyntax()

    def contextMenuEvent(self, e):
        menu = self.createStandardContextMenu()

        self.undoAction = QAction('Undo', self)
        self.undoAction.triggered.connect(self.undo)
        self.undoAction.setShortcut(QKeySequence("Ctrl+z"))
        self.undoAction.setEnabled(self.undoStack.canUndo())
        oldUndoAction = menu.actions()[0]
        menu.insertAction(oldUndoAction, self.undoAction)
        menu.removeAction(oldUndoAction)

        self.redoAction = QAction('Redo', self)
        self.redoAction.triggered.connect(self.redo)
        self.redoAction.setShortcut(QKeySequence("Ctrl+Shift+z"))
        self.redoAction.setEnabled(self.undoStack.canRedo())
        oldRedoAction = menu.actions()[1]
        menu.insertAction(oldRedoAction, self.redoAction)
        menu.removeAction(oldRedoAction)

        for a in range (3, 7):
            menu.actions()[a].triggered.connect(self.checkSyntax)

        menu.exec(e.globalPos())

    def dropEvent(self, e):
        super().dropEvent(e)
        self.checkSyntax()

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insert(source.text())

    def checkSyntax(self, force=False, undo=False):
        if self.calculator is not None and (force or undo or self.oldHtml is None or self.oldHtml != self.getContents()):
            expr = self.getContents()

            if len(expr) > 0 and expr[-1] != "\n":
                expr += "\n"

            if not undo and (self.oldHtml is None or self.oldHtml != self.getContents()):
                self.undoStack.push(expr)

            before = []
            after = []
            i = 0
            ii = len(expr)
            if self.cachedStatements is not None and not force:
                for statement in self.cachedStatements:
                    if expr[i:].startswith(statement.text):
                        before.append(statement)
                        i += statement.length
                    else:
                        break
                if len(before) > 0:
                    i -= before[-1].length
                    del before[-1]

                for statement in reversed(self.cachedStatements):
                    if ii <= i:
                        break
                    elif expr[ii - statement.length:].startswith(statement.text):
                        after.insert(0, statement)
                        ii -= statement.length
                    else:
                        break
                if len(after) > 0:
                    ii += after[0].length
                    del after[0]

            self.lastUuid = uuid.uuid4()
            statements = SyntaxService.doSyntaxParsing(self.calculator, self.htmlservice.highlighter, expr[i:ii], True)
            self.doSyntaxHighlighting(statements, before, after, self.lastUuid)

            if self.config.main['entry']['show_execution_errors']:
                self.syntaxservice.sendToProc(expr, [], self.lastUuid)


    def doSyntaxHighlighting(self, statements, before, after, uuid):
        if self.lastUuid is None or uuid != self.lastUuid:
            return

        if len(statements) > 0 and len(statements[-1].flatItems) > 0 and statements[-1].flatItems[-1][0] == 'error':
            statements[-1].flatItems[-1] = (statements[-1].flatItems[-1][0], statements[-1].flatItems[-1][1] + ''.join([s.text for s in after]))
            after = []

        newhtml = self.htmlservice.createStatementsHtml(statements)

        allStatements = before + statements + after
        totalHtml = self.htmlservice.css
        totalHtml += ''.join([s.html for s in before])
        totalHtml += newhtml
        totalHtml += ''.join([s.html for s in after])

        highlightPositions = []
        if self.config.main['entry']['view_line_highlighting']:
            p = 0
            for i, statement in enumerate(allStatements):
                if i % 2 == 1:
                    highlightPositions.append((p, p + statement.length))
                p += statement.length

        self.applySyntaxHighlighting(allStatements, totalHtml, highlightPositions)

    def applySyntaxHighlighting(self, allStatements, html, highlightPositions):
        self.cachedStatements = allStatements
        self.updateHtml(html)
        self.oldHtml = self.toHtml()
        if self.config.main['entry']['view_line_highlighting']:
            self.highlightPositions = highlightPositions
            self.addLineHighlights()
        else:
            self.highlightPositions = []
            self.setExtraSelections([])

        self.interface.filemanager.setCurrentFileAndModified(self.interface.filemanager.currentFile(), self.isModified())

    def addLineHighlights(self):
        extraSelections = []
        for pos in self.highlightPositions:
            selection = QTextEdit.ExtraSelection()

            selection.cursor = QTextCursor(self.document())
            selection.cursor.setPosition(pos[0])
            selection.cursor.setPosition(pos[1], QTextCursor.MoveMode.KeepAnchor)

            background = self.colours[1]
            selection.format.setBackground(background)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)

            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def refresh(self):
        self.initStyling()
        self.applyConfig()
        self.checkSyntax(True)

    def updateHtml(self, html):
        cursoranc = self.textCursor().anchor()
        cursorpos = self.textCursor().position()
        sliderpos = self.verticalScrollBar().sliderPosition()
        self.setHtml(html)
        cursor = self.textCursor()
        if cursoranc != cursorpos:
            cursor.setPosition(cursoranc)
            cursor.setPosition(cursorpos, QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.setPosition(cursorpos)
        self.setTextCursor(cursor)
        self.verticalScrollBar().setSliderPosition(sliderpos)

    def insert(self, text):
        self.insertPlainText(text)
        self.checkSyntax()

    def getContents(self):
        return self.toPlainText()

    def setContents(self, text, undo=False):
        if len(text) > 0 and text[-1] != "\n":
            text += "\n"
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
            original = self.toHtml()
        self.original = original

    def isModified(self):
        return self.toHtml() != self.original

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
        try:
            self.lastUuid = None
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
                cursor.setPosition(state['cursorSelectionStart'], QTextCursor.MoveMode.MoveAnchor)
                if 'cursorSelectionEnd' in state:
                    cursor.setPosition(state['cursorSelectionEnd'], QTextCursor.MoveMode.KeepAnchor)
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
            self.oldHtml = None

            if refresh:
                self.refresh()
            else:
                self.oldHtml = self.toHtml()
        except Exception as e:
            self.interface.printError()


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
                self.parent.oldHtml = self.history[self.historyPos - 2]
            else:
                self.parent.oldHtml = None
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
            self.parent.oldHtml = self.history[self.historyPos - 2]
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
