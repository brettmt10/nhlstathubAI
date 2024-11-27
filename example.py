from api_handler import NHLHandler

# create a handler object. you can now call any function in the schedule or player data handlers
nhl = NHLHandler()

# call a schedule function
print(nhl.schedule_handler.get_num_games())

# get the schedule
sched = nhl.schedule_handler.nhl_schedule()

# check out todays games
nhl.schedule_handler.print_beautify_schedule(sched)

# update the date of your existing object
print("setting new date......")
nhl.set_date("2024-11-20")
sched = nhl.schedule_handler.nhl_schedule()
nhl.schedule_handler.print_beautify_schedule(sched)

# or create a new object with its own date
print("separate object....")
nhl_yesterday = NHLHandler(date="2024-11-23")
sched = nhl_yesterday.schedule_handler.nhl_schedule()
nhl_yesterday.schedule_handler.print_beautify_schedule(sched)

# get a teams player data
player_data = nhl.player_data_handler.get_team_player_data_as_df("boston")



