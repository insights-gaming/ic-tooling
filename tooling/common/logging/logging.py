from datetime import datetime
from tooling.common.intro_banner import header

class ConsoleInterface: 
    def __init__(self, title="insights-cs-tooling"): 
        self.title = title

    def log(self, string): 
        print("[{}][{}]: {}".format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S"), self.title, string))


    def logTitle(self):
        print(header)


    def getInput(self, question): 
        return input("[{}][{}]: {}?: ".format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S"), self.title, question))
