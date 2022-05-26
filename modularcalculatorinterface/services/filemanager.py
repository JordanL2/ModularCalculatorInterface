#!/usr/bin/python3


class FileManager():

    def __init__(self, interface):
        self.interface = interface


    def currentFile(self, i=None):
        if i is None:
            i = self.selectedTab()
        return self.tabmanager.tabs[i]['currentFile']

    def currentFileModified(self, i=None):
        if i is None:
            i = self.selectedTab()
        return self.tabmanager.tabs[i]['currentFileModified']

    def setCurrentFile(self, currentFile, i=None):
        if i is None:
            i = self.selectedTab()
        self.tabmanager.tabs[i]['currentFile'] = currentFile

    def setCurrentFileModified(self, currentFileModified, i=None):
        if i is None:
            i = self.selectedTab()
        self.tabmanager.tabs[i]['currentFileModified'] = currentFileModified

    def selectedTab(self):
        return self.tabmanager.selectedTab

    def setWindowTitle(self, title):
        self.interface.setWindowTitle(title)

    def setTabText(self, title, i=None):
        if i is None:
            i = self.selectedTab()
        self.tabmanager.tabbar.setTabText(i, title)

    def setCurrentFileAndModified(self, file, modified=False, i=None):
        self.setCurrentFile(file, i)
        self.setCurrentFileModified(modified, i)
        if not modified:
            self.tabmanager.setOriginal(i)
        if i is None or i == self.selectedTab():
            if self.currentFile() is None:
                self.setWindowTitle('Modular Calculator')
            else:
                fileName = self.currentFile()
                if self.currentFileModified():
                    fileName += ' *'
                self.setWindowTitle("Modular Calculator - {}".format(fileName))
                self.setTabText(fileName, self.selectedTab())

    def open(self):
        filePath = self.interface.getOpenFileName("Open File", "All Files (*)")
        if filePath:
            for i in range(0, len(self.tabmanager.tabs)):
                if self.currentFile(i) == filePath:
                    self.tabmanager.selectTab(i)
                    return
            self.tabmanager.addTab()
            fh = open(filePath, 'r')
            text = str.join("", fh.readlines())
            self.interface.entry.setContents(text)
            self.interface.entry.undoStack.clearHistory()
            self.setCurrentFileAndModified(filePath, False)

    def save(self, i=None):
        if i == False:
            i = None
        if self.currentFile(i) is None:
            self.saveAs(i)
            return
        fh = open(self.currentFile(i), 'w')
        fh.write(self.getEntryContents(i))
        self.setCurrentFileAndModified(self.currentFile(), False, i)

    def saveAs(self, i=None):
        if i == False:
            i = None
        filePath = self.interface.getSaveFileName("Save File", "All Files (*)")
        if filePath:
            fh = open(filePath, 'w')
            fh.write(self.getEntryContents(i))
            self.setCurrentFileAndModified(filePath, False, i)

    def checkIfNeedToSave(self, i=None):
        if self.currentFile(i) is not None and self.currentFileModified(i):
            response = self.interface.questionYesNoCancel('Unsaved File', "Save changes to {} before closing?".format(self.currentFile()))
            if response == True:
                self.save(i)
            elif response is None:
                return True
        return False

    def getEntryContents(self, i=None):
        self.tabmanager.storeSelectedTab()
        if i is None:
            i = self.selectedTab()
        return self.tabmanager.tabs[i]['entry']['text']
