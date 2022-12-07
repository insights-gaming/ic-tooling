from os import listdir, remove
from os.path import join, isfile

from json import dumps

from gzip import open as gzipopen

from re import compile, search
from requests import get
from typing import Dict, List, Union

from xmltodict import parse, unparse # Someone fucking explain to me WHY IT'S UNPARSE?????????

# AFAIK this is the only place Overwolf has stored the GameList, however we should still 
# allow custom inputs in case of a change in the future. 
DEFAULT_OVERWOLF_DATA_PATH = "/mnt/c/Users/tayxb/AppData/local/Overwolf"# "%localappdata%/Overwolf" 

# At the time of writing I have no specifics on the length of the version # attached to each file 
# ATM they're all 7 chars long, and I've set a max of 20 allowed just in-case
GAMESLIST_REGEX = compile('GamesList.\d{7,20}.xml') 


def checkIfKeyExistsInObj(obj: any, key: str) -> bool:
    """
    checkIfKeyExistsInObj For any object with a `__class_getitem__`, we'll check to see if the key exists in said object. 
    Will silently "fail" by returning false when __class_getitem__ is not present. If you're feeling froggy,
    you can tweak the try/catch below to prevent that :) 

    :param obj: Any object with __class_getitem__
    :type obj: any

    :param key: The key you want to check for
    :type key: str

    :return: Whether or not the key exists in da object
    :rtype: bool
    """
    try: 
        obj.__class_getitem__(key)
        return True
    except: 
        return False

class OVERWOLF_GAMEINFO_CONTAINER:
    """
     A translation table that holds our internal version of the keyword as keys
     and Overwolf's versions are values. 
    """
    id = 'ID'
    gameTitle = 'GameTitle'
    processNames = 'ProcessNames'
    gameRenderers = 'GameRenderers'
    injectionDecision = 'InjectionDecision'
    launcherNames = 'LuancherNames'

    def __class_getitem__(self, item): 
        return self.__getattribute__(self, item)


class GameInfo: 
    id: str # https://overwolf.github.io/api/games/ids
    gameTitle: str
    gameRenderers: str # I just noticed this but apparently OW takes in a string of values delimited by spaces
    injectionDecision: str
    processNames: Union[str, None] 
    launcherNames: Union[str, None]

    unusedArgs: List[Dict[str, any]]

    def __init__(self, gameObject: dict, isOverwolfFormat: bool = True):
        # Pre-setup anything that needs it 
        self.unusedArgs = []

        # Populate our internal class with the KNOWQN contents of gameObject 
        # from the keys of OVERWOLF_GAMEINFO_CONSTS
        copyOfGameObject = gameObject
        for args in vars(OVERWOLF_GAMEINFO_CONTAINER): 
            if (not args.startswith("_")):
                self[args] = (
                    self._useIfValueIsPresentInObject(copyOfGameObject, OVERWOLF_GAMEINFO_CONTAINER[args])
                    if isOverwolfFormat
                    else self._useIfValueIsPresentInObject(copyOfGameObject, args)
                )

                if isOverwolfFormat and OVERWOLF_GAMEINFO_CONTAINER[args] in copyOfGameObject:
                    del copyOfGameObject[OVERWOLF_GAMEINFO_CONTAINER[args]]
                
                if not isOverwolfFormat and args in copyOfGameObject:
                    del copyOfGameObject[args]


        # Now throw the rest into the unused args LMAOz
        for key in gameObject.keys():
            self.unusedArgs.append({ key: gameObject[key] })

    def toJson(self):
        dictToReturn = {}

        # Add known shit
        for args in vars(OVERWOLF_GAMEINFO_CONTAINER): 
            if (not args.startswith("_")):
                dictToReturn[args] = self[args]

        # Add dat spoopy unknown jazzzzzzz
        # NOTE: If there's a key name in unusedArgs that's the same as any known variable 
        # the known variable will get over-written in this step here. 
        for object in self.unusedArgs:
            for key in object.keys():
                dictToReturn[key] = object[key]

        return dictToReturn

    def toString(self): 
        return dumps(self.toJson(), indent = 4)

    def toOWXML(self, pretty: bool = False): 
        return unparse(self.toOWNamespace(), pretty=pretty)

    def toOWNamespace(self): 
        returnDict = {
            # "ID": self.id,
            # "GameTitle": self.gameTitle,
            # "ProcessNames": self._wrapValueInObject('string', self.processNames),
            # "LuancherNames": self._wrapValueInObject('string', self.launcherNames),
            # "GameRenderers": self.gameRenderers,
            # "InjectionDecision": self.injectionDecision,
        }

        for args in vars(OVERWOLF_GAMEINFO_CONTAINER): 
            if (not args.startswith("_") and self[args] is not None):
                returnDict[OVERWOLF_GAMEINFO_CONTAINER[args]] = self[args]

        for object in self.unusedArgs:
            for key in object.keys():
                returnDict[key] = object[key]

        return returnDict

    def _wrapValueInObject(self, key: str, value: any): 
        return {
            key: value # For the record, being able to label a key just by putting a var name is FUCKED
        }

    def _unwrapValueInObject(self, key: str, object: dict): 
        return object[key]

    def _useIfValueIsPresentInObject(self, object, value):
        if (value in object): 
            return object[value] 
        
        return None

    def __setitem__(self, __name: str, __value: any) -> None:
        setattr(self, __name, __value)

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __str__(self):
        return self.toString()


class GameList: 
    fileLocation: str
    contents: dict

    games: List[GameInfo]

    def __init__(self, fileLocation: Union[str, None] = None):
        # Ensure we have a file path
        if (fileLocation):
            self.fileLocation = fileLocation             
        else: 
            self.fileLocation = self.getGameListFilepath()
        
        # Read el file and convert to dictoronie
        self.games = []
        self.populateContents()

    def getGameListFilepath(self, folder: str = DEFAULT_OVERWOLF_DATA_PATH) -> str:
        """
        getGameListFilepath Gets the "newest" GamesList.\d{7}.xml file within a given folder. The "newest" file is 
        determined by looking at which files has the largest version number in its filename.

        :param folder: The folder to look for GameLists in, defaults to DEFAULT_OVERWOLF_DATA_PATH
        :type folder: str, optional
        
        :raises ValueError: Raises when we can't find a gamelist in that folder
        
        :return: Returns the path to the newest GamesList folder
        :rtype: str
        """
        # Walk through the possible storage local 
        possibleFiles = list(filter(isGameListFile, listdir(folder)))
        possibleFiles.sort(key=sortGameListsByVersion, reverse=True)

        if len(possibleFiles) == 0: 
            raise ValueError("Unable to find gamelist in {}".format(folder))

        # The above filter will collect any number of possible gamelist files
        # We should probably take the newest version of that file
        return join(folder, possibleFiles[0]) # Maybe we should refactor this to return all possible gamelists... 

    def populateContents(self): 
        # Pull from the file into memory
        file = open(self.fileLocation, "r")
        self.contents = parse(file.read(), encoding="utf-8")
        file.close()

        # Pull games out 
        root = self.contents['ArrayOfGameInfo']['GameInfo']
        for gameObject in root: 
            self.games.append(GameInfo(gameObject, True))

    def _dumpGameInfoPossibleParams(self) -> dict: 
        """
        __dumpGameInfoPossibleParams A debug function that loops through all of the games in self.content[ArrayOfGameInfo]
        and collects all of the possible keys a GameInfo object can have. 

        NOTE from Aud: I'll probably ever only use this once, but I've included it just in-case you need to know.

        :return: returns a dict containing the keys being used, and possible values
        :rtype: dict
        """
        root = self.contents['ArrayOfGameInfo']['GameInfo']
        returnDict = {}
        optionLimit = 5

        gameIndex = 0
        for gameObject in root:
            for key in gameObject:
                if key not in returnDict:
                    returnDict[key] = [root[gameIndex][key]]

                elif len(returnDict[key]) < optionLimit: 
                    returnDict[key].append(root[gameIndex][key])

            gameIndex += 1
        
        return returnDict

    def addGame(self, id: str, title: str, renderer: str, processName: str): 
        obj = GameInfo({
            'id': id,
            'title': title,
            'gameRenderers': renderer,
            'injectionDecision': 'supported',
            'processNames': processName,
        }, False)
        self.games.append(obj)

    def addGameFromOWJson(self, object: dict): 
        self.games.append(GameInfo(object, True))

    def addGameInfoObject(self, object: GameInfo):
        self.games.append(object)


    def save(self):
        file = open(self.fileLocation, "w")

        gamesCompiled = []
        for game in self.games:
            gamesCompiled.append(game.toOWNamespace())


        self.contents['ArrayOfGameInfo']['GameInfo'] = gamesCompiled
        
        file.write(
            unparse(self.contents, pretty=True)
        )

        file.close()


        return 


def isGameListFile(fileName: str) -> bool: 
    """
    isGameListFile A sloppy regex test to check if the given file name is a GamesList file. 
    NOTE that this test will fail out on file paths, adjust the regex for your use case.

    :param fileName: The path of the file we're looking at. 
    :type fileName: str

    :return: Returns whether or not the fileName is a GamesList file
    :rtype: bool
    """
    return GAMESLIST_REGEX.match(fileName)

def getGameListVersion(fileName: str) -> Union[str, None]: 
    """
    getGameListVersion Extracts the version number attached to a game list file name

    :param fileName: The name of the file that's being torn apart 
    NOTE The regex here only looks for a group of numbers, so consider that if you're inputting a filepath.
    :type fileName: str

    :return: Returns the version number attached if one was found, else returns None 
    :rtype: Union[str, None]
    """
    lookup = search(r'\d{7,20}', fileName)

    # I would prefer to return in the ternary but python said no lmao
    check = lookup.group(0) if (lookup != None) else None
    return check
    
def sortGameListsByVersion(GameListFileName: str) -> int:
    """
    sortGameListsByVersion Used as a key for sorting a list of GameList files. For each file name being sorted
    we extract and return the version number. 

    :param GameListFileName: The name of the GamesList file 
    :type GameListFileName: str

    :return: Returns the version number attached to the filename, casted to an int
    :rtype: int
    """

    # Quietly squash invalid fileVersions
    try: 
        return int(getGameListVersion(GameListFileName))

    # TODO: Probably should propperly handle this...
    except ValueError: 
        return 0
        # pass

    except: 
        raise


def refreshGameListFile(filepathToSaveTo, overwolfVersion = "0.195.0", gameslistVersion = "8963241") -> bool: 
    url = "http://gamelist.overwolf.com/gz.{}/GamesList.{}.xml.gz".format(overwolfVersion, gameslistVersion)

    tmpZip = './zip.tmp.gz'
    req = get(url)
    if req.status_code == 200:
        file = open(tmpZip, "wb")
        file.write(req.content)
        file.close()

        try: 
            file = gzipopen(tmpZip, 'rb')
            contents = file.read()
            file.close()

            file = open(filepathToSaveTo, "wb")
            file.write(contents)
            file.close()

            if isfile(tmpZip): remove(tmpZip) 


        except Exception as e: 
            if isfile(tmpZip): remove(tmpZip) 
            # if isfile(filepathToSaveTo): remove(filepathToSaveTo)'

            raise e

        return True 
    
    print(req.status_code)
    print(req.reason)

    return True
