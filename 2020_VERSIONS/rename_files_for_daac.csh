Mission Reports:
IMPACTS_Reports_[er2|p3]_YYYYMMDD_mission_scientist.pdf
IMPACTS_Reports_[er2|p3]_YYYYMMDD_aircraft_scientist.pdf
IMPACTS_Reports_flight_plan_YYYYMMDD_daily.pdf
IMPACTS_Reports_plan_of_the_day_YYYYMMDD_daily.pdf
IMPACTS_Reports_science_plan_YYYYMMDD_daily.pdf
IMPACTS_Reports_science_summary_YYYYMMDD_daily.pdf
IMPACTS_Reports_scorecard_YYYYMMDD_overall.pdf

This includes the following changes:
- Change all periods (.) to underscores (_)
- Add "IMPACTS_Reports_" to the beginning of each file
- Since adding "IMPACTS_Reports_", remove the first "missions_" in the missions.* files

NEXRADs:
IMPACTS_<site name>_<start date>_<start time>_to_<end date>_<end time>_SUR.nc
IMPACTS_nexrad_mosaic_east_<start date>_<start time>_grid.nc
IMPACTS_nexrad_mosaic_midwest_<start date>_<start time>_grid.nc

This includes the following changes:
- Remove 'cfrad'
- Add 'IMPACTS_' to the beginning of each file
- Move the site name to the beginning after 'IMPACTS_'
- I left out 'Surveillance' because I assumed it meant the same thing as 'SUR'. If not, then it is okay to leave this in

NY Mesonet:
IMPACTS_nys_lidar_<product>_YYYYMMDD_hhmm_<site>.png

This includes the following changes:
- Remove 'ops'
- Add 'IMPACTS_' at the beginning of the file
- Turn periods (.) to underscores (_)
- Add underscore (_) between date and time
