from os.path import exists, getsize, getmtime, join
from json import loads, dumps, JSONEncoder
from time import time
from typing import Any, Dict 
from uuid import uuid4

from ffprobe import FFProbe, FFProbeError

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
            rawFileContents = open(self.filePath, "r", encoding="utf8")
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
        filePath = join(videoPath, fileName)#.replace("\\", "\\" + "\\") # This feels so fucked

        # Get the video capture
        media = FFProbe(join(videoPath, fileName))

        for index, stream in enumerate(media.streams, 1):
            print('\tStream: ', index)
            try:
                if stream.is_video():
                    frame_rate = stream.frames() / stream.duration_seconds()
                    print('\t\tFrame Rate:', frame_rate)
                    print('\t\tFrame Size:', stream.frame_size())

                print('\t\tDuration:', stream.duration_seconds())
                print('\t\tFrames:', stream.frames())
                print('\t\tIs video:', stream.is_video())
            except FFProbeError as e:
                print(e)
            except Exception as e:
                print(e)

        # Build up a video object PAWG
        videoObject = {
            "uuid": uuid,
            "created": round(getmtime(join(videoPath, fileName)) * 1000), # Somehow, I feel like this might be problematic but ohwellsi
            "size": sizeInBytes,
            "gameClassId": options['gameId'], 
            "result": {
                "success": True,
                "stream_id": 1, # I'm like, 30% positive this can be any int
                "url": "overwolf://media/recordings/Insights+Capture\\\\{}".format(fileName.replace(" ", "+")),
                "file_path": filePath,
                "duration": stream.duration_seconds() * 1000,
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
        with open(filePath, "w", encoding="utf8") as file: 
            file.write(dumps(self.content, indent=4, cls=stupidFuckingIntEncoder))
            file.close()



def createNewBackup(path):
    jsonToWrite = """{"videoStore":{},"commentStore":{},"settingStore":{},"productTourStore":{},"videoUploadRecordStore":{},"commentRootUploadRecordStore":{},"commentReplyUploadRecordStore":{},"videoBookmarkUploadRecordStore":{},"videoMergedInfoUpdateStore":{},"videoLoLStatsStore":{},"videoValorantGameInfoStore":{},"appDataStore":{"lastBannerId":10844},"videoRecycleBinStore":{},"folderStore":{},"folderRecycleBinStore":{},"libraryItemParentStore":{},"trackedUploadsStore":{},"achievementTrackerStore":{},"actionTrackerStore":{},"libraryMetadataStore":{},"appVersion":"1.8.0.1"}"""
    contents = open(path, "w", encoding='utf8')
    contents.write(jsonToWrite)
    contents.close()

    return Backup(path)