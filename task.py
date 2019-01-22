
class Task():
    SingleFile = "File"
    MultipleFiles = "Multiple Files"
    Directory = "Directory"

    def __init__(self, source, fileType, dest, profileName):
        self.source = source
        self.fileType = fileType
        self.dest = dest
        self.profileName = profileName


    def __str__(self):
        return "{} {} {} {}".format(self.source, self.fileType, self.dest, self.profileName)
