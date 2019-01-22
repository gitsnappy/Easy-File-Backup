import task
import os
from subprocess import run
from subprocess import CompletedProcess
import shlex
import logging

includeLocation = "includes"
restoreLocation = "restores"

restorePath = os.path.join(restoreLocation, "restore.txt")


def executeCmd(cmd) -> CompletedProcess:
    """
    @type cmd string
    """
    args = shlex.split(cmd)
    # print(args)
    completedProcess = run(args)

    log = logging.getLogger("base")
    log.info(completedProcess.__str__())

    # print("return code {}".format(completedProcess.returncode))
    # print("stderr {}".format(completedProcess.stderr))
    # print("sdtout: {}".format(completedProcess.stdout))

    return completedProcess
    # CompletedProcess.

def createRdiffCommand(backupTask):
    """
    @type backupTask: task.Task
    """
    if backupTask.fileType == task.Task.SingleFile:
        return _makeFileRdiffCommand(backupTask, False)

    elif backupTask.fileType == task.Task.Directory:
        return _makeDirRdiffCommand(backupTask)

    elif backupTask.fileType == task.Task.MultipleFiles:
        return _makeFileRdiffCommand(backupTask, True)
    else:
        return None

def _touchIncludeDirectory():
    if not os.path.isdir(includeLocation):
        os.mkdir(includeLocation)

def _touchRestoreDirectory():
    if not os.path.isdir(restoreLocation):
        os.mkdir(restoreLocation)


def _makeFileRdiffCommand(backupTask, isMultiple):
    _touchIncludeDirectory()
    source = backupTask.source
    dest = backupTask.dest
    # os.chdir()
    includeFileList = os.path.join(includeLocation, "templist")
    abspath = os.path.abspath(includeFileList)

    if isMultiple:
        source = source.replace(", ", "\n")

    # write files to backup
    with open(includeFileList, 'w') as f:
        f.write(source)

    # get directory name where the file is located
    firstFile = source
    if isMultiple:
        firstFile = source[:source.find("\n")]

    sourceDir = os.path.dirname(firstFile)

    return "rdiff-backup --include-filelist '{}' --exclude '**' '{}' '{}'".format(abspath, sourceDir, dest)

def _makeDirRdiffCommand(backupTask):
    return "rdiff-backup '{}' '{}'".format(backupTask.source, backupTask.dest)


def getRestorePathList():
    paths = []
    if os.path.isfile(restorePath):
        f = open(restorePath, 'r')
        for line in f:
            paths.append(line.strip())
        f.close()
    return paths

def saveRestorePaths(tasks):
    """
    @type tasks: list[task.Task]
    """
    _touchRestoreDirectory()
    paths = getRestorePathList()

    destPaths = []
    for p in paths:
        loc = os.path.join(p, "rdiff-backup-data")
        if os.path.isdir(loc):
            destPaths.append(p)

    for t in tasks:
        destPaths.append(t.dest)
    destPaths = list(set(destPaths))

    f = open(restorePath, 'w')
    for x in destPaths:
        f.write(x + "\n")
    f.close()










#rdiff-backup host.net::/remote-dir/rdiff-backup-data/increments/file.2003-03-05T12:21:41-07:00.diff.gz local-dir/file


"""

"""



