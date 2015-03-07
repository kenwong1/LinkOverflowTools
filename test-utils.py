import os

#
# This file will return all the test assets used for the unit tests
#


def getAWSSettings():
    return os.path.expanduser("~/.aws.settings")

def getInstanceConfig():
    return 'instance.config'

def getFileNotReadableByOwner():
    return "notReadableByOwner.file"

def getFileReadableByOthers():
    return "readableByOthers.file"