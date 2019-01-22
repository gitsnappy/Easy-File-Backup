import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import functools
from typing import List

defaultProfileName = "New Profile"
import jsonfiles

# if not os.path.isfile("profiles.json"):

#load structure beginning of program
#add New profile at beginning

#program modifies file & data structures whenever "update" is hiht

class LabelTime(QWidget):
    def __init__(self, labelText):
        super().__init__()
        widgetLabel = QLabel()
        widgetLabel.setText(labelText)
        self.dateEdit = QDateTimeEdit()


        layout = QHBoxLayout()
        layout.addWidget(widgetLabel)
        layout.addWidget(self.dateEdit)
        self.setLayout(layout)


class LabelPeriod(QWidget):
    def __init__(self, labelText, options):
        super().__init__()
        widgetLabel = QLabel()
        widgetLabel.setText(labelText)
        self.box = QComboBox()
        self.box.addItems(options)

        self.spin = QSpinBox()
        self.spin.setRange(1,100)
        self.spin.setValue(1)


        layout = QHBoxLayout()
        layout.addWidget(widgetLabel)
        layout.addWidget(self.spin)
        layout.addWidget(self.box)

        self.setLayout(layout)


class LabelEdit(QWidget):
    def __init__(self, labelText):
        super().__init__()
        widgetLabel = QLabel()
        widgetLabel.setText(labelText)
        self.edit = QLineEdit()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(widgetLabel)
        layout.addWidget(self.edit)
        self.setLayout(layout)
        # self.show()

class Profile():

    def __init__(self, name = None, startDateTimeString = None, interval = None, period = None):
        self.name = name
        self.startDateTime = QDateTime.fromString(startDateTimeString)
        self.interval = interval
        self.period = period

    def __str__(self):
        return "{} {} every {} {} ".format(self.name, self.startDateTime.toString(), self.interval, self.period)

def getDefaultProfile():
    profiles = []
    default = Profile(defaultProfileName, "Mon May 23 23:25:38 2016", interval=1, period="Day(s)")
    profiles.append(default)
    return profiles


profiles = getDefaultProfile()
saved = jsonfiles.getProfileListFromFile()
profiles.extend(saved)

def getProfiles() -> List[Profile]:
    return profiles[1:]


def setSelectedItem(box, item):
    #todo error checking
    box.setCurrentIndex(box.findText(item))


def openProfileMenu(parent):
    def getFormDataAsProfile():
        profile = Profile()
        profile.name = profileNameEdit.edit.text()
        profile.startDateTime = dateTimeLabel.dateEdit.dateTime()

        profile.interval = periodLabelBox.spin.value()
        profile.period = periodLabelBox.box.currentText()
        return profile

    def deleteProfile():
        selectedProfileName = selectProfileBox.currentText()
        if selectedProfileName != defaultProfileName:
            for index, item in enumerate(profiles):
                if item.name == selectedProfileName:
                    profiles.remove(item)
                    break
            selectProfileBox.removeItem(index)

        #update profiles file
        jsonfiles.writeProfilesToFile(profiles[1:]) # don't include default

    def createProfile():
        profile = getFormDataAsProfile()


        namesUnique = not any([x.name for x in profiles if x.name == profile.name])
        notDefault = selectProfileBox.currentText() != defaultProfileName
        # name must be unique, throw error

        #Update
        selectedProfileName = selectProfileBox.currentText()
        if notDefault:
            for index, item in enumerate(profiles):
                if item.name == selectedProfileName:
                    profiles[index] = profile
                    selectProfileBox.setItemText(index, profile.name) #updating the name in selection

        elif not namesUnique:
            mb = QMessageBox()
            mb.setText("Profile name must be unique")
            mb.exec_()
        #New
        elif not profile.name:
            mb = QMessageBox()
            mb.setText("Profile name must have at least one character")
            mb.exec_()

        else:
            profiles.append(profile)
            selectProfileBox.addItem(profile.name)
            setSelectedItem(selectProfileBox, profile.name)
            #TODO: check ignores for validity

        #update profiles file
        jsonfiles.writeProfilesToFile(profiles[1:]) # don't include default

    def updateFormData():
        #Updates text fields & boxes with information from the profile
        profileName = selectProfileBox.currentText()
        profile = [x for x in profiles if x.name == profileName][0]

        profileNameEdit.edit.setText(profile.name)
        dateTimeLabel.dateEdit.setDateTime(profile.startDateTime)
        dateTimeLabel.dateEdit.setDateTime(profile.startDateTime)
        periodLabelBox.spin.setValue(int(profile.interval))

        setSelectedItem(periodLabelBox.box, profile.period)

        if (profile.name == defaultProfileName):
            createBtn.setText("Create")
            deleteBtn.setEnabled(False)
        else:
            createBtn.setText("Update")
            deleteBtn.setEnabled(True)


    dialog = QDialog(parent)
    dialog.setWindowTitle("Profiles")
    dialog.resize(500,300)
    dialog.setModal(True)
    grid = QGridLayout()
    dateTimeLabel = LabelTime("Start Time")

    times = [(str(x) + "000")[:4] for x in range(24)]

    # profiles = getDefaultProfile()
    # saved = profilejson.getProfileListFromFile()
    # profiles.extend(saved)

    # updateProfilesFile(profiles)


    names = [x.name for x in profiles]

    selectProfileBox = QComboBox()
    selectProfileBox.addItems(names)

    selectProfileBox.currentIndexChanged.connect(updateFormData)
    # ???

    profileNameLabel = QLabel()
    profileNameLabel.setText("Profile Name")
    profileName = QLineEdit()

    profileNameEdit = LabelEdit("Profile Name")



    createBtn = QPushButton()
    createBtn.setText("Create")
    createBtn.clicked.connect(createProfile)
    deleteBtn = QPushButton()
    deleteBtn.setText("Delete")
    deleteBtn.clicked.connect(deleteProfile)
    exitBtn = QPushButton()
    exitBtn.setText("Exit")
    exitBtn.clicked.connect(dialog.close)

    periods = ["Hour(s)","Day(s)","Week(s)"]
    periodLabelBox = LabelPeriod("Backup every", periods)

    # orderDict = {periodLabelBox:0, timeBoxLabel:1, ignores:2, profileNameEdit: 3, createBtn:4}
    # print (orderDict[0])

    grid.addWidget(selectProfileBox, 0, 0)
    grid.addWidget(profileNameEdit, 1,0)
    grid.addWidget(dateTimeLabel, 2,0)
    grid.addWidget(periodLabelBox, 3,0)
    grid.addWidget(createBtn,5,0)
    grid.addWidget(deleteBtn,6,0)
    grid.addWidget(exitBtn,7,0)

    dialog.setLayout(grid)
    updateFormData()
    dialog.exec_()


if __name__ == '__main__':
  app = QApplication(sys.argv)
  openProfileMenu(QMainWindow())
