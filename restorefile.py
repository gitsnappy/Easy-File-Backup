from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import glob
from datetime import datetime
from functools import partial
import task
import rdbcommands


class customFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__()




    def data(self, index, role=None):
        """
        @type index QModelIndex
        @type role int
        """
        if not index.isValid():
            return None



        # index.row()
        data = QFileSystemModel.data(self, index, role)
        # self.fileName(index)

        # index.row().


        if role == Qt.DisplayRole and index.column() == 0: #if data is filename
            if index.sibling(index.row(), 2).data() != 'Folder':
                #filename.2016-....06:00.diff.gz
                if data.endswith(".gz"):
                    filename = data[:data.find(".")]
                    data = data[data.find(".") + 1:-14]
                #foldername.2016...06:00.dir
                elif data.endswith(".dir"):
                    filename = data[:data.find(".")]
                    data = data[data.find(".") + 1: -10]
                    # print(filename)
                    # print(data)


                else:
                    pass
                    # print("what")
                # print( )
                # print (data)


                dt = datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
                data = dt.strftime("{}         %Y-%b-%d      %I:%M %p".format(filename))
                # optionDict.update({timeString: o})

            # print(data)

            # print(index.parent().column())
            # print(data + " index {}".format(index.column()))
            # print("okay")
        return data

#restore previous
def restoreFileOrDirectory(parent, parentListView):
    """
    @type parent QDialog
    @type parentListView: QListView
    """
    modelIndexList = parentListView.selectedIndexes()
    if not modelIndexList:
        return
    backupPath = modelIndexList[0].data()

    fullPath = os.path.join(backupPath, "rdiff-backup-data/increments")

    dialog = QDialog(parent)
    dialog.setWindowTitle(backupPath + " Restore previous version of a file or folder")
    dialog.resize(600,300)
    dialog.setModal(True)

    grid = QGridLayout()
    dialog.setLayout(grid)
    # model = QStandardItemModel()
    # model = QFileSystemModel()
    model = customFileSystemModel()
    filters = []
    filters.append("*.diff.gz")
    filters.append("*.dir")

    model.setNameFilters(filters)
    model.setNameFilterDisables(False)
    model.setRootPath(fullPath)

    treeView = QTreeView()
    treeView.setModel(model)
    treeView.hideColumn(1)
    treeView.hideColumn(2)
    treeView.hideColumn(3)
    treeView.setRootIndex(model.index(fullPath))

    destLabel = QLabel()
    destLabel.setText("Destination:\n"
                      "  Empty folder recommended for folder sources\n"
                      "  Empty file recommended for file sources")

    restoreDestinationEdit = QLineEdit()
    restoreDestinationEdit.setReadOnly(True)
    restoreDestinationEdit.setToolTip("Select area to restore files to")

    fileFolderCombo = QComboBox()
    fileFolderCombo.addItem(task.Task.SingleFile)
    fileFolderCombo.addItem(task.Task.Directory)
    fileFolderCombo.setCurrentIndex(0)

    browseBtn = QPushButton()
    browseBtn.setText("...")
    #try this see if it actually works or if the data is too mangled
    browseBtn.clicked.connect(partial(_getDestPathPrevious, dialog, model, treeView, restoreDestinationEdit, fileFolderCombo))

    restoreBtn = QPushButton()
    restoreBtn.setText("Restore")
    restoreBtn.clicked.connect(partial(restorePrevious, treeView, model, backupPath, restoreDestinationEdit))


    grid.addWidget(treeView, 0,0)  #Qt.AlignHCenter
    grid.addWidget(destLabel, 1,0)
    grid.addWidget(restoreDestinationEdit, 2,0)
    grid.addWidget(fileFolderCombo, 2,1)
    grid.addWidget(browseBtn, 2,2)
    grid.addWidget(restoreBtn, 3,0)


    dialog.exec_()


def _getDestPathPrevious(dialog, model, treeView, restoreDestinationEdit, fileFolderCombo):
    """
    @type treeView QTreeView
    @type model QFileSystemModel
    @type restoreDestinationEdit QLineEdit
    @type fileFolderCombo QComboBox
    """
    modelIndexList = treeView.selectedIndexes()
    if not modelIndexList:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText("You must select a source first")
        box.exec_()
        return

    backupSelection = model.filePath(modelIndexList[0])
    home = os.path.expanduser("~")
    text = fileFolderCombo.currentText()
    if text == task.Task.SingleFile:
        path = QFileDialog.getOpenFileName(dialog, "Choose restore destination", home)
    elif text == task.Task.Directory:
        path = QFileDialog.getExistingDirectory(dialog, "Choose restore destination", home)
    restoreDestinationEdit.setText(path)
    return path


def _getDestPath(dialog, model, treeView, restoreDestinationEdit):
    """
    @type treeView QTreeView
    @type model QFileSystemModel
    @type restoreDestinationEdit QLineEdit
    """
    modelIndexList = treeView.selectedIndexes()
    if not modelIndexList:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText("You must select a source first")
        box.exec_()
        return

    backupSelection = model.filePath(modelIndexList[0])

    home = os.path.expanduser("~")
    if os.path.isdir(backupSelection):
        path = QFileDialog.getExistingDirectory(dialog, "Choose restore destination Empty folder recommended", home)
    else:
        path = QFileDialog.getOpenFileName(dialog, "Choose restore destination Empty file recommended",home)
    restoreDestinationEdit.setText(path)
    return path


#restore from diff.gz
def restorePrevious(treeView, model, backupPath, restoreDestinationEdit):
    """
    @type treeView QTreeView
    @type model QFileSystemModel
    @type backupPath String
    @type restoreDesinationEdit QLineEdit
    """
    modelIndexList = treeView.selectedIndexes()
    if not modelIndexList:
        return
    # backupSelection = modelIndexList[0].data()
    backupSelection = model.filePath(modelIndexList[0])
    dest = restoreDestinationEdit.text()

    if not dest:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText("You must select a destination")
        box.exec_()
        return

    force = False
    mb = QMessageBox()
    mb.setWindowTitle("Warning")
    mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    if os.path.isdir(dest):
        if os.listdir(dest): #empty directory?
            warningText = ("Selected folder has files in it. \n"
                   "Existing data will be overwritten.\n"
                   "Are you sure you want to continue?")
            mb.setText(warningText)
            retval = mb.exec_()
            if retval == QMessageBox.No:
                return
            force = True

    else:
        if os.path.isfile(dest) and os.stat(dest).st_size != 0:
            warningText = ("Selected file is not empty\n"
                           "Existing data will be overwritten.\n"
                           "Are you sure you want to continue?")
            mb.setText(warningText)
            retval = mb.exec_()
            if retval == QMessageBox.No:
                return
            force = True

    if force:
        cmd = "rdiff-backup --force"
    else:
        cmd = "rdiff-backup"

    cmd += " -r now '{}' '{}'".format(backupSelection, dest)
    # print(cmd)

    completedProcess = rdbcommands.executeCmd(cmd)
    if completedProcess.returncode != 0:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText(completedProcess.__str__())
        box.exec_()

    else:
        box = QMessageBox()
        box.setWindowTitle("Success")
        box.setText("Restored {} to \n{}".format(backupSelection, dest))
        box.exec_()




def restoreSelection(treeView, model, backupPath, restoreDestinationEdit):
    """
    @type treeView QTreeView
    @type model QFileSystemModel
    @type backupPath String
    @type restoreDestinationEdit QLineEdit
    """
    modelIndexList = treeView.selectedIndexes()
    if not modelIndexList:
        return
    # backupSelection = modelIndexList[0].data()
    backupSelection = model.filePath(modelIndexList[0])

    dest = restoreDestinationEdit.text()
    #selected destination
    if not dest:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText("You must select a destination")
        box.exec_()
        return

    if "rdiff-backup-data" in backupSelection:
        box = QMessageBox()
        box.setText("Files in the rdiff-backup-data folder are not a valid selection")
        box.exec_()
        return

    force = False
    mb = QMessageBox()
    mb.setWindowTitle("Warning")
    mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    # mb.setText("Selected folder has files in it. \n"
    #            "Existing data will be overwritten.\n"
    #            "Are you sure you want to continue?")


    if os.path.isdir(dest):
        if os.listdir(dest): #empty directory?
            warningText = ("Selected folder has files in it. \n"
                   "Existing data will be overwritten.\n"
                   "Are you sure you want to continue?")
            mb.setText(warningText)
            retval = mb.exec_()
            if retval == QMessageBox.No:
                return
            force = True
    else:
        if os.path.isfile(dest) and os.stat(dest).st_size != 0:
            warningText = ("Selected file is not empty\n"
                          "Existing data will be overwritten.\n"
                          "Are you sure you want to continue?")
            mb.setText(warningText)
            retval = mb.exec_()
            if retval == QMessageBox.No:
                return
            force = True

    if force:
        cmd = "rdiff-backup --force"
    else:
        cmd = "rdiff-backup"

    cmd += " -r now '{}' '{}'".format(backupSelection, dest)


    # print(cmd)
    completedProcess = rdbcommands.executeCmd(cmd)
    if completedProcess.returncode != 0:
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText(completedProcess.__str__())
        box.exec_()

    else:
        box = QMessageBox()
        box.setWindowTitle("Success")
        box.setText("Restored {} to \n{}".format(backupSelection, dest))
        box.exec_()
    #todo log result to log
    # print(completedProcess)





def clearEdit(edit):
    """
    @type edit QLineEdit
    """
    edit.setText("")


#now
def restoreLatest(parent, parentListView):
    """
    @type parent QDialog
    @type parentListView: QListView
    """
    modelIndexList = parentListView.selectedIndexes()
    if not modelIndexList:
        return
    backupPath = modelIndexList[0].data()


    dialog = QDialog(parent)
    dialog.setWindowTitle(backupPath + " Restore latest file or folder")
    dialog.resize(600,300)
    dialog.setModal(True)

    grid = QGridLayout()
    dialog.setLayout(grid)
    model = QFileSystemModel()
    model.setRootPath(backupPath)

    #there's no easy way to filter out a folder using setNameFilters or a QSortFilterProxyModel



    treeView = QTreeView()
    treeView.setModel(model)

    # treeView.hideColumn(1)
    # treeView.hideColumn(2)
    # treeView.hideColumn(3)


    treeView.setRootIndex(model.index(backupPath))

    destLabel = QLabel()
    destLabel.setText("Destination:\n"
                      "  Empty folder recommended for folder sources\n"
                      "  Empty file recommended for file sources")
    restoreDestinationEdit = QLineEdit()
    restoreDestinationEdit.setReadOnly(True)
    restoreDestinationEdit.setToolTip("Select area to restore files to")

    browseBtn = QPushButton()
    browseBtn.setText("...")
    browseBtn.clicked.connect(partial(_getDestPath, dialog, model, treeView, restoreDestinationEdit))

    selectionModel = treeView.selectionModel()
    selectionModel.selectionChanged.connect(partial(clearEdit, restoreDestinationEdit))

    restoreBtn = QPushButton()
    restoreBtn.setText("Restore")
    restoreBtn.clicked.connect(partial(restoreSelection, treeView, model, backupPath, restoreDestinationEdit))

    grid.addWidget(treeView, 0,0)
    grid.addWidget(destLabel, 1,0)
    grid.addWidget(restoreDestinationEdit, 2,0)
    grid.addWidget(browseBtn, 2,1)
    grid.addWidget(restoreBtn, 3,0)




    dialog.exec_()




