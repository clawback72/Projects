import os
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json
import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials

# define the scope and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('/Users/brianm/Documents/keys/pga2024-b6209fa5969d.json', scopes=scope)

# authenticate with Google Sheets API
client = gspread.authorize(creds)

# open the Google Sheets document by its URL
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1B82nFMxUa4ESKt3z2l8LHVPNBGMgp16tiGgOOBkjSZI/edit?gid=0#gid=0')

# access specific worksheet
worksheet = sheet.worksheet('Sheet1')

def main():

    # define picks by unique golfer ID - hard coded due to small number of participants
    participant_selections = {
        'Steve':['47959', '34363', '33204', '28237', '22405'],
        'Amos':['28237', '30925', '47959', '52955', '29725'],
        'Brian':['50525', '46046', '52215', '30911', '26329'],
        'DC':['47959', '48081', '46046', '52955', '24502'],
        'Dad':['28237', '48081', '52955', '50525', '08793']
    }

    # print title and timestamp to console
    print('British Open 2024 Pool Standings:')
    time = datetime.datetime.now()
    print('Timestamp:', time)
    print()

    # get clean dataframe of leaderboard data
    df = get_data(time)

    # print title to google sheets
    worksheet.clear()
    dt_str = time.strftime('%m/%d/%Y %H:%M')
    worksheet.update(range_name='A1', values=[['British Open 2024 Pool']])
    worksheet.update(range_name='A2', values=[['Timestamp: ', dt_str]])
    worksheet.update(range_name='A4', values=[['Current Standings:']])
    worksheet.update(range_name='A5', values=[['Participant', 'Net over/under']])

    # create dictionary containing participants and total scores for team
    participant_scores = {}
    # iterate through each participant and reset variables to zero
    for participant, selections in participant_selections.items():
        total_score = 0
        projected_winnings = 0
        net_score = 0
        # for each participant iterate through each golfer and acccumulate scoring data
        for golfer in selections:
            golfer_data = df[df['PlayerID'] == golfer]
            if not golfer_data.empty:
                points = golfer_data.iloc[0]['Points']
                winnings = golfer_data.iloc[0]['Projected_Winnings']
                score = golfer_data.iloc[0]['Score']
                total_score += points
                projected_winnings += winnings
                if score == 'E':
                    pass
                else:
                    net_score += int(score)
        # add participant score data to dictionary
        participant_scores[participant] = (total_score, projected_winnings, net_score)

    # dictionary complete for all participants, sort by net_score variable
    sorted_scores = dict(sorted(participant_scores.items(), key=lambda item: item[1][2], reverse=False))

    # print to console
    for participant, (score, projected_winnings, net_score) in sorted_scores.items():
        print(f'{participant}: {score} {projected_winnings} {net_score}')
        
    print()

    # write to google sheets
    values = [[participant, int(net_score)] for participant, (score, projected_winnings, net_score) in sorted_scores.items()]
    worksheet.append_rows(values)

    # print pool standings and golfer summaries
    # print header to console and worksheet
    print('Participant Standings Detail:')
    print()
    worksheet.update(range_name='A12', values=[['Participant Standings Detail:']])
    
    # for each participant create a dataframe where each selected golfers data is added
    for sorted_participant,(score, projected_winnings, net_score) in sorted_scores.items():
        # print participant data to console and worksheet
        print(f'{sorted_participant}: {score} {projected_winnings} {net_score}')
        worksheet.append_rows([[sorted_participant, int(net_score) ]])
        for participant, selections in participant_selections.items():
            if sorted_participant == participant:
                participant_df = pd.DataFrame()
                for golfer in selections:
                    golfer_data = df[df['PlayerID'] == golfer]
                    if participant_df.empty:
                        participant_df = golfer_data.copy()
                    else:
                        participant_df = pd.concat([participant_df, golfer_data], ignore_index=True)
                # specify fields to display and sort values by 'Points'
                selected_columns = participant_df[['Name', 'Position', 'Today', 'Thru', 'Score', 'Rounds', 'Total','Points']]
                selected_columns = selected_columns.sort_values(by='Points', ascending=False)
                # 'Points' is useful variable for sorting, but is depricated for pool standings - remove from df for spreadsheet printing
                selected_columns = selected_columns[['Name', 'Score', 'Position', 'Today', 'Thru', 'Rounds', 'Total']]
                # print to console
                print(selected_columns.to_string(justify='center',index=False))
                print()
                # print to spreadsheet
                values = [selected_columns.columns.tolist()] + selected_columns.values.tolist()
                worksheet.append_rows(values)
                # print separator line
                worksheet.append_rows([['_']])
            else:
                pass

def get_data(time):
    '''
    Following block of commented code was used to fetch the JSON from pgatour.com
    Code has been altered to fetch JSON from the /data_backup directory for demonstration purposes.
    Live data on pgatour.com has rolls weekly to the most recent tournament and will not work as expected for The Open Championship 2024.
    '''

    # # URL of the leaderboard page
    # url = 'https://www.pgatour.com/leaderboard'

    # # Send a GET request to the URL
    # response = requests.get(url)

    # # Check if the request was successful (status code 200)
    # if response.status_code == 200:
    #     # parse the HTML content of the page
    #     soup = BeautifulSoup(response.content, 'html.parser')
        
    #     # find the <script> tag containing the JSON data
    #     script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        
    #     # extract the JSON data from the <script> tag
    #     if script_tag:
    #         json_data = json.loads(script_tag.string)
    #         # write JSON file to backup directory if top of the hour
    #         if time.minute == 0:
    #             save_json(json_data)
            
    #         # access the specific part of the JSON data containing the leaderboard information
    #         leaderboard_data = json_data['props']['pageProps']['leaderboard']['players']
                        
    #     else:
    #         print('JSON data not found on the page.')
    #         return()

    # else:
    #     # Print an error message if the request was unsuccessful
    #     print('Failed to retrieve data:', response.status_code)
    #     return()

    # load final tournament data downloaded from pga.com from data_backup directory
    with open('data_backup/backup_20240721170003.json', 'r') as file:
        json_data = json.load(file)
        leaderboard_data = json_data['props']['pageProps']['leaderboard']['players']

    # extract selected data from JSON and create dataframe
    selected_columns = [{'PlayerID': row.get('player', {}).get('id'),
                     'Position': row.get('scoringData', {}).get('position'),
                     'Name': row.get('player', {}).get('displayName'),
                     'Rounds': row.get('scoringData', {}).get('rounds'),
                     'Score': row.get('scoringData', {}).get('total'),
                     'Today': row.get('scoringData', {}).get('score'),
                     'Thru': row.get('scoringData', {}).get('thru'),
                     'Time': row.get('scoringData', {}).get('teeTime'),
                     'backNine': row.get('scoringData', {}).get('backNine'),
                     'Total': row.get('scoringData', {}).get('totalStrokes')}
                    for row in leaderboard_data]
    df = pd.DataFrame(selected_columns)

    # convert rounds field to string so it can be stored in database
    df['Rounds'] = df['Rounds'].apply(lambda x: ','.join(map(str, x)) if x is not None else '')

    # Count number of participants in the tournament
    max_points = df['Name'].notna().sum()

    # Check if Thru is empty - if so, update Thru with starting time
    df.loc[df['Thru'] == '', 'Thru'] = df[df['Thru'] == ''].apply(lambda row: teeTime(row['Time'], row['backNine']), axis=1)

    # create new column PositionNum from Position in dataframe to be cleaned and casted to int
    # strip any leading 'T' values indicating ties in the position column
    df['PositionNum'] = df['Position'].str.replace('^T', '', regex=True)

    # convert the position column to numeric values
    df['PositionNum'] = pd.to_numeric(df['PositionNum'], errors='coerce')

    # convert NaN values for position to 0
    df['PositionNum'] = np.where(df['PositionNum'].notna(), df['PositionNum'], 0)

    # Create and calculate points column - if not a number assign 0
    df['Points'] = np.where(df['PositionNum'].notna(), max_points - df['PositionNum'] + 1, 0)

    # correct points for players with position 0 - ie DQ and MC
    df['Points'] = np.where(df['Points'] > max_points, 0, df['Points'])

    # cast Position and Points as integer from float
    df['PositionNum'] = df['PositionNum'].astype(int)
    df['Points'] = df['Points'].astype(int)

    # Assign rankings to calculate projected winnings
    df['Rank'] = assign_rank(df['PositionNum'])

    # Get Projected Winnings based on Rank
    df['Projected_Winnings'] = df['Rank'].map(get_prize_money)

    # save dataframe to CSV if needed - else comment out
    # df.to_csv('golfers.csv')
    # print df if needed - else comment out
    # print(df)

    # return dataframe
    return df

def assign_rank(position):
    # assign rank brackets by position, grouping ties, for assignment of payout
    rank  = 0
    prev_position = None
    ranks = []
    for pos in position:
        if pos != prev_position:
            rank += 1
        if pos == 0:
            rank = 0
        ranks.append(rank)
        prev_position = pos
    return ranks

def get_prize_money(rank):
    # create dictionary containing prize money estimates using 2023 payouts by rank
    prize_money = {1:3240000, 2:1584000, 3:744000, 4:580500, 5:522000, 6:432000, 7:333000,
                    8:261000, 9:187200, 10:147000, 11:125100, 12:111600, 13:97200, 14:79200,
                     15:66600, 16:57600, 17:50760, 18:46080, 19:44280, 20:43200}
    
    # assign prize money by rank
    if rank > 20:
        return 40000
    return prize_money.get(rank, 0)

def save_json(data):
    backup_directory = '/ukopen/data_backup'

    # make sure directory exists
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    # create unique filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'backup_{timestamp}.json'

    # write data to file
    with open(os.path.join(backup_directory, filename), 'w') as file:
        json.dump(data, file)

def teeTime(time_m, backNine):
    
    # convert time to seconds from milliseconds
    time_s = time_m / 1000

    # get UTC time
    time_utc = datetime.datetime.fromtimestamp(time_s, tz=pytz.UTC)

    # convert to EST
    est = pytz.timezone('US/Eastern')

    time_est = time_utc.astimezone(est)

    # format time as H:M and add an asterisk if player teeing off on back nine
    time_formatted = time_est.strftime('%l:%M %p')

    if backNine:
        time_formatted += '*'

    return time_formatted

if __name__ == "__main__":
    main()