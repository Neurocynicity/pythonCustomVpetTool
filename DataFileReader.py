import pathlib
from abc import ABC, abstractmethod
from re import sub

class DataFileReader(ABC):
    def ReadAnimationDataFile(self, pathToDataFile : pathlib.Path):
        datafile = pathToDataFile.open()
        readLine = datafile.readline()
        while readLine != "":
            removedComments = readLine.split("#")[0]
            parts = removedComments.split(":", 1)
            command = sub(r"[^\w\d]", "", parts[0].lower()) # small regex to remove non letter/ number characters

            if len(parts) > 1:
                self.HandleDataFromDataFile(command, parts[1])

            readLine = datafile.readline()

        if self.updatesPerFrame == 0: # if we still don't have a value for updates a frame
            self.updatesPerFrame = 1 # then use 1 as default
        pass

    @abstractmethod
    def HandleDataFromDataFile(self, varName : str, value : str):
        pass

    pass