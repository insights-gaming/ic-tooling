from event_handlers.eventFilters import Event


def buildEventFilter(eventFilter, funct):
    async def on_event_called(eventName, eventData):
        event = Event(eventName, eventData)
        if (eventFilter(event)):
            await funct(eventData)

    return on_event_called