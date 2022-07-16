from os.path import exists, getsize, join
from json import loads, dumps, JSONEncoder
from time import time
from typing import Any, Dict 
from uuid import uuid4

from cv2 import VideoCapture, CAP_PROP_POS_MSEC

class Backup:
    filePath: str
    content: Dict[str, Any]

    version: str
    videos: Dict[str, Dict]

    def __init__(self, filePath): 
        self.filePath = filePath
        
        # Double check the given file path exists :suicide_kanna: 
        if (exists(filePath) != True): 
            raise ValueError("The provided file path {} is not a valid file path. Please double check your path".format(filePath))

        # Load the file in :pog: 
        self.content = self.load()

        # Populate some extra stuff
        self.version = self.content["appVersion"]
        self.videos = self.content["videoStore"]

    def load(self):
        try: 
            rawFileContents = open(self.filePath, "r")
            fileContents = loads(rawFileContents.read()) # probably should do this different

            return fileContents
        except: 
            raise ValueError("Impropper JSON found in {}, are you sure this file is a backup file?".format(self.filePath))


    # Note that filePath must be the FULL file path, not local or whatevr 
    def videoExists(self, filePath: str) -> bool:
        for videos in self.videos:
            video = self.videos[videos]

            if video["result"] and video["result"]["file_path"]:
                if video["result"]["file_path"] == filePath: 
                    return True 

        return False 

    def videoCount(self) -> int: 
        return len(self.videos)


    def addVideo(self, 
        videoPath, 
        fileName, 
        options = {
            "gameId": 21640, # See: https://overwolf.github.io/api/games/ids 
            "created": round(time() * 1000),
            "providedName": None,
        }
    ) -> str: 
        # Generate the UUID for said video | https://stackoverflow.com/questions/534839/how-to-create-a-guid-uuid-in-python
        uuid = str(uuid4())

        # Make sure it doesn't collide with existing video objects 
        while (uuid in self.videos): # I'm sure blindly looping will be FINE
            uuid = str(uuid4())

        # Get the size of the file (i think this one actually matters)
        sizeInBytes = getsize(join(videoPath, fileName))

        # Clean up the file path 
        filePath = join(videoPath, fileName).replace("\\", "\\" + "\\") # This feels so fucked

        # Build up a video object PAWG
        videoObject = {
            "uuid": uuid,
            "created": options['created'],
            "size": sizeInBytes,
            "gameClassId": options['gameId'], 
            "result": {
                "success": True,
                "stream_id": 1, # I'm like, 30% positive this can be any int
                "url": "overwolf://media/recordings/Insights+Capture\\\\{}".format(fileName.replace(" ", "+")),
                "file_path": filePath,
                "duration": VideoCapture(join(videoPath, fileName)).get(CAP_PROP_POS_MSEC),
                "last_file_path": filePath,
                "split": True,
                "splitCount": 1,
                "extra": "{  \"drawn\": 0,  \"dropped\": 0,  \"lagged\": 0,  \"percentage_dropped\": 0,  \"percentage_lagged\": 0,  \"system_info\": {    \"game_dvr_bg_recording\": false,    \"game_dvr_enabled\": true,    \"game_mode_enabled\": true  },  \"total_frames\": 0}",
                "osVersion": "10.0.19043.1766",
                "osBuild": "2009"
            },
            "userProvidedName": fileName if options["providedName"] == None else options["providedName"]
        }

        self.videos[uuid] = videoObject 
        return uuid


    def saveModdedVideos(self): 
        self.content["videoStore"] = self.videos

    def saveToDisk(self, filePath: str): 
        # Replace modded shit
        self.saveModdedVideos()

        # i.... IDK without it the ints get fucking converted to a string and it 
        # really makes me want to relapse 
        class stupidFuckingIntEncoder(JSONEncoder):
            def default(self, obj):
                if type(obj) == "int": 
                    return int(obj)

                return JSONEncoder.default(self, obj)

        # Save to file
        with open(filePath, "w") as file: 
            file.write(dumps(self.content, indent=4, cls=stupidFuckingIntEncoder))
            file.close()

