#!/usr/bin/python3
from os.path import expanduser
from typing import List
import functools
import os
import sys
import jsonfiles
import rdbcommands
import restorebackup

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import profile
import task
import logger

def centerWindow(window):
    frameGm = window.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    frameGm.moveCenter(centerPoint)
    window.move(frameGm.topLeft())


def addMenu(window):
    mainMenu = window.menuBar()
    mainMenu.setNativeMenuBar(False)
    fileMenu = mainMenu.addMenu('File')

    exitButton = QAction('Exit', window)
    exitButton.setShortcut('Ctrl+Q')
    exitButton.triggered.connect(window.close)
    fileMenu.addAction(exitButton)


class FilePathWidget(QWidget):
    def __init__(self, parentLayout, source=None, fileType=None, dest=None, profileName=None):
        super().__init__()
        self.parentLayout = parentLayout
        self.home = expanduser("~")

        hbox = QHBoxLayout()

        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)
        self.sourceLineEdit = QLineEdit()
        self.sourceLineEdit.setReadOnly(True)
        self.sourceLineEdit.setToolTip("Select a File or Folder")
        self.sourceLineEdit.setText(source)

        self.getSourceBtn = QPushButton("...")  # , mainWindow
        self.chooseFileType = QComboBox()
        self.chooseFileType.addItem(task.Task.SingleFile)
        self.chooseFileType.addItem(task.Task.MultipleFiles)
        self.chooseFileType.addItem(task.Task.Directory)
        self.chooseFileType.setCurrentIndex(0)
        if fileType:
            index = self.chooseFileType.findText(fileType)
            self.chooseFileType.setCurrentIndex(index)

        self.chooseFileType.currentIndexChanged.connect(self.clearSource)

        self.removeBtn = QPushButton()
        removePixmap = QPixmap("remove.png")  # /add
        icon = QIcon(removePixmap)
        self.removeBtn.setIcon(icon)
        self.removeBtn.clicked.connect(self._delete)

        hbox.addWidget(self.sourceLineEdit)
        hbox.addWidget(self.getSourceBtn)
        hbox.addWidget(self.chooseFileType)
        hbox.setStretch(0, 4)
        hbox.setStretch(1, 0)
        hbox.setStretch(2, 0)

        self.getSourceBtn.clicked.connect(self._getPath)

        self.destLineEdit = QLineEdit()
        self.destLineEdit.setReadOnly(True)
        self.destLineEdit.setText(dest)
        self.destLineEdit.setToolTip(dest)
        self.getDestBtn = QPushButton("...")  # , mainWindow
        self.getDestBtn.clicked.connect(self._getDirectoryPath)

        self.profileBox = QComboBox()

        hbox.addWidget(self.destLineEdit)
        hbox.addWidget(self.getDestBtn)
        hbox.addWidget(self.profileBox)
        hbox.addWidget(self.removeBtn)
        hbox.setStretch(3, 4)
        hbox.setStretch(4, 0)
        hbox.setStretch(5, 0)
        hbox.setStretch(6, 0)

        self.updateProfileList()
        self.profileBox.setCurrentIndex(self.profileBox.findText(profileName))  # if it doesn't exist?

    def clearSource(self):
        # fileType button changed, clear source or else it is invalid
        self.sourceLineEdit.clear()
        self.sourceLineEdit.setToolTip("Select a File or Folder")

    def updateProfileList(self):
        profiles = profile.getProfiles()

        self.profileBox.clear()
        self.profileBox.addItems([x.name for x in profiles])
        # /task


        # todo
        # get profile from file...?
        # self.profileBox.setCurrentIndex()

    # user selects a path, it goes into the sourceLineEdit
    def _getPath(self):
        fileType = self.chooseFileType.currentText()

        if (fileType == task.Task.SingleFile):
            function = QFileDialog.getOpenFileName

        elif fileType == task.Task.Directory:
            function = QFileDialog.getExistingDirectory

        elif fileType == task.Task.MultipleFiles:
            function = QFileDialog.getOpenFileNames

        else:
            mb = QMessageBox()
            mb.setText("Error! Neither File nor Directory Selected.")
            mb.exec_()

        path = function(self, "Choose " + fileType, self.home)

        if type(path) is list:
            self.sourceLineEdit.setText(", ".join(path))  # if multiple files option
            self.sourceLineEdit.setToolTip("\n".join(path))
        else:
            self.sourceLineEdit.setText(path)
            self.sourceLineEdit.setToolTip(path)

    def _getDirectoryPath(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Directory", self.home)
        # empty directory?, existing rdb folder
        if os.listdir(path) and not os.path.isdir(os.path.join(path, "rdiff-backup-data")):
                mb = QMessageBox()
                mb.setWindowTitle("Warning")
                mb.setText("Selected directory must be empty or be an existing backup directory.\n"
                           "Create an empty directory.")
                mb.exec_()
        else:
            self.destLineEdit.setText(path)
            self.destLineEdit.setToolTip(path)

    def _delete(self):
        msg = QMessageBox()
        msg.setWindowTitle("Delete Row?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setText("Are you sure you want to delete this?")
        # msg.buttonClicked.connect
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            self.parentLayout.removeWidget(self)
            self.deleteLater()
        # self.parentlayout.repaint()



    def getTask(self):
        source = self.sourceLineEdit.text()
        dest = self.destLineEdit.text()
        fileType = self.chooseFileType.currentText()
        profileName = self.profileBox.currentText()
        t = task.Task(source, fileType, dest, profileName)  # todo, get profile method from profile module
        return t


def setupMainWindow():

    mainWindow = QMainWindow()
    scrollArea = QScrollArea()
    scrollArea.setBackgroundRole(QPalette.Dark)
    scrollArea.setWidget(mainWindow)
    scrollArea.setHorizontalScrollBarPolicy(Qt.QScrollBarPolicy.KKK)

    mainWindow.setMinimumWidth(1000)  # easy way to prevent sliding left
    mainWindow.move(200, 200)
    mainWindow.setWindowTitle('Easy Backup')
    # centerWindow(mainWindow)
    addMenu(mainWindow)
    return mainWindow


# def setupMainGrid(mainWindow):
#     form = QWidget()
#     grid = QGridLayout()
#     form.setLayout(grid)
#     mainWindow.setCentralWidget(form)
#     return grid


def getAddBtn():
    addBtn = QPushButton()
    pixmap = QPixmap("add.png")  # /add
    icon = QIcon(pixmap)
    addBtn.setIcon(icon)
    return addBtn


def addRow(vbox):
    filePath = FilePathWidget(vbox)
    vbox.addWidget(filePath)


def update(filePathVBox: QVBoxLayout):
    tasks = []
    for i in range(filePathVBox.count()):
        filePathWidget = filePathVBox.itemAt(i).widget()

        source = filePathWidget.sourceLineEdit.text()
        dest = filePathWidget.destLineEdit.text()
        fileType = filePathWidget.chooseFileType.currentText()
        p = filePathWidget.profileBox.currentText()

        inputs = [source, dest, fileType, p]
        valid = all(inputs)
        if valid:
            tasks.append(filePathWidget.getTask())

    jsonfiles.writeTasksToFile(tasks)
    rdbcommands.saveRestorePaths(tasks)


def restoreFromBackup(mainwindow):
    restorebackup.openRestoreMenu(mainwindow)


def loadTasks(filePathVBox: QVBoxLayout) -> List[task.Task]:
    # Grab tasks from file, create filepathwidgets for them
    tasks = jsonfiles.getTaskListFromFile()
    # remove empty rows
    if len(tasks) > 0:
        for i in range(filePathVBox.count()):
            filePathWidget = filePathVBox.itemAt(i).widget()
            filePathWidget.deleteLater()

    for t in tasks:
        filePathWidget = FilePathWidget(filePathVBox,
                                        t.source,
                                        t.fileType,
                                        t.dest,
                                        t.profileName
                                        )
        filePathVBox.addWidget(filePathWidget)

        if "," in t.source:
            files = t.source.split(",")
            filePathWidget.sourceLineEdit.setToolTip("\n".join(files))
        else:
            filePathWidget.sourceLineEdit.setToolTip(t.source)

        filePathWidget.sourceLineEdit.setText(t.source)

    return tasks


def editProfiles(mainWindow, filePathVBox: QVBoxLayout):
    profile.openProfileMenu(mainWindow)
    loadTasks(filePathVBox)
    # to update profile boxes with proper indexes simplest to just reload everything.


    # for i in range (filePathVBox.count()):
    #     filePathWidget = filePathVBox.itemAt(i).widget()
    #     filePathWidget.updateProfileList()


def main():
    # import rdiffbackup
    app = QApplication(sys.argv)
    # app.desktop()

    mainWindow = QMainWindow()
    scrollArea = QScrollArea()
    scrollArea.setBackgroundRole(QPalette.Dark)
    scrollArea.setWidget(mainWindow)
    # scrollArea.setHorizontalScrollBarPolicy(Qt.QScrollBarPolicy.KKK)

    mainWindow.setMinimumWidth(1000)  # easy way to prevent sliding left
    mainWindow.move(200, 200)
    mainWindow.setWindowTitle('Easy Backup')
    centerWindow(mainWindow)
    addMenu(mainWindow)
    # mainWindow = setupMainWindow()
    form = QWidget()
    grid = QGridLayout()
    form.setLayout(grid)
    mainWindow.setCentralWidget(form)
    # grid = setupMainGrid(mainWindow)

    addBtn = getAddBtn()

    # awful but it works
    lineEditLabel = QLabel("Source                                                                         "
                           "                                                   Destination")
    #
    filePathVBox = QVBoxLayout()

    filePath = FilePathWidget(filePathVBox)

    filePathVBox.setContentsMargins(0, 0, 0, 0)
    filePathVBox.addWidget(filePath)
    tasks = loadTasks(filePathVBox)

    saveBtn = QPushButton("Save tasks")
    saveBtn.setStyleSheet("background-color:pink")
    saveBtn.clicked.connect((functools.partial(update, filePathVBox)))

    restoreBtn = QPushButton("Restore from backup")
    restoreBtn.clicked.connect(functools.partial(restoreFromBackup, mainWindow))

    profileBtn = QPushButton("Edit Profiles")
    # profileBtn.clicked.connect(functools.partial(profile.openProfileMenu, mainWindow))
    profileBtn.clicked.connect(functools.partial(editProfiles, mainWindow, filePathVBox))

    grid.addWidget(profileBtn, 0, 0, 1, 2, Qt.AlignHCenter)
    grid.addWidget(restoreBtn, 1, 0, 1, 2, Qt.AlignHCenter)
    # grid.addLayout(profileRow,0,1)
    grid.addWidget(lineEditLabel, 2, 1)
    grid.addWidget(addBtn, 3, 0, Qt.AlignTop)

    grid.addLayout(filePathVBox, 3, 1)
    grid.addWidget(saveBtn, 4, 0, 1, 2, Qt.AlignHCenter)  # Qt.AlignHCenter

    addBtn.clicked.connect(functools.partial(addRow, filePathVBox))

    mainWindow.setMaximumSize(mainWindow.size())
    log = logger.setupLogger("base")
    log.info("Started GUI")
    mainWindow.show()
    print('test')

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
