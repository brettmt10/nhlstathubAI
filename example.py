from api_handler import NHLScheduleHandler

# create a handler object. by default, today's date is used.
nhl = NHLScheduleHandler()

# or, specify your own date
nhl = NHLScheduleHandler(date="2024-11-22")

# this gets you the schedule of the date provided
schedule: list[dict] = nhl.nhl_schedule()

# want to verify you have the right day? print out the schedule in readable text
nhl.beautify_schedule(schedule=schedule)


