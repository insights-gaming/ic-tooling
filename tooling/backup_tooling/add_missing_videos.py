from os import walk, mkdir, getcwd
from os.path import join, exists
from time import time
from sys import argv
from backup.backup_file import Backup


from common.logging import ConsoleInterface
from backup import BackupFolder, createNewBackup
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
        return object.endswith('.mp4') and not backup.videoExists(join(backupPath, object))

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


def runInDirectory():
    directory = getcwd()
    log.log("Checking to see if a backup folder and its contents exists: {}".format(directory))

    # Check to see if a backup folder exists 
    currentBackup = None
    if exists("./backups") != True:
        log.log("Backup folder didn't exist, gonna create a new one and populate it")
        mkdir("./backups")

        # Write the base backup 
        currentBackup = createNewBackup("./backups/Insights-Capture-{}.json".format(int(round(time() * 1000))))

    else: 
        log.log("Backup folder was found in this folder, crazy man. Gonna use it tho-")
        log.log("If you see issues here, you might want to just move the backup folder to another folder for now.")
        backupContainer = BackupFolder('./')
        currentBackup = backupContainer.newestBackup

    # Now that we have a backup, lets open her up and populate 
    def isVideoAndIsntInBackup(vod: str): 
        if (vod.endswith('.mp4') != True): return False 
        return False if currentBackup.videoExists(vod) else True # Pretty fucking complicated way of doing this, someone fix it

    files = list(walk('./'))[0][2]
    missingFiles = list(filter(isVideoAndIsntInBackup, files))

    for file in missingFiles: 
        print("\t Handling file {}...".format(file), end="", flush=True)
        currentBackup.addVideo(directory, file)
        print("DONE")
        
    currentBackup.saveToDisk(currentBackup.filePath)
    log.log("Saved backup to {}".format(currentBackup.filePath))
    input("Done :) Press enter to close me")


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



# Quick and dirty way to provide a runtime argument. 
# If you're adding more arguments, please change the way we find arguments :) 
def performRuntime(): 
    if (len(argv) >= 2):
        for items in argv:
            if (items == '--ask-for-backup-folder'): 
                main()
                return 

    runInDirectory()

if __name__ == "__main__":
    try: 
        log.logTitle()
        performRuntime()
        print("\n") # looks pretty roowowowowoowowowowo

    except Exception as e: 
        print("Something went wrong during the tool's runtime")
        print(e)
        input("Press enter to close this window")

