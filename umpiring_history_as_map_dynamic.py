#Import modules pandas and plotly express
import pandas as pd
import plotly.express as px
import numpy as np

#Read in the csv file containing venue information and locations
directory = 'C:/Users/Azzla/Downloads/'
venues = 'PerthFootballLeagueVenues.csv'
AllVenues = pd.read_csv(directory + venues)

#Read in the umpiring history csv
history = 'AllGamesUmpiredPFL2017_2022.csv'
UmpiringHistory = pd.read_csv(directory + history)

#Get all the venues as a list from both dataframes
UH_Venues = UmpiringHistory['Venue']
MappedVenues = AllVenues['VENUE']

#Check for venues in the umpiring history that are not in the venues list
#of all mapped venues
Venues_To_Check = []
for v in UH_Venues:
    if v not in MappedVenues.values:
        if v not in Venues_To_Check:
            Venues_To_Check.append(v)

#Check all venue names in the umpiring history
#Prompt for correction if names in umpiring history do not match any names
#in mapped venues
#And keep asking user for corrections to all venue names match in both databases
for v in Venues_To_Check:
    string_line_one = str(v) + ' is not in the list of mapped PFL venues.\n'
    string_line_two = 'Is it any one of these?:\n'
    string_line_three = ''
    for mv in MappedVenues:
        string_line_three += str(mv) + ', '
    string = string_line_one + string_line_two + string_line_three
    venue_name_correction = input(string)
    if venue_name_correction in MappedVenues.values:
        print('Venue Renamed Successfully!')
        UH_Venues.replace(v, venue_name_correction)
    else:
        in_MappedVenues = False
        while in_MappedVenues == False:
            venue_name_correction = input(string)
            if venue_name_correction in MappedVenues.values:
                in_MappedVenues = True
        UH_Venues.replace(v, venue_name_correction)



            
#Create a dataframe that combines the venue geolocation (latitude and longitude
#Coordinates with the umpiring history
Latitudes = AllVenues['LATITUDE']
Longitudes = AllVenues['LONGITUDE']
uh_latitudes = []
uh_longitudes = []
for i in range(len(UH_Venues)):
    for j in range(len(MappedVenues)):
        if UH_Venues[i] == MappedVenues[j]:
            uh_latitudes.append(Latitudes[j])
            uh_longitudes.append(Longitudes[j])
            break

#Update the umpiring history dataframe with the latitude and longitude attributes
UmpiringHistory['latitude'] = uh_latitudes
UmpiringHistory['longitude'] = uh_longitudes

#Export updated dataframe to csv
output_csv = 'UmpireHistory_WithGeolocations.csv'
UmpiringHistory.to_csv(directory + output_csv)

PossibleVenues = set(UH_Venues)
AllVenuesUmpired = []
for p in PossibleVenues:
    AllVenuesUmpired.append(p)
NumberOfVenues = len(AllVenuesUmpired)

NumGamesUmpiredTotal = len(UH_Venues)

#Create the dataframe for the plotly map
#Start off with creating the columns
venues_umpired = [] #Stores all the venues umpired
suburbs = [] #The suburbs each venue is located in
host_clubs = [] #The host clubs for each venue
num_games = [] #The number of games umpired at each ground after each game umpired
all_lats = [] #The latitude of the venues
all_lons = [] #The longitude of the venues


#Fill in the first row of values
#Each row represents date after one match is umpired
num_games_round = []
match_numbers = []
venues_endof_round = []
match_number = []
for j in range(NumberOfVenues):
    num_games_round.append(0)
    ven = AllVenuesUmpired[j]
    venues_endof_round.append(ven)
    match_number.append(0)
num_games.append(num_games_round)
venues_umpired.append(venues_endof_round)
match_numbers.append(match_number)

#Now fill in the other rows of values
for i in range(NumGamesUmpiredTotal):
    venues_endof_round = []
    num_games_round = []
    match_number = []
    CurrentVenue = UmpiringHistory['Venue'][i]
    for j in range(NumberOfVenues):
        ven = AllVenuesUmpired[j]
        if AllVenuesUmpired[j] == CurrentVenue:
            n = num_games[i][j] + 1
        else:
            n = num_games[i][j]
        match_number.append(int(i+1))
        num_games_round.append(n)
        venues_endof_round.append(ven)
    num_games.append(num_games_round)
    venues_umpired.append(venues_endof_round)
    match_numbers.append(match_number)

#Calculate the number of elements in each array and use this value in
#Numpy to change the arrays into 1-D arrays
num_elements = (NumGamesUmpiredTotal+1)*NumberOfVenues
num_games = np.reshape(num_games, num_elements)
venues_umpired = np.reshape(venues_umpired, num_elements)
match_numbers = np.reshape(match_numbers, num_elements)

#Extract dataframe information (AllVenues) that is useful
HostClubs = AllVenues['HOST_CLUB']
Suburbs = AllVenues['SUBURB']

#Match the host clubs, suburb locations, latitude and longitudes to the venue names
for i in range(len(num_games)):
    for j in range(len(HostClubs)):
        if venues_umpired[i] == MappedVenues[j]:
            host_clubs.append(HostClubs[j])
            suburbs.append(Suburbs[j])
            all_lats.append(Latitudes[j])
            all_lons.append(Longitudes[j])
        
#Create new dataframe        
UmpiringHistoryByVenue_Plotting = pd.DataFrame({'Matches Completed At Time': match_numbers, 'Venue': venues_umpired,
                                                'Number Of Matches Completed At Venue': num_games,
                                                'Host Club': host_clubs, 'Suburb Location Of Venue': suburbs, 'Latitude': all_lats, 'Longitude': all_lons})

#Write new dataframe to csv
output_csv = 'UmpiringByVenueHistory_Plotly.csv'
UmpiringHistoryByVenue_Plotting.to_csv(directory + output_csv)


#Now lets create the map

#Access token to mapbox declared here
token = 'pk.eyJ1IjoiYWFyb25icnVudCIsImEiOiJjbGQ3MmNtbjMxaTJmM3hvZzRnYnZtZnloIn0.xw5Va9Qk5DvxlXa5CEC-zQ'

#Declare data to be displayed when you hover over the point
data_to_display = {}
data_to_display['Matches Completed At Time']=True
data_to_display['Venue']=True
data_to_display['Number Of Matches Completed At Venue']=True
data_to_display['Host Club']=True
data_to_display['Suburb Location Of Venue']=True
data_to_display['Latitude']=False
data_to_display['Longitude']=False



GameNumbers = UmpiringHistoryByVenue_Plotting['Matches Completed At Time'] #Timesteps for the animation

#The size of the dots representing the values is determined by the number of matches umpired there
SizeByGames = UmpiringHistoryByVenue_Plotting['Number Of Matches Completed At Venue']
            
#Plot the stadia on a map
fig = px.scatter_mapbox(UmpiringHistoryByVenue_Plotting, lat="Latitude", lon="Longitude", size=SizeByGames, animation_frame="Matches Completed At Time",
                        animation_group=GameNumbers, hover_name="Venue", hover_data=data_to_display,
                        color_discrete_sequence=["red"], center=dict(lat=-31.95,lon=115.86), zoom=9,
                        title='Aaron Brunt PFL/WAAFL Goal Umpiring Tally By Venue (since 2017)', height=800, width=500)

#Update the map so that the basemap is satellite, which requires your mapbox token
#You will need a mapbox account to do this
fig.update_layout(mapbox_style="satellite", mapbox_accesstoken=token)

#Update the map so that the margins right, top, left and bottom are zero
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#Show the map which will open up a new tab in your default internet browser
fig.show()

#Export to html
file_name = directory + "My_PFL_WAAFL_Umpiring_History.html"
fig.write_html(file_name)

    
        



