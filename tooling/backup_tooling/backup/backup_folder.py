from os.path import exists
from os import walk 
from re import findall
from typing import List

from backup import Backup


class BackupFolder:
    rootFilePath: str
    backupFiles: List[str]
    newestBackup: str

    def __init__(self, filePath): 
        # I have no idea if this'll work, but this should 
        # convert D:/x/y (which isn't a valid PY string) to D://x//y
        self.rootFilePath = filePath.replace("\\", "\\" + "\\") 

        if (self.rootFilePath.endswith("/backups") != True):
            self.rootFilePath += "/backups"

        # Check to see if the file is validish 
        if (exists(filePath) != True): 
            raise ValueError("The provided file path {} is not a valid file path. Please double check your path".format(filePath))

        # Generate a list of files in said directory 
        self.backupFiles = self.locateBackupFiles()
        self.newestBackup = self.findNewestBackup()

    # Scheme: Insights-Capture-${timestamp}
    def locateBackupFiles(self): 
        backupFiles = []
        for _, _, files in walk(self.rootFilePath):
            for file in files:
                if (len(findall("^Insights-Capture-\d{10,15}.json$", file)) > 0):
                    backupFiles.append(file) 


        return backupFiles
    
    def findNewestBackup(self) -> str:
        def sortingAlgoOrSomeShit(item): 
            try: 
                return int(item.split("-")[2][:-5])

            except:
                raise ValueError("{} had an incorrect filename pattern".format(item)) 

        if len(self.backupFiles) == 0: return ''        
        return sorted(self.backupFiles, key=sortingAlgoOrSomeShit, reverse=True)[0]

    def loadBackup(self, fileName: str) -> Backup:
        return Backup("{}/{}".format(self.rootFilePath, fileName))