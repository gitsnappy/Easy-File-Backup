import schedule
"""note on how schedule module works
if you schedule a task to run daily at 7:00 PM and it is currently 7:00 PM or later, the first execution of the task will be
tomorrow at 7:00 PM.  after that, if the run_pending() method is not ran until 7:35 PM a few days later, the job will still run,
but only once
"""
import getpass
# stream = open("user.txt","a")
# stream = open("/home/v/PycharmProjects/easybackup/user.txt","a")
# print(getpass.getuser())
# stream.write(getpass.getuser())
# stream.close()

from datetime import datetime
import time
import jsonfiles
import rdbcommands
import os
import logger
import task
import shlex
from subprocess import run
from subprocess import CompletedProcess

log = logger.setupLogger("commands")



def runJobs():
    schedule.run_pending()
    if schedule.next_run() is None:
        return 60*60

    delta = schedule.next_run() - datetime.now()
    secondsUntilNextRun = min(delta.total_seconds(), 60*60) #poll every hour
    return secondsUntilNextRun

def executeCommand(cmd):
    args = shlex.split(cmd)
    completedProcess = run(args)
    log.info(completedProcess.__str__())


def checkSourceFiles(selectedTask, selectedProfile):
    """
    @type selectedTask task.Task
    """
    # if a file has since been deleted, the command will fail
    # just log it and keep going

    files = selectedTask.source.split(", ")
    for f in files:
        if not os.path.exists(f):
            log.warning("{} source does not exist:\nTask: {}\nProfile:{}".format(selectedTask.source, selectedTask ,selectedProfile))


def scheduleJob(selectedTask, selectedProfile):
    checkSourceFiles(selectedTask,selectedProfile)
    cmd = rdbcommands.createRdiffCommand(selectedTask)
    interval = int(selectedProfile.interval)
    taskTime = selectedProfile.startDateTime.toString("hh:mm")
    minuteTime = selectedProfile.startDateTime.toString(":mm")

    log.info("Scheduled {}\n with profile {}".format(selectedTask, selectedProfile))
    if selectedProfile.period == "Hour(s)":
        job = schedule.every(interval).hours.at(minuteTime).do(executeCommand, cmd)
        # job = schedule.every(20).seconds.do(executeCommand, cmd) #for debugging
    elif selectedProfile.period == "Day(s)":
        job = schedule.every(interval).days.at(taskTime).do(executeCommand, cmd)
    elif selectedProfile.period == "Week(s)":
        # at command is not supported for weeks
        job = schedule.every(interval).weeks.do(executeCommand, cmd)
    else:
        log.error("Expected Hours, Days, or Weeks for interval option")
        job = None
    return job

def getProfileListAndTaskList():
    profiles = jsonfiles.getProfileListFromFile()
    taskList = jsonfiles.getTaskListFromFile()
    return (profiles, taskList)

def addTaskJobs():
    """Get Tasks from file, schedule jobs if is after start day"""
    profileAndTaskLists = getProfileListAndTaskList()
    profiles = profileAndTaskLists[0]
    taskList = profileAndTaskLists[1]

    for t in taskList:
        p = [x for x in profiles if x.name == t.profileName][0]
        profileDateTime = p.startDateTime.toPyDateTime()
        day = profileDateTime.replace(hour=0,second=0,minute=0)

        if (datetime.now() >= day):
            scheduleJob(t, p)


def runScheduler():
    log.info("Started Scheduler")
    oldStamps = jsonfiles.getTimeStamps()
    addTaskJobs() #get stuff on startup of service
    while True:
        currentStamps = jsonfiles.getTimeStamps()
        if currentStamps != oldStamps:
            log.info("Profile or Task has changed, resetting schedule")
            schedule.clear()
            oldStamps = currentStamps
            addTaskJobs()

        secondsUntilNextRun = runJobs()
        time.sleep(secondsUntilNextRun)

if __name__ == '__main__':
    # stream = open(f, 'a')
    # stream.write(datetime.now())
    runScheduler()
