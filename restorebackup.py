from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
from functools import partial
import glob

import rdbcommands
from datetime import datetime
from os.path import expanduser
import restorefile
import logging

def openRestoreMenu(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Restore")
    dialog.resize(600,300)
    dialog.setModal(True)
    # dialog.setContentsMargins(0,0,0,0)
    grid = QGridLayout()
    # grid.setContentsMargins(0,0,0,0)
    paths = rdbcommands.getRestorePathList()
    backupPaths = []
    for p in paths:
        loc = os.path.join(p, "rdiff-backup-data")
        if os.path.isdir(loc):
            backupPaths.append(p)

    # cv = QColumnView(dialog)
    # cv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    model = QStandardItemModel()
    # model.setColumnCount(0)
    # cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    listView = QListView()
    # listView.setContentsMargins(0,0,0,0)
    listView.setFixedSize(500,200)
    listView.setModel(model)
    listView.setEditTriggers(QAbstractItemView.NoEditTriggers)


    # listView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    # listView.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    # listView.setResizeMode(QListView.Fixed) QListView.Adjust
    # listView.setLayoutMode()

    for p in backupPaths:
        item = QStandardItem(p)
        model.appendRow(item)

    # model.appendRow(QStandardItem("asdfasdasfdd"))


    chooseBtn = QPushButton()
    chooseBtn.setText("Restore previous file or folder version")
    chooseBtn.clicked.connect(partial(restorefile.restoreFileOrDirectory, dialog, listView))

    chooseLatestBtn = QPushButton()
    chooseLatestBtn.setText("Restore latest file or folder version")
    chooseLatestBtn.clicked.connect(partial(restorefile.restoreLatest, dialog, listView))

    restoreAllBtn = QPushButton()
    restoreAllBtn.setText("Restore entire directory")
    restoreAllBtn.clicked.connect(partial(restoreEntireDirectory, dialog, listView))

    grid.addWidget(listView, 0,0, Qt.AlignHCenter)
    grid.addWidget(chooseBtn,1, 0)
    grid.addWidget(chooseLatestBtn, 2, 0)
    grid.addWidget(restoreAllBtn, 3, 0)

    # vert.addWidget(listView)

    """
    | file/path/1
    | file/path/2
    |
    | restore entire directory  | choose a file

    """
    dialog.setLayout(grid)
    dialog.exec_()



"""

"""
def restoreEntireDirectory(parent, parentListView):
    """
    @type parentListView: QListView
    """

    def restoreSelection(listView, dict, backupSource, destinationLineEdit):
        """
        @type listView: QListView
        @type dict: dictionary
        @type destinationLineEdit: QLineEdit
        """
        dest = destinationLineEdit.text()
        #selected destination
        if not dest:
            box = QMessageBox()
            box.setText("You must select a destination")
            box.exec_()
            return

        #selected restore date
        indexList = listView.selectedIndexes()
        if not indexList:
            return
        selection = indexList[0].data()

        nowOrFileName = dict[selection] #if now: restores latest. if a time restores to that time

        #if yes, force, if no??
        force = False
        if os.listdir(dest): #empty directory?
            mb = QMessageBox()
            mb.setWindowTitle("Warning")
            mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            mb.setText("Selected folder has files in it. \n"
                       "Existing data will be overwritten.\n"
                       "Are you sure you want to continue?")
            retval = mb.exec_()


            if retval == QMessageBox.No:
                return
            force = True

        if force:
            cmd = "rdiff-backup --force"
        else:
            cmd = "rdiff-backup"

        if nowOrFileName == "now":
            command = cmd + ' -r now "{}" "{}"'.format(backupSource, dest) #-r stands for restore
        else:
            fullSrcPath = os.path.join(backupSource, nowOrFileName)
            command = cmd + ' "{}" "{}"'.format(fullSrcPath, dest)
            # does this need the -r?. i think it can tell fromthe filename

        # print(command)

        completedProcess = rdbcommands.executeCmd(command)

        if completedProcess.returncode != 0:
            box = QMessageBox()
            box.setWindowTitle("Error")
            box.setText(completedProcess.__str__())
            box.exec_()

        else:
            box = QMessageBox()
            box.setWindowTitle("Success")
            box.setText("Restored \n{} \nto \n{}".format(backupSource, dest))
            box.exec_()

        #this will overwrite everything in the target directory. be careful!kkkkk
        #also works with files
        # rdiff-backup --force -r now backupDirectory destination
        # rdiff-backup location/filename.2003-03-.....dif.gz destination


    def _getDestPath(dialog, restoreDestinationEdit):
        """
        @type restoreDestinationEdit QLineEdit
        """
        home = expanduser("~")
        path = QFileDialog.getExistingDirectory(dialog, "Choose restore path", home)
        restoreDestinationEdit.setText(path)
        return path



    modelIndexList = parentListView.selectedIndexes()
    if not modelIndexList:
        return
    backupPath = modelIndexList[0].data()




    dialog = QDialog(parent)
    dialog.setWindowTitle(backupPath + " Restore Entire directory")
    dialog.resize(400,200)
    dialog.setModal(True)
    # print(parentListView.selectedIndexes())
    # parentListView.selectionModel()
    # create some rdb examplse... oh maybe just the abcd folders on desktop


    # print(path)
    fullPath = os.path.join(backupPath, "rdiff-backup-data")
    # print (fullPath)
    options = glob.glob(fullPath + os.sep + "increments.*.dir")

    # print(options)



    grid = QGridLayout()
    dialog.setLayout(grid)
    model = QStandardItemModel()
    listView = QListView()
    listView.setFixedSize(400,150)
    listView.setModel(model)
    model.appendRow(QStandardItem("Now"))


    optionDict = {}
    for o in options:
        date = os.path.basename(o)[11:-10]
        dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        timeString = dt.strftime("%Y-%b-%d      %I:%M %p")
        optionDict.update({timeString: o})
        model.appendRow(QStandardItem(timeString))
        #todo

        # datetime.strptime()
        # increments.2016-06-08T18:24:57-06:00.dir
    optionDict.update({"Now": "now"})

    destLabel = QLabel()
    destLabel.setText("Destination Folder (Empty folder recommended)")

    restoreDestinationEdit = QLineEdit()
    restoreDestinationEdit.setReadOnly(True)
    restoreDestinationEdit.setToolTip("Select area to restore files to")

    restoreBtn = QPushButton()
    restoreBtn.setText("Restore")
    restoreBtn.clicked.connect(partial(restoreSelection,listView, optionDict, backupPath, restoreDestinationEdit))

    browseBtn = QPushButton()
    browseBtn.setText("...")
    browseBtn.clicked.connect(partial(_getDestPath, dialog, restoreDestinationEdit))


    grid.addWidget(listView, 0,0, Qt.AlignHCenter)
    grid.addWidget(destLabel, 1,0)
    grid.addWidget(restoreDestinationEdit, 2,0)
    grid.addWidget(browseBtn, 2,1)
    grid.addWidget(restoreBtn, 3,0, Qt.AlignHCenter)













    dialog.exec_()

