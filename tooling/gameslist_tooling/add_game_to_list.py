from gamelist import GameList
from traceback import format_exc 
from os import getcwd, listdir
from json import loads

# Quick hack to allow us to import the tooling
# Assumes that you're running the script from the project root :^)
from sys import path
path.append(getcwd())

from tooling.gameslist_tooling.gamelist.gamelist_file import refreshGameListFile
from tooling.common.logging import ConsoleInterface

log = ConsoleInterface()

def main(): 
    log.log("Pulling out the latest GamesList in your Overwolf storage...")
    log.log("If you have the path to a specific GamesList.xml file, you can paste it below-")
    log.log("If you don't, just simply hit enter")
    customGamesList = log.getInput("Do you have a specific GamesList.xml file you'd like to edit")
    
    # Have I mentioned how fucking ugly python's ternaries are? Like fuck me...
    gameListContainer = (
        GameList(customGamesList)
        if (customGamesList and customGamesList != "") 
        else GameList()
    )

    log.log("Using GamesList file: {}".format(gameListContainer.fileLocation))
    log.log("File contains {} games...".format(len(gameListContainer.games)))

    gamesToAddFolder = "./tooling/gameslist_tooling/examples/games"
    log.log("Preparing to collect games to add from {}".format(gamesToAddFolder))

    # Probably should upgrade this later lol
    def isJson(filename:str) -> bool: 
        if filename.endswith(".json"): return True
        return False
    possibleFiles = list(filter(isJson, listdir(gamesToAddFolder)))


    log.log("Found {} games to add".format(len(possibleFiles)))
    for fileName in possibleFiles: 
        file = open("{}/{}".format(gamesToAddFolder, fileName), "r")
        content = loads(file.read())

        gameListContainer.addGameFromOWJson(content)
        game = gameListContainer.games[(len(gameListContainer.games) - 1)]
        log.log("Successfully added {} - {}".format(game.id, game.gameTitle))

    gameListContainer.save()

    log.log("Job done uwu")



def pullNewGamesList():
    log.log("Pulling out the latest GamesList in your Overwolf storage...")
    log.log("If you have the path to a specific GamesList.xml file, you can paste it below-")
    log.log("If you don't, just simply hit enter")
    customGamesList = log.getInput("Do you have a specific GamesList.xml file you'd like to edit")

    path = (
        customGamesList
        if (customGamesList and customGamesList != "") 
        else GameList.getGameListFilepath({})
    )

    attempt = refreshGameListFile(path)
    log.log("Finished refreshing games list, result: {}".format(attempt))

if __name__ == "__main__":
    try: 
        log.logTitle()
        # pullNewGamesList()
        main()
        print("\n")
        # input("Press enter to close this window")


    except Exception as e: 
        print("Something went wrong during the tool's runtime")
        print(e)
        print(format_exc())

