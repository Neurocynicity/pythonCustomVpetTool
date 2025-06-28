from Utility import localPath
from enum import Enum

class MessageLevel:
    ERROR   = 0b00000001
    WARNING = 0b00000010
    MESSAGE = 0b00000100

class LoggingLevel:
    ERRORS   = 0b00000001
    WARNINGS = 0b00000010
    MESSAGES = 0b00000100
    ERRORS_AND_WARNINGS = 0b00000011
    ALL = 0b00000111

class Logger:
    instance = None

    def __init__(self, loggingLevel : LoggingLevel):
        Logger.instance = self
        self.loggingLevel = loggingLevel

        self.datafile = open(localPath.joinpath("output.txt"), "w")
        pass

    def Log(self, messageLevel : MessageLevel, text : str):

        if messageLevel & self.loggingLevel == 0:
            return
        
        prefix = ""
        
        if messageLevel == MessageLevel.ERROR:
            prefix = "[ERROR] "
        elif messageLevel == MessageLevel.WARNING:
            prefix = "[WARNING] "
        elif messageLevel == MessageLevel.MESSAGE:
            prefix = "[MESSAGE] "
        
        self.datafile.write(prefix + text + '\n')
        print(prefix + text)

        pass