from sys import argv
from json import dumps

from .obs_utils import is_obs_ctx

# Setup a flag dict
global RUNTIME_FLAGS 
RUNTIME_FLAGS = {
    "--help": {
        "description": "Prints help then exits",
        "value": False,
    },
    "--fake-obs-data": {
        "description": "Creates a fake runtime from dev based OBS event data",
        "value": False
    },
    "--obs-context": {
        "description": "Runs the script as if it were executd by obs-python",
        "value": is_obs_ctx()
    }
}
RUNTIME_ARGS = list(filter(lambda item: item in RUNTIME_FLAGS, argv))


def LOAD_RUNTIME_FLAGS():
    # Find which keys are active
    for key in RUNTIME_FLAGS.keys():
        if key in RUNTIME_ARGS:
            RUNTIME_FLAGS[key]["value"] = True

    # Print help if it's needed
    if RUNTIME_FLAGS["--help"]["value"] == True:
        print(dumps(RUNTIME_FLAGS, indent= 4))
        exit()


