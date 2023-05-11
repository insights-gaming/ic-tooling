from asyncio import get_event_loop, new_event_loop, set_event_loop
from event_handlers.eventFilters import EventFilters
from event_handlers.executeOnEvent import buildEventFilter

from overwolf_chrome_ws_client import OverwolfChromeDebugClient
from utils import generateFakeRecordingData, Timer, RUNTIME_FLAGS

from utils.obs_utils import is_obs_ctx, setup_simpleobsws
from utils.registry import enableDevMode, isInDevMode
from utils.runtime_flags import LOAD_RUNTIME_FLAGS

from event_handlers import addVideoToInsightsCapture

import simpleobsws

LOAD_RUNTIME_FLAGS()
print("Script Init: Loaded.")

# Dev Mode Catch
# TODO: If we find that Overwolf isn't in dev mode, we should kill Overwolf and restart it after we flip the reg switch
if isInDevMode() == False:
    print("Script Init: Overwolf's dev mode flag wasn't on, so we're enabling it. If you see this, and OW is still running, please restart it")
    enableDevMode() 
    print("Script Init: Done enabling Overwolf's dev switch")


OBS_WS_URL = "ws://localhost:4455"
OBS_WS_PWORD = None

# OBS Context Runtime
# TODO: Remove the "or" flag here when RUNTIME_FLAGS works.
# This is a patch to fix an issue where OBS displays the wrong value for RUNTIME_FLAGS["--obs-context"]
try:
    callable(script_path)
    RUNTIME_FLAGS["--obs-context"]["value"] = True
except: 
    RUNTIME_FLAGS["--obs-context"]["value"] = False


# Fake OBS Runtime
if RUNTIME_FLAGS["--fake-obs-data"]["value"] == True:
    print("Script Init: Starting runtime, but with fake OBS Data...")
    loop = get_event_loop()
    loop.run_until_complete(
        addVideoToInsightsCapture(generateFakeRecordingData("C:/Users/tayxb/Videos/Overwolf/obs/2022-12-18_23-18-50.mp4"))
    )

elif RUNTIME_FLAGS["--obs-context"]["value"] == True:
    print("Script Init: Starting runtime, but inside of OBS as a script...")
    def thread_runtime(eventLoop):
        set_event_loop(eventLoop)
        ws = simpleobsws.WebSocketClient(
            url = OBS_WS_URL, 
            # password = OBS_WS_PWRD,
            identification_parameters = simpleobsws.IdentificationParameters(),
        )

        eventLoop.run_until_complete(setup_simpleobsws(ws))
        ws.register_event_callback(
            buildEventFilter(
                EventFilters.recording_stopped,
                addVideoToInsightsCapture,
            )
        )

        eventLoop.run_forever()


# Script Runtime 
else:
    print("Script Init: Starting runtime, but locally...")
    ws = simpleobsws.WebSocketClient(
            url = OBS_WS_URL, 
            # password = OBS_WS_PWRD, 
            identification_parameters = simpleobsws.IdentificationParameters(),
    )

    loop = get_event_loop()
    loop.run_until_complete(setup_simpleobsws(ws))
    ws.register_event_callback(
        buildEventFilter(
            EventFilters.recording_stopped,
            addVideoToInsightsCapture,
        )
    )

    loop.run_forever()
