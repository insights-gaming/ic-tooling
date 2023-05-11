from time import time

class Timer(object):
    events = []
    idCount = 0


    """
     _summary_

     Attributes: 
         events: a list of dicts, in the format:
            { name: str; startTime: number; endTime: None || number; duration: None || number }

         idCount: a number, effectively just the index of the last item in the eventsArray
    """

    @classmethod
    def requestId(ctx):
        curId = Timer.idCount
        Timer.idCount += 1

        return curId

    @classmethod
    def startRecordingTime(ctx, name):
        """
        addTime _summary_

        :param name: the name of the event you're adding
        :type name: str

        :returns: number, id of event
        """ 
        now = time()
        Timer.events.append({ "name": name, "startTime": now, "endTime": None, "duration": None })

        return Timer.requestId()

    @classmethod
    def endRecordingTime(ctx, id):
        Timer.events[id]["endTime"] = time()
        Timer.events[id]["duration"] = Timer.events[id]["endTime"] - Timer.events[id]["startTime"]

    @classmethod
    def timeEvent(ctx, eventName, funct, args = None):
        eventId = Timer.startRecordingTime(eventName)

        # Args get supplied as a tuple, if the tuple only has one item though it gets 
        # Converted to that item's type. 
        if type(args) is not tuple and args != None:
            runtime = funct(args)

        # If there are spreadable args
        elif args != None:
            runtime = funct(*args)

        # If there aren't any args
        elif args == None: 
            runtime = funct()

        else: 
            print(args)
            raise ValueError("unsure how to handle args in timing event")

        Timer.endRecordingTime(eventId)
        return runtime

    @classmethod
    async def timeEventAsync(ctx, eventName, funct, args = None):
        eventId = Timer.startRecordingTime(eventName)

        runtime = None

        # Args get supplied as a tuple, if the tuple only has one item though it gets 
        # Converted to that item's type. 
        if type(args) is not tuple and args != None:
            runtime = await funct(args)

        # If there are spreadable args
        elif args != None:
            runtime = await funct(*args)

        # If there aren't any args
        elif args == None: 
            runtime = await funct()

        else: 
            print(args)
            raise ValueError("unsure how to handle args in timing event")

        Timer.endRecordingTime(eventId)
        return runtime


    @classmethod
    def getTimingForLastEvent(ctx):
        return Timer.events[len(Timer.events) - 1]["duration"]
    
    @classmethod
    def getLastEventInfo(ctx):
        return Timer.events[len(Timer.events) - 1] 

    @classmethod
    def prettyPrintTiming(ctx):
        event = Timer.getLastEventInfo()
        return "[{}]: Took {} seconds".format(event["name"], event["duration"])

    @classmethod
    def dumpTimings(ctx):
        strToReturn = ""
        for event in Timer.events:
            strToReturn += "{}\n".format("[{}]: {} Seconds".format(event["name"], event["duration"]))

        return strToReturn
   
    @classmethod
    def dumpTotalRuntime(ctx):
        durationTotal = 0
        for events in Timer.events:
            durationTotal += events["duration"]

        return {
            "total": durationTotal,
            "events": len(Timer.events)
        }
