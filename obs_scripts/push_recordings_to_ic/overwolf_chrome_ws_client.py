from datetime import datetime
from time import time, sleep
from uuid import UUID, uuid4
from os.path import getsize, getmtime

from websockets.exceptions import ConnectionClosedError
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS #TODO: Replace with FFMPEG, too lazy to figure out why borko


import requests
import json
import websockets

from utils import Timer


class OverwolfChromeDebugClient():
    def __init__(self, host, port): 
        self.host = host
        self.port = port 

        self.base = "http://{}:{}".format(self.host, self.port)

        self.ids = []
        self.pages = []

        self.pageIndex = []
        self.eventStreams = []


    def query(self, endpoint): 
        # This dum as shit, but fuck it we ball
        return requests.get(
            "{}{}".format(self.base, endpoint),
        )


    def getPages(self):
        if (len(self.pageIndex) == 0):
            req = self.query("/json/list")
            if (req.ok != True):
                raise ValueError("Failed to get pages, said: {}".format(req.text))
            
            # Find the IC BG
            return json.loads(req.text)

        return self.pageIndex


    def getPage(self, filteredUrl): 
        pages = self.getPages()
        filterd = [x for x in pages if x["url"].startswith("overwolf-extension://okmohcjfmchpapljmoineeecekojmbbheniohgnp/background.html")]

        if filterd[0]: return filterd[0]
        
        raise ValueError("Filtered URL not found, is page active? URL: {}".format(filteredUrl))

    async def addPage(self, name, filteredUrl): 
        # First find the wbesocket
        pageData = self.getPage(filteredUrl)

        wsCtx = await Timer.timeEventAsync(
            "addPage:{}:connect-to-websocket".format(name),
            websockets.connect,
            (pageData["webSocketDebuggerUrl"])
        )

        await Timer.timeEventAsync(
            "addPage:{}:enable-run-time".format(name),
            wsCtx.send,
            (
                json.dumps({
                    "id": self.useId(name),
                    "method": "Runtime.enable"
                })
            )
        )

        await Timer.timeEventAsync(
            "addPage:{}:recieve-run-time-enable".format(name),
            wsCtx.recv,
        )

        await Timer.timeEventAsync(
            "addPage:{}:enable-debugger".format(name),
            wsCtx.send,
            (
                json.dumps({
                    "id": self.useId(name),
                    "method": "Debugger.enable"
                })
            )
        )

        # await wsCtx.recv() # No need to wait on a res here :) 

        self.pages.append({
            "name": name,
            "pageData": pageData, 
            "wsUrl": pageData["webSocketDebuggerUrl"],
            "ws": wsCtx
        })

    async def refreshConnection(self, name):
        # Find the connection 
        print("refreshing {}".format(name))
        for i in range(0, len(self.pages)):
            if self.pages[i]["name"] == name:
                print(self.pages[i])
                self.pages[i]["ws"] = await websockets.connect(self.pages[i]["wsUrl"])

                await self.pages[i]["ws"].send(json.dumps({
                    "id": self.useId(name),
                    "method": "Runtime.enable"
                }))
                await self.pages[i]["ws"].recv()

                await self.pages[i]["ws"].send(json.dumps({
                    "id": self.useId(name),
                    "method": "Debugger.enable"
                }))
                await self.pages[i]["ws"].recv()
                

                return

    async def sendWS(self, page, data):
        try:
            if type(data) is dict:
                data = json.dumps(data)

            await page["ws"].send(data)

        except ConnectionClosedError:
            await self.refreshConnection(page["name"])
            # await self.sendWS(page, data)
            return False
    
    async def readWS(self, page):
        try:
            data = await page["ws"].recv()
            try:
                return json.loads(data)
            except: 
                return data


        except ConnectionClosedError:
            await self.refreshConnection(page["name"])
            return await page["ws"].recv()

    async def getPageStream(self, page):
        stream = []
        try:
            while(True):
                stream.append(json.loads(await page["ws"].recv()))
        
        except: pass 

        streamLookup = [x for x in self.eventStreams if x["page"] == page["name"]]
        if (len(streamLookup) == 0):
            self.eventStreams.append({
                "page": page["name"],
                "events": stream
            })
            return {
                "page": page["name"],
                "events": stream
            }

        else:
            for y in range(0, len(self.eventStreams) - 1):
                if self.eventStreams[y]["page"] == page["name"]:
                    self.eventStreams[y]["events"] = [*self.eventStreams[y]["events"], *stream]
                    return self.eventStreams[y]["events"]

    async def runScript(self, task, page, script):
        # Create the script
        fileName = "{}-{}.js".format(task, time())

        compileId = self.useId(page["name"])
        compile_script_args = {
            "id": compileId,
            "method": "Runtime.compileScript",
            # "executionContextId": 26, # it's just always been 26, but you can hook into the events to find this #
            "params": {
                "expression": script,
                "sourceURL": fileName,
                "persistScript": True
            }
        }

        atmp = await self.sendWS(page, compile_script_args)
        if atmp == False:
            await self.sendWS(page, compile_script_args)

        scriptId = None
        lesGo = True

        attmpt = 1
        while scriptId == None:
            if attmpt > 3: raise ValueError("Couldn't find id in 3 attempts")
            try:
                while (lesGo):
                    ctx = await self.readWS(page)

                    # if "method" in ctx and ctx["method"] == "Debugger.scriptParsed":
                    #     print(ctx)
                    #     raise ValueError("fuck off wank")

                    if "result" in ctx and "scriptId" in ctx["result"]:
                        scriptId = ctx["result"]["scriptId"]
                        break
            except Exception as e: 
                print("e")
                print(scriptId)
                pass

            attmpt += 1

        # Run the script
        run_script_args = {
            "id": compileId,
            "method": "Runtime.runScript",
            "params": {
                # "executionContextId": 26,
                "scriptId": scriptId,
                "awaitPromise": True
            }
        }

        atmp = await self.sendWS(page, run_script_args)
        if atmp == False:
            await self.sendWS(page, run_script_args)

        # try:
        #     while(True):
        #         ctx = json.loads(await page["ws"].recv())

        # except: pass


    async def addVideosToLocalStorage(self, videoObjects):
        filterd = [x for x in self.pages if x["name"] == 'desktop']

        await self.runScript( "addVideos", filterd[0], """
            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            async function fuck(){
                dbReq = indexedDB.open('localforage', 28);
                let done = false;
                let res = null;
                dbReq.onsuccess = (event) => {
                    const db = event.target.result;
                    let transaction = db.transaction(['Video'], 'readwrite');
                    let store = transaction.objectStore('Video');
                    Object.entries(""" + json.dumps(videoObjects) + """).forEach(([key, value]) => {
                        store.add(value, key);
                    });
                };

                while (!done) {
                    await sleep(500);
                }

                console.log(res);

            }


            console.log('yuh');fuck();""")

    def createPushToLocalStorageFunction(self,videoObjects):
        return """
            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            async function pushToLocalForage(){
                dbReq = indexedDB.open('localforage', 28);
                let done = false;
                let res = null;
                dbReq.onsuccess = (event) => {
                    const db = event.target.result;
                    let transaction = db.transaction(['Video'], 'readwrite');
                    let store = transaction.objectStore('Video');
                    Object.entries(""" + json.dumps(videoObjects) + """).forEach(([key, value]) => {
                        store.add(value, key);
                    });
                };

                while (!done) {
                    await sleep(500);
                }

                console.log(res);

            }
        """

    def createDispatchCode(self, fname, action):
        return """
            console.log(`Dispatching Action: {}`);
            globals.store.dispatch(""" + json.dumps(action) + """)
        """.format(fname)

    async def addVideosToInsightsCapture(self, name, path):
        # Determine size and duration
        mediaDetectionId = Timer.startRecordingTime("addVideosToInsightsCapture:media-detection")

        media = VideoCapture(path)
        frames = media.get(CAP_PROP_FRAME_COUNT)
        fps = media.get(CAP_PROP_FPS)

        Timer.endRecordingTime(mediaDetectionId)


        # Build
        act = Timer.timeEvent(
            "addVideosToInsightsCapture:action-creation",
            self.createVideoAction,
            (name, path, round((frames / fps) * 1000), getsize(path))
        )

        # await self.addVideosToLocalStorage({
        #     "{}".format(act["payload"]["uuid"]): act["payload"]
        # })

        # Combine the two scripts and fire them :) 

        addToLocalAndDispatch = Timer.timeEvent(
            "addVideosToInsightsCapture:code-build-time",
            """{}\n{}\npushToLocalForage();""".format,
            (
                self.createPushToLocalStorageFunction({
                    "{}".format(act["payload"]["uuid"]): act["payload"]
                }), 
                self.createDispatchCode("video-library/videoSaved", act)
            )
        )


        desktopFilter = [x for x in self.pages if x["name"] == 'desktop']

        await Timer.timeEventAsync(
            "addVideosToInsightsCapture:send-off-code",
            self.runScript,
            ("addVideoToIC", desktopFilter[0], addToLocalAndDispatch)
        )

    async def reload(self, pageName):
        filterd = [x for x in self.pages if x["name"] == pageName]
        await self.runScript("reload", filterd[0], """console.log('reloading'); window.location.reload();""")


    def useId(self, page):
        # if (len(self.ids) == 0):
        #     self.ids.append({
        #         "page": page,
        #         "id": 1x
        #     })
        #     return 1
        # find page 

        for y in range(0, len(self.ids)): 
            if self.ids[y]["page"] == page:
                num = int("{}".format(self.ids[y]["id"]))
                self.ids[y]["id"] += 1

                return num

        self.ids.append({
            "page": page,
            "id": 10
        })
        return 10

    def createVideoAction(self, name, path, duration, size): 
        # Pull file from path 
        fileParts = path.split("/")
        fileParts.reverse()

        return {
            "type": "video-library/videoSaved",
            "payload": {
                "uuid": str(uuid4()),
                "created": round(getmtime(path) * 1000),
                "size": size,
                "userProvidedName": name,
                "result": {
                    "success": True,
                    "stream_id": 1,
                    "url": "overwolf://media/recordings/Insights+Capture\\{}".format(fileParts[0]),
                    "file_path": path, #"C:/Users/tayxb/Videos/Overwolf\\Insights Capture\\Desktop 12-18-2022_22-47-54-621.mp4",
                    "duration": duration,
                    "last_file_path": path, #"C:/Users/tayxb/Videos/Overwolf\\Insights Capture\\Desktop 12-18-2022_22-47-54-621.mp4",
                    "split": True,
                    "splitCount": 1,
                    "extra": "{\r\n  \"drawn\": 0,\r\n  \"dropped\": 0,\r\n  \"lagged\": 0,\r\n  \"percentage_dropped\": 0,\r\n  \"percentage_lagged\": 0,\r\n  \"system_info\": {\r\n    \"game_dvr_bg_recording\": false,\r\n    \"game_dvr_enabled\": true,\r\n    \"game_mode_enabled\": false\r\n  },\r\n  \"total_frames\": 25\r\n}",
                    "osVersion": "10.0.19045.2251",
                    "osBuild": "2009"
                }
            }
        }

    # def log(self, title, m):
    #     now = datetime.now()
    #     print("[{}][{}] {}".format(now, title, m))


