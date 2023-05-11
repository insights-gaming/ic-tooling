class Event:
    name: str
    data: dict[str, any]

    def __init__(self, name, data):
        self.name = name
        self.data = data


class EventFilters:
    @classmethod
    def recording_stopped(ctx, event: Event) -> bool:
        """
        recording_stopped Checks to see if the event in question is an RecordingStateChanged event, that
                          denotes the end of a recording. 

        Args:
            ctx (EventFilters): The class's context
            eventType (str): The name of the event being looked at
            eventData (dict[str, any]): The OBS event "RecordStateChanged", see https://wiki.streamer.bot/en/Broadcasters/OBS/Events/Output-Events/RecordStateChanged

        Returns:
            bool: Whether or not the event is a recording stopped event
        """
        return event.name == "RecordStateChanged" \
            and event.data["outputState"] == "OBS_WEBSOCKET_OUTPUT_STOPPED" \
            and event.data["outputPath"] is not None


    """
        TODO:
            - Add other event filters as needed ayayaya
    """