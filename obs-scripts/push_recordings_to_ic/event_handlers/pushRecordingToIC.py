from overwolf_chrome_ws_client import OverwolfChromeDebugClient
from utils.timer import Timer


async def addVideoToInsightsCapture(event):
    print("Runtime Init: Got Recording Finished event, handling file {} now".format(event["outputPath"]))
    client = OverwolfChromeDebugClient("localhost", "54284")

    desktopPageCreation = Timer.startRecordingTime("OWCDC: Add desktop page")
    await client.addPage("desktop", "overwolf-extension://okmohcjfmchpapljmoineeecekojmbbheniohgnp/desktop.html")
    Timer.endRecordingTime(desktopPageCreation)

    fileNameInfo = event["outputPath"].split("/")
    fileNameInfo.reverse()

    addVideoTimer = Timer.startRecordingTime("OWCDC: Add video function")
    await client.addVideosToInsightsCapture(fileNameInfo[0], event["outputPath"])
    Timer.endRecordingTime(addVideoTimer)

    print(Timer.dumpTimings())
    print("It took {} seconds to upload your OBS clip to Insights Capture".format(Timer.dumpTotalRuntime()["total"]))
