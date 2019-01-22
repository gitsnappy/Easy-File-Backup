import os
import task
from typing import List

profileLocation = "profiles"
if not os.path.isdir(profileLocation):
    os.mkdir(profileLocation)

fileName = "profiles.json"
profilePath = os.path.join(profileLocation, fileName)


taskLocation = "tasks"
if not os.path.isdir(taskLocation):
    os.mkdir(taskLocation)

fileName = "tasks.json"
taskPath = os.path.join(taskLocation, fileName)


import json


def getProfileDict(profile):
    d = {"name" : profile.name  ,
         "startDateTime" : profile.startDateTime.toString(),
         "interval" : profile.interval,
         "period" : profile.period}
    return d

def writeProfilesToFile(profiles):
    l = []
    for profile in profiles:
        d = getProfileDict(profile)
        l.append(d)

    data = { "profile" : l}

    with open(profilePath, 'w') as outfile:
        json.dump(data, outfile)

# def getProfileListFromFile() -> List[profile.Profile]:
def getProfileListFromFile():
    import profile # get latest
    profileList = []
    with open(profilePath) as data_file:
        js = json.load(data_file)
    l = js["profile"]
    ######
    for item in l:
        p = profile.Profile(item["name"], item["startDateTime"], item["interval"], item["period"])
        profileList.append(p)

    return profileList

##########################################################33
def getTimeStamps():
    """
    Provides timestamps of files used by service
    :return: [profileStamp, taskStamp]
    """
    filesToCheck = [profilePath, taskPath]
    l = []
    for f in filesToCheck:
        stamp = os.stat(f).st_mtime
        l.append(stamp)
    return l


def getTaskDict(t):
    d = {
        "source" : t.source,
         "fileType" : t.fileType,
         "dest" : t.dest,
         "profileName" : t.profileName #get profile info from profile file
         }
    return d

def writeTasksToFile(tasks):
    l = []
    for t in tasks:
        d = getTaskDict(t)
        l.append(d)

    data = { "task" : l}

    with open(taskPath, 'w') as outfile:
        json.dump(data, outfile)

def getTaskListFromFile() -> List[task.Task]:
    taskList = []
    if os.path.exists(taskPath):
        with open(taskPath) as data_file:
            js = json.load(data_file)
        l = js["task"]
        for item in l:
            t = task.Task(item["source"], item["fileType"], item["dest"], item["profileName"])
            taskList.append(t)

    return taskList






