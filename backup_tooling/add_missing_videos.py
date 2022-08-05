from os import walk, mkdir
from os.path import join, exists
from time import time
from backup.backup_file import Backup

from common.logging import ConsoleInterface
from backup import BackupFolder
log = ConsoleInterface()

# TODO 
#     + We should probably use addMissingVideosToBackup in main, instead of re-using 
#       the same code, but I'm lazy rn

def main(): 
    # Get the latest back up
    log.log("Fetching latest backup...")
    backupPath = log.getInput("What's the path to the folder you're using for Insights Capture")

    # Validate is folder
    backupContainer = BackupFolder(backupPath)
    log.log("Latest backup file is \"{}\", going to use it as a basis for videos".format(backupContainer.newestBackup))

    # Generate the backup
    backup = backupContainer.loadBackup(backupContainer.newestBackup)
    
    # Generate a list of videos that are currently in the backup folder 
    def isVideoAndIsntInBackup(object: str): 
        if (object.endswith('.mp4') != True): return False 
        return False if backup.videoExists(join(backupPath, object)) else True # Pretty fucking complicated way of doing this, someone fix it

    files = list(walk(backupPath))[0][2]
    missingFiles = list(filter(isVideoAndIsntInBackup, files))
    
    videoCount = backup.videoCount()
    log.log("Backup contains {} videos...".format(videoCount))
    log.log("The backup is missing {} videos from the path {}".format(len(missingFiles), backupPath))
    log.log("Creating a new backup file that contains the missing {} videos...".format(len(missingFiles)))

    # Time to do some FUCKED shit :agony: 
    for file in missingFiles: 
        print("\t Handling file {}...".format(file), end="", flush=True)
        backup.addVideo(backupPath, file)
        print("DONE")


    log.log("New backup populated with missing videos, saving backup to disk")
    if exists("./generated_backups") != True: 
        mkdir("./generated_backups")

    finalPath = "./generated_backups/generated_backup_{}.json".format(str(round(time() * 1000)))
    backup.saveToDisk(finalPath)
    log.log("Saved backup to: {}".format(finalPath))


def addMissingVideosToBackup(
    inputBackupFilepath:str, 
    outputFilePath: str, 
    pathToICVideoLibary: str, 
    fileEndings = ['mp4']
): 
    backup = Backup(inputBackupFilepath)

    def isVideoAndIsntInBackup(object: str): 
        for endings in fileEndings: 
            if (object.endswith(endings) != True): return False 
            if backup.videoExists(join(pathToICVideoLibary, object)): return False 

            return True

    files = list(walk(pathToICVideoLibary))[0][2]
    missingFiles = list(filter(isVideoAndIsntInBackup, files))

    for file in missingFiles: 
        backup.addVideo(pathToICVideoLibary, file)

    backup.saveToDisk(outputFilePath)

if __name__ == "__main__":
    log.logTitle()
    main()
    print("\n") # looks pretty roowowowowoowowowowo